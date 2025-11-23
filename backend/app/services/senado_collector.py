"""
Coletor de dados do Senado Federal
"""
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
from loguru import logger
from sqlalchemy.orm import Session

from app.integrations.senado_api import senado_client
from app.models.models import Legislation, DataCollectionJob


class SenadoDataCollector:
    """Coletor de dados do Senado Federal"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.client = senado_client
    
    async def coletar_normas(
        self,
        ano_inicio: int = 1988,
        ano_fim: Optional[int] = None,
        tipo: Optional[str] = None,
        job_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Coletar normas (leis) do Senado
        
        Args:
            ano_inicio: Ano inicial
            ano_fim: Ano final (None = ano atual)
            tipo: Tipo de norma (LEI, DEC, MPV, etc)
            job_id: ID do job de coleta
        """
        if ano_fim is None:
            ano_fim = datetime.now().year
        
        logger.info(f"Coletando normas do Senado ({ano_inicio}-{ano_fim})")
        
        total_coletado = 0
        total_falhas = 0
        
        for ano in range(ano_inicio, ano_fim + 1):
            logger.info(f"Processando ano {ano}...")
            
            try:
                # Listar normas do ano
                resultado = await self.client.listar_normas(
                    ano=ano,
                    tipo=tipo,
                    quantidade=1000
                )
                
                normas = resultado.get("normas", [])
                logger.info(f"  Encontradas {len(normas)} normas")
                
                for norma in normas:
                    try:
                        # Verificar se já existe
                        codigo = norma.get("codigo")
                        if not codigo:
                            continue
                        
                        external_id = f"senado_{codigo}"
                        
                        existing = self.db.query(Legislation).filter(
                            Legislation.external_id == external_id
                        ).first()
                        
                        if existing:
                            continue
                        
                        # Obter detalhes completos
                        detalhes = await self.client.detalhe_norma(codigo)
                        
                        # Tentar obter texto completo
                        texto_completo = await self.client.texto_norma(codigo)
                        
                        # Extrair dados
                        numero = norma.get("numero", "")
                        tipo_norma = norma.get("tipo", {})
                        tipo_sigla = tipo_norma.get("sigla", "LEI") if isinstance(tipo_norma, dict) else "LEI"
                        
                        titulo = norma.get("ementa", "")
                        data_norma = norma.get("data")
                        ano_norma = int(data_norma[:4]) if data_norma else ano
                        
                        # Criar registro
                        legislation = Legislation(
                            external_id=external_id,
                            source="senado",
                            type=tipo_sigla,
                            number=str(numero),
                            year=ano_norma,
                            title=titulo,
                            summary=norma.get("ementa", ""),
                            full_text=texto_completo,
                            author="Senado Federal",
                            raw_data={
                                "norma": norma,
                                "detalhes": detalhes
                            },
                            created_at=datetime.utcnow()
                        )
                        
                        self.db.add(legislation)
                        total_coletado += 1
                        
                        # Commit a cada 100 registros
                        if total_coletado % 100 == 0:
                            self.db.commit()
                            logger.info(f"  Coletadas {total_coletado} normas até agora")
                        
                    except Exception as e:
                        logger.error(f"Erro ao processar norma {codigo}: {str(e)}")
                        total_falhas += 1
                
                # Commit final do ano
                self.db.commit()
                
                # Atualizar job se fornecido
                if job_id:
                    job = self.db.query(DataCollectionJob).filter_by(id=job_id).first()
                    if job:
                        job.processed_items = total_coletado
                        self.db.commit()
                
                # Delay entre anos
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Erro ao processar ano {ano}: {str(e)}")
                total_falhas += 1
        
        logger.info(
            f"Coleta concluída: {total_coletado} normas coletadas, "
            f"{total_falhas} falhas"
        )
        
        return {
            "collected": total_coletado,
            "failed": total_falhas,
            "years": ano_fim - ano_inicio + 1
        }
    
    async def coletar_materias(
        self,
        ano_inicio: int = 2020,
        ano_fim: Optional[int] = None,
        sigla: Optional[str] = None,  # PLS, PLC, PEC, etc
        tramitando: bool = True,
        job_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Coletar matérias (projetos de lei) do Senado
        
        Args:
            ano_inicio: Ano inicial
            ano_fim: Ano final (None = ano atual)
            sigla: Sigla da matéria (PLS, PEC, etc)
            tramitando: Apenas em tramitação
            job_id: ID do job de coleta
        """
        if ano_fim is None:
            ano_fim = datetime.now().year
        
        logger.info(f"Coletando matérias do Senado ({ano_inicio}-{ano_fim})")
        
        total_coletado = 0
        total_falhas = 0
        
        for ano in range(ano_inicio, ano_fim + 1):
            logger.info(f"Processando ano {ano}...")
            
            try:
                # Listar matérias do ano
                resultado = await self.client.listar_materias(
                    ano=ano,
                    sigla=sigla,
                    tramitando=tramitando,
                    quantidade=1000
                )
                
                materias = resultado.get("materias", [])
                logger.info(f"  Encontradas {len(materias)} matérias")
                
                for materia in materias:
                    try:
                        # Verificar se já existe
                        codigo = materia.get("codigo")
                        if not codigo:
                            continue
                        
                        external_id = f"senado_mat_{codigo}"
                        
                        existing = self.db.query(Legislation).filter(
                            Legislation.external_id == external_id
                        ).first()
                        
                        if existing:
                            continue
                        
                        # Obter detalhes completos
                        detalhes = await self.client.detalhe_materia(codigo)
                        
                        # Tentar obter texto completo
                        texto_completo = await self.client.texto_materia(codigo)
                        
                        # Obter autores
                        autores = await self.client.autores_materia(codigo)
                        autor_principal = autores[0].get("nome") if autores else "Senado Federal"
                        
                        # Extrair dados
                        numero = materia.get("numero", "")
                        sigla_materia = materia.get("sigla", "PLS")
                        
                        titulo = materia.get("ementa", "")
                        ano_materia = materia.get("ano", ano)
                        
                        # Status de tramitação
                        situacao = materia.get("situacao", {})
                        status = situacao.get("descricao") if isinstance(situacao, dict) else "Em tramitação"
                        
                        # Criar registro
                        legislation = Legislation(
                            external_id=external_id,
                            source="senado",
                            type=sigla_materia,
                            number=str(numero),
                            year=int(ano_materia),
                            title=titulo,
                            summary=materia.get("ementa", ""),
                            full_text=texto_completo,
                            status=status,
                            author=autor_principal,
                            raw_data={
                                "materia": materia,
                                "detalhes": detalhes,
                                "autores": autores
                            },
                            created_at=datetime.utcnow()
                        )
                        
                        self.db.add(legislation)
                        total_coletado += 1
                        
                        # Commit a cada 50 registros
                        if total_coletado % 50 == 0:
                            self.db.commit()
                            logger.info(f"  Coletadas {total_coletado} matérias até agora")
                        
                    except Exception as e:
                        logger.error(f"Erro ao processar matéria {codigo}: {str(e)}")
                        total_falhas += 1
                
                # Commit final do ano
                self.db.commit()
                
                # Atualizar job se fornecido
                if job_id:
                    job = self.db.query(DataCollectionJob).filter_by(id=job_id).first()
                    if job:
                        job.processed_items = total_coletado
                        self.db.commit()
                
                # Delay entre anos
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Erro ao processar ano {ano}: {str(e)}")
                total_falhas += 1
        
        logger.info(
            f"Coleta concluída: {total_coletado} matérias coletadas, "
            f"{total_falhas} falhas"
        )
        
        return {
            "collected": total_coletado,
            "failed": total_falhas,
            "years": ano_fim - ano_inicio + 1
        }
    
    async def coletar_por_tema(
        self,
        palavra_chave: str,
        tipo: str = "materia",  # materia ou norma
        ano: Optional[int] = None,
        limite: int = 100
    ) -> Dict[str, Any]:
        """
        Coletar documentos por palavra-chave
        """
        logger.info(f"Buscando {tipo}s sobre: {palavra_chave}")
        
        try:
            resultados = await self.client.buscar_por_palavra_chave(
                palavra_chave=palavra_chave,
                tipo=tipo,
                ano=ano,
                quantidade=limite
            )
            
            total_coletado = 0
            
            for doc in resultados:
                try:
                    codigo = doc.get("codigo")
                    if not codigo:
                        continue
                    
                    # Determinar external_id
                    if tipo == "norma":
                        external_id = f"senado_{codigo}"
                    else:
                        external_id = f"senado_mat_{codigo}"
                    
                    # Verificar se já existe
                    existing = self.db.query(Legislation).filter(
                        Legislation.external_id == external_id
                    ).first()
                    
                    if existing:
                        continue
                    
                    # Processar e salvar
                    if tipo == "norma":
                        texto = await self.client.texto_norma(codigo)
                        tipo_doc = doc.get("tipo", {}).get("sigla", "LEI")
                    else:
                        texto = await self.client.texto_materia(codigo)
                        tipo_doc = doc.get("sigla", "PLS")
                    
                    legislation = Legislation(
                        external_id=external_id,
                        source="senado",
                        type=tipo_doc,
                        number=str(doc.get("numero", "")),
                        year=int(doc.get("ano", datetime.now().year)),
                        title=doc.get("ementa", ""),
                        summary=doc.get("ementa", ""),
                        full_text=texto,
                        author="Senado Federal",
                        raw_data=doc,
                        created_at=datetime.utcnow()
                    )
                    
                    self.db.add(legislation)
                    total_coletado += 1
                    
                except Exception as e:
                    logger.error(f"Erro ao processar documento: {str(e)}")
            
            self.db.commit()
            
            logger.info(f"{total_coletado} novos documentos sobre '{palavra_chave}'")
            
            return {
                "collected": total_coletado,
                "total": len(resultados),
                "keyword": palavra_chave
            }
            
        except Exception as e:
            logger.error(f"Erro na busca por tema: {str(e)}")
            return {"collected": 0, "total": 0}
    
    async def estatisticas(self) -> Dict[str, Any]:
        """
        Obter estatísticas dos dados coletados do Senado
        """
        try:
            from sqlalchemy import func
            
            # Total de documentos
            total = self.db.query(Legislation).filter(
                Legislation.source == "senado"
            ).count()
            
            # Por tipo
            by_type = self.db.query(
                Legislation.type,
                func.count(Legislation.id)
            ).filter(
                Legislation.source == "senado"
            ).group_by(Legislation.type).all()
            
            # Por ano
            by_year = self.db.query(
                Legislation.year,
                func.count(Legislation.id)
            ).filter(
                Legislation.source == "senado"
            ).group_by(Legislation.year).all()
            
            return {
                "total": total,
                "by_type": {tipo: count for tipo, count in by_type},
                "by_year": {ano: count for ano, count in sorted(by_year, reverse=True)[:10]}
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {str(e)}")
            return {"total": 0}
