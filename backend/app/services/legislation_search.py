"""
Serviço unificado de busca de legislação

Busca em múltiplas fontes (LexML, Senado, Câmara) e retorna resultados padronizados.
"""
from typing import List, Dict, Any, Optional
from loguru import logger
from datetime import datetime

from app.integrations.legislative_apis import (
    lexml_client,
    camara_client
)
from app.integrations.senado_api import senado_client


class UnifiedLegislationSearch:
    """Serviço unificado para buscar legislação em múltiplas fontes"""

    async def search(
        self,
        query: str,
        limit: int = 5,
        sources: Optional[List[str]] = None,
        year: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Buscar legislação em múltiplas fontes

        Args:
            query: Texto da busca
            limit: Número máximo de resultados por fonte
            sources: Fontes a buscar (None = todas)
                    Opções: 'lexml', 'senado', 'camara'
            year: Ano específico para buscar (opcional)

        Returns:
            Lista de resultados padronizados
        """
        if sources is None:
            sources = ['lexml', 'senado', 'camara']

        # Extrair ano da query se não foi fornecido
        if year is None:
            import re
            year_match = re.search(r'\b(20\d{2})\b', query)
            if year_match:
                year = int(year_match.group(1))
                logger.debug(f"Ano extraído da query: {year}")

        all_results = []

        # Extrair número de lei se mencionado
        import re
        lei_pattern = re.search(
            r'lei\s+(?:n[º°]|n\.?\s*)?\s*(\d+)', query, re.IGNORECASE)
        lei_numero = lei_pattern.group(1) if lei_pattern else None

        # Buscar no LexML
        if 'lexml' in sources:
            try:
                # Se mencionou número específico de lei, tentar buscar diretamente
                if lei_numero and year:
                    # Buscar leis do ano que contenham o número
                    lexml_results = await lexml_client.search_laws(
                        year=year,
                        limit=limit * 2
                    )
                    # Filtrar por número
                    lexml_results = [
                        doc for doc in lexml_results
                        if lei_numero in str(doc.get("title", "")) or
                        lei_numero in str(doc.get("lexml_id", ""))
                    ]
                    # Se não encontrou, fazer busca genérica
                    if not lexml_results:
                        lexml_results = await lexml_client.search_by_keywords(
                            keywords=query,
                            limit=limit
                        )
                else:
                    lexml_results = await lexml_client.search_by_keywords(
                        keywords=query,
                        limit=limit
                    )

                # Se tiver ano, filtrar resultados
                if year:
                    lexml_results = [
                        doc for doc in lexml_results
                        if str(year) in str(doc.get("date", "")) or str(year) in str(doc.get("dc:date", ""))
                    ]
                for doc in lexml_results:
                    all_results.append(self._normalize_lexml_result(doc))
            except Exception as e:
                logger.debug(f"Erro ao buscar no LexML: {str(e)}")

        # Buscar no Senado
        if 'senado' in sources:
            try:
                senado_results = await senado_client.search_legislation(
                    keywords=query,
                    year=year,  # Passar ano se disponível
                    limit=limit
                )
                for doc in senado_results:
                    all_results.append(self._normalize_senado_result(doc))
            except Exception as e:
                logger.debug(f"Erro ao buscar no Senado: {str(e)}")

        # Buscar na Câmara
        if 'camara' in sources:
            try:
                camara_results = await camara_client.search_propositions(
                    keywords=query,
                    year=year,  # Passar ano se disponível
                    limit=limit
                )
                for doc in camara_results:
                    all_results.append(self._normalize_camara_result(doc))
            except Exception as e:
                logger.debug(f"Erro ao buscar na Câmara: {str(e)}")

        # Extrair número de lei se mencionado na query
        import re
        lei_pattern = re.search(
            r'lei\s+(?:n[º°]|n\.?\s*)?\s*(\d+)', query, re.IGNORECASE)
        lei_numero = lei_pattern.group(1) if lei_pattern else None

        # Ordenar por relevância (priorizar resultados que contenham o número da lei)
        def relevance_score(result):
            title_lower = result.get('title', '').lower()
            query_lower = query.lower()
            score = 0

            # Prioridade máxima: título contém o número da lei mencionado
            if lei_numero and lei_numero in str(result.get('number', '')):
                score += 100
            if lei_numero and lei_numero in title_lower:
                score += 50

            # Prioridade alta: título contém palavras da query
            query_words = query_lower.split()
            matching_words = sum(
                1 for word in query_words if word in title_lower and len(word) > 3)
            score += matching_words * 10

            # Prioridade média: query completa no título
            if query_lower in title_lower:
                score += 20

            # Prioridade baixa: data mais recente
            date_str = str(result.get('date', ''))
            if '2025' in date_str:
                score += 5
            elif '2024' in date_str:
                score += 3

            return score

        all_results.sort(key=relevance_score, reverse=True)

        return all_results[:limit * len(sources)]

    def _normalize_lexml_result(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """Normalizar resultado do LexML"""
        return {
            "id": doc.get("urn", ""),
            "title": doc.get("title", doc.get("dc:title", "")),
            "description": doc.get("description", doc.get("dc:description", ""))[:300],
            "type": doc.get("tipo_documento", ""),
            "date": doc.get("date", doc.get("dc:date", "")),
            "source": "LexML",
            "url": doc.get("url", ""),
            "urn": doc.get("urn", "")
        }

    def _normalize_senado_result(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """Normalizar resultado do Senado"""
        return {
            "id": str(doc.get("id", "")),
            "title": doc.get("ementa", ""),
            "description": doc.get("ementa", "")[:300],
            "type": doc.get("tipo", ""),
            "date": doc.get("data_apresentacao", ""),
            "source": "Senado Federal",
            "number": doc.get("numero", ""),
            "year": doc.get("ano", ""),
            "author": doc.get("autor", "")
        }

    def _normalize_camara_result(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """Normalizar resultado da Câmara"""
        return {
            "id": str(doc.get("id", "")),
            "title": doc.get("ementa", ""),
            "description": doc.get("ementa", "")[:300],
            "type": doc.get("siglaTipo", ""),
            "date": doc.get("dataApresentacao", ""),
            "source": "Câmara dos Deputados",
            "number": str(doc.get("numero", "")),
            "year": doc.get("ano", ""),
            "status": doc.get("statusProposicao", {}).get("descricaoSituacao", "")
        }

    async def get_relevant_context(
        self,
        query: str,
        max_results: int = 5
    ) -> str:
        """
        Obter contexto relevante de legislação para uma pergunta

        Args:
            query: Pergunta do usuário
            max_results: Número máximo de resultados

        Returns:
            Texto formatado com contexto relevante
        """
        import re

        # Extrair informações específicas da query
        year_match = re.search(r'\b(20\d{2})\b', query)
        year = int(year_match.group(1)) if year_match else None

        # Extrair número de lei se mencionado (ex: "Lei nº 2025", "Lei 2025", "Lei n° 2025")
        lei_pattern = re.search(
            r'lei\s+(?:n[º°]|n\.?\s*)?\s*(\d+)', query, re.IGNORECASE)
        lei_numero = lei_pattern.group(1) if lei_pattern else None

        # Se mencionou número específico de lei, buscar mais resultados e filtrar
        if lei_numero:
            results = await self.search(query, limit=max_results * 2, year=year)
            # Filtrar resultados que contenham o número da lei no título
            filtered_results = [
                r for r in results
                if lei_numero in str(r.get('title', '')) or lei_numero in str(r.get('number', ''))
            ]
            # Se não encontrou com filtro, usar todos os resultados
            results = filtered_results if filtered_results else results[:max_results]
        else:
            results = await self.search(query, limit=max_results, year=year)

        if not results:
            return ""

        context_parts = []
        for i, result in enumerate(results, 1):
            title = result.get('title', 'Sem título')
            description = result.get('description', '')
            source = result.get('source', '')
            date = result.get('date', '')
            number = result.get('number', '')
            tipo = result.get('type', '')

            context = f"{i}. {title}"
            if tipo:
                context += f" (Tipo: {tipo})"
            if number:
                context += f" (Número: {number})"
            if description and len(description) > 50:
                context += f"\n   Descrição: {description[:200]}..."
            elif description:
                context += f"\n   Descrição: {description}"
            if source:
                context += f"\n   Fonte: {source}"
            if date:
                context += f" | Data: {date}"

            context_parts.append(context)

        return "\n\n".join(context_parts)


# Instância global
unified_search = UnifiedLegislationSearch()
