from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from loguru import logger

from app.schemas.schemas import SearchRequest, SearchResponse, LegislationSimplified
from app.integrations.legislative_apis import camara_client, lexml_client

router = APIRouter()


@router.post("/", response_model=SearchResponse)
async def search_legislation(request: SearchRequest):
    """
    Buscar legislação por palavras-chave

    Busca em múltiplas fontes (Câmara, Senado, municípios).
    """
    try:
        year_filter = request.filters.get("year") if request.filters else None

        # Se houver filtro de ano antigo (antes de 2000) ou não houver termo de busca, usar LexML
        # O LexML tem melhor suporte para anos antigos
        use_lexml = False
        if year_filter and year_filter < 2000:
            use_lexml = True  # Anos antigos: usar LexML
        elif not request.query or request.query.strip() == "" or request.query.strip() == "*":
            if year_filter:
                use_lexml = True  # Sem termo mas com ano: usar LexML

        if use_lexml and year_filter:
            # Buscar no LexML por ano
            try:
                lexml_results = await lexml_client.search_by_keywords(
                    keywords="lei",  # Termo genérico
                    year=year_filter,
                    limit=request.page_size
                )

                # Converter resultados do LexML para formato padronizado
                results = []
                for doc in lexml_results:
                    urn = doc.get("urn", "")
                    doc_id = doc.get("lexml_id")
                    if not doc_id:
                        doc_id = abs(hash(urn)) % (10 ** 10) if urn else 0

                    # Extrair número e ano
                    title = doc.get("title", "")
                    number = ""
                    year = doc.get("date", year_filter)

                    if "nº" in title or "Nº" in title:
                        parts = title.split(
                            "nº") if "nº" in title else title.split("Nº")
                        if len(parts) > 1:
                            number_part = parts[1].split("/")[0].strip()
                            number = number_part

                    # Determinar status
                    status = None
                    dc_type = doc.get("dc_type", "").lower(
                    ) if doc.get("dc_type") else ""
                    if "aprovado" in dc_type or "aprovada" in dc_type:
                        status = "Aprovado"
                    elif "rejeitado" in dc_type or "rejeitada" in dc_type:
                        status = "Rejeitado"
                    elif "arquivado" in dc_type or "arquivada" in dc_type:
                        status = "Arquivado"
                    else:
                        status = "Em tramitação"

                    # Aplicar filtro de status se especificado
                    status_filter = request.filters.get(
                        "status") if request.filters else None
                    if status_filter:
                        if status and status_filter.lower() not in status.lower():
                            continue

                    results.append(LegislationSimplified(
                        id=int(doc_id) if doc_id else abs(
                            hash(urn)) % (10 ** 10),
                        type=doc.get("tipo_documento", "Documento"),
                        number=number or "N/A",
                        year=int(year) if year else year_filter,
                        title=title,
                        summary=doc.get("description", "")[
                            :200] + "..." if doc.get("description") else None,
                        status=status,
                        author=doc.get("autoridade"),
                        presentation_date=None,
                        tags=None,
                        urn=urn,
                        identifier=doc.get("lexml_id") or urn
                    ))

                if results:
                    return SearchResponse(
                        total=len(results),
                        page=request.page,
                        page_size=request.page_size,
                        results=results
                    )
            except Exception as e:
                logger.warning(
                    f"Erro ao buscar no LexML por ano, tentando Câmara: {str(e)}")

        # Buscar na Câmara dos Deputados (padrão ou fallback)
        propositions = await camara_client.search_propositions(
            keywords=request.query if request.query and request.query.strip() != "*" else None,
            year=request.filters.get("year") if request.filters else None,
            limit=request.page_size
        )

        # Converter para formato padronizado
        results = []
        status_filter = request.filters.get(
            "status") if request.filters else None

        for prop in propositions:
            prop_id = prop.get("id")
            # Construir URL da Câmara
            camara_url = None
            if prop_id:
                camara_url = f"https://www.camara.leg.br/proposicoesWeb/fichadetramitacao?idProposicao={prop_id}"

            # Extrair status da proposição
            # A API da Câmara pode retornar status em diferentes campos
            status = None
            situacao = prop.get("statusProposicao") or prop.get(
                "situacao") or prop.get("status")
            situacao_lower = ""

            if situacao:
                # Normalizar status para corresponder aos filtros
                situacao_lower = str(situacao).lower()
                if "aprovado" in situacao_lower or "aprovada" in situacao_lower:
                    status = "Aprovado"
                elif "rejeitado" in situacao_lower or "rejeitada" in situacao_lower:
                    status = "Rejeitado"
                elif "arquivado" in situacao_lower or "arquivada" in situacao_lower:
                    status = "Arquivado"
                elif "tramit" in situacao_lower or "em análise" in situacao_lower:
                    status = "Em tramitação"
                else:
                    status = situacao  # Usar o status original se não corresponder
            else:
                # Se não tiver status, assumir "Em tramitação" por padrão
                status = "Em tramitação"

            # Aplicar filtro de status se especificado
            if status_filter:
                status_lower = status.lower() if status else ""
                filter_lower = status_filter.lower()
                # Verificar se o status corresponde ao filtro
                if filter_lower not in status_lower and (not situacao_lower or filter_lower not in situacao_lower):
                    continue  # Pular se não corresponder ao filtro

            results.append(LegislationSimplified(
                id=prop_id,
                type=prop.get("siglaTipo", ""),
                number=str(prop.get("numero", "")),
                year=prop.get("ano", 0),
                title=prop.get("ementa", ""),
                summary=prop.get("ementa", "")[
                    :200] + "..." if prop.get("ementa") else None,
                status=status,
                author=None,
                presentation_date=None,
                tags=None,
                identifier=camara_url  # Usar identifier para armazenar URL da Câmara
            ))

        return SearchResponse(
            total=len(results),
            page=request.page,
            page_size=request.page_size,
            results=results
        )

    except Exception as e:
        logger.error(f"Erro na busca: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/autocomplete")
async def autocomplete(q: str = Query(..., min_length=2)):
    """
    Autocompletar termos de busca

    Args:
        q: Termo parcial para autocompletar
    """
    # Sugestões baseadas em termos comuns
    suggestions = [
        "educação",
        "saúde",
        "transporte",
        "meio ambiente",
        "trabalho",
        "previdência",
        "impostos",
        "segurança",
        "cultura",
        "esporte"
    ]

    filtered = [s for s in suggestions if q.lower() in s.lower()]

    return {"suggestions": filtered[:5]}


@router.get("/filters")
async def get_available_filters():
    """
    Obter filtros disponíveis para busca
    """
    from datetime import datetime
    current_year = datetime.now().year
    # Incluir anos desde 1988 (Constituição) até o ano atual
    years = list(range(1988, current_year + 1))
    years.reverse()  # Mais recentes primeiro

    return {
        "types": ["PL", "PEC", "PLP", "PLV"],
        "years": years,
        "sources": ["camara", "senado", "municipal"],
        "status": [
            "Em tramitação",
            "Aprovado",
            "Rejeitado",
            "Arquivado"
        ]
    }
