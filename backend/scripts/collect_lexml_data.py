#!/usr/bin/env python3
"""
Script para coleta completa de dados do LexML
Execute: python scripts/collect_lexml_data.py
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path

# Adicionar diretório do backend ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.core.database import SessionLocal, init_db
from app.services.data_collector import DataCollector
from app.services.pipeline_service import PipelineService
from loguru import logger


class LexMLDataCollector:
    """Coletor de dados do LexML"""
    
    def __init__(self):
        self.db = SessionLocal()
        self.collector = DataCollector(self.db)
        self.pipeline = PipelineService(self.db)
        
    async def collect_all_laws(self, start_year: int = 1988, end_year: int = None):
        """
        Coletar todas as leis federais de um período
        
        Args:
            start_year: Ano inicial (padrão: 1988 - Constituição)
            end_year: Ano final (padrão: ano atual)
        """
        if end_year is None:
            end_year = datetime.now().year
            
        logger.info(f"Iniciando coleta de leis de {start_year} a {end_year}")
        
        total_collected = 0
        total_failed = 0
        
        for year in range(start_year, end_year + 1):
            logger.info(f"Coletando leis de {year}...")
            
            try:
                result = await self.collector.collect_from_lexml(
                    year=year,
                    tipo_documento="Lei",
                    limit=1000  # Máximo por requisição
                )
                
                collected = result.get('collected', 0)
                failed = result.get('failed', 0)
                
                total_collected += collected
                total_failed += failed
                
                logger.info(
                    f"Ano {year}: {collected} leis coletadas, {failed} falhas"
                )
                
                # Aguardar entre anos para não sobrecarregar o servidor
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Erro ao coletar leis de {year}: {str(e)}")
                total_failed += 1
                
        logger.info(
            f"Coleta concluída! Total: {total_collected} leis coletadas, "
            f"{total_failed} falhas"
        )
        
        return {
            'total_collected': total_collected,
            'total_failed': total_failed
        }
    
    async def collect_recent_projects(self, years: int = 5):
        """
        Coletar projetos de lei recentes
        
        Args:
            years: Quantidade de anos para trás (padrão: 5)
        """
        current_year = datetime.now().year
        start_year = current_year - years
        
        logger.info(
            f"Coletando projetos de lei de {start_year} a {current_year}"
        )
        
        total_collected = 0
        total_failed = 0
        
        for year in range(start_year, current_year + 1):
            logger.info(f"Coletando projetos de {year}...")
            
            try:
                result = await self.collector.collect_from_lexml(
                    year=year,
                    tipo_documento="Projeto de Lei",
                    limit=1000
                )
                
                collected = result.get('collected', 0)
                failed = result.get('failed', 0)
                
                total_collected += collected
                total_failed += failed
                
                logger.info(
                    f"Ano {year}: {collected} projetos coletados, {failed} falhas"
                )
                
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Erro ao coletar projetos de {year}: {str(e)}")
                total_failed += 1
                
        logger.info(
            f"Coleta concluída! Total: {total_collected} projetos coletados, "
            f"{total_failed} falhas"
        )
        
        return {
            'total_collected': total_collected,
            'total_failed': total_failed
        }
    
    async def collect_by_theme(self, theme: str, limit: int = 100):
        """
        Coletar leis sobre um tema específico
        
        Args:
            theme: Tema para buscar (ex: "educação", "saúde")
            limit: Limite de resultados
        """
        from app.integrations.legislative_apis import lexml_client
        
        logger.info(f"Buscando leis sobre: {theme}")
        
        try:
            results = await lexml_client.search_by_keywords(
                keywords=theme,
                tipo_documento="Lei",
                limit=limit
            )
            
            logger.info(f"Encontradas {len(results)} leis sobre {theme}")
            
            # Salvar no banco
            collected = 0
            for doc in results:
                try:
                    from app.models.models import Legislation
                    
                    # Verificar se já existe
                    existing = self.db.query(Legislation).filter(
                        Legislation.external_id == doc.get("lexml_id")
                    ).first()
                    
                    if existing:
                        continue
                    
                    legislation = Legislation(
                        external_id=doc.get("lexml_id", ""),
                        source="lexml",
                        type=doc.get("tipo_documento", "Lei"),
                        number=self._extract_number(doc.get("title", "")),
                        year=int(doc.get("date", datetime.now().year)),
                        title=doc.get("title", ""),
                        summary=doc.get("description", ""),
                        author=doc.get("autoridade"),
                        raw_data=doc,
                        created_at=datetime.utcnow()
                    )
                    
                    self.db.add(legislation)
                    collected += 1
                    
                except Exception as e:
                    logger.error(f"Erro ao salvar documento: {str(e)}")
                    
            self.db.commit()
            logger.info(f"{collected} novas leis salvas sobre {theme}")
            
            return {'collected': collected, 'total': len(results)}
            
        except Exception as e:
            logger.error(f"Erro ao buscar leis sobre {theme}: {str(e)}")
            return {'collected': 0, 'total': 0}
    
    async def run_full_pipeline(
        self, 
        year: int = None,
        tipo_documento: str = "Lei",
        limit: int = 50
    ):
        """
        Executar pipeline completo: coleta + processamento + embeddings
        
        Args:
            year: Ano para coletar (padrão: ano atual)
            tipo_documento: Tipo de documento
            limit: Limite de documentos
        """
        if year is None:
            year = datetime.now().year
            
        logger.info(
            f"Executando pipeline completo para {tipo_documento} de {year}"
        )
        
        try:
            result = await self.pipeline.run_full_pipeline(
                source="lexml",
                year=year,
                tipo_documento=tipo_documento,
                limit=limit
            )
            
            logger.info(f"Pipeline concluído! Estatísticas:")
            logger.info(f"  - Documentos coletados: {result.get('collected', 0)}")
            logger.info(f"  - Documentos processados: {result.get('processed', 0)}")
            logger.info(f"  - Chunks criados: {result.get('chunks_created', 0)}")
            logger.info(f"  - Pares QA gerados: {result.get('corpus_pairs', 0)}")
            logger.info(f"  - Embeddings gerados: {result.get('embeddings_generated', 0)}")
            
            return result
            
        except Exception as e:
            logger.error(f"Erro no pipeline: {str(e)}")
            raise
    
    def _extract_number(self, title: str) -> str:
        """Extrair número do título"""
        try:
            if "nº" in title or "Nº" in title:
                parts = title.split("nº") if "nº" in title else title.split("Nº")
                if len(parts) > 1:
                    number_part = parts[1].split("/")[0].strip()
                    return number_part
            return ""
        except:
            return ""
    
    def close(self):
        """Fechar conexão com banco"""
        self.db.close()


async def main():
    """Função principal"""
    # Inicializar banco de dados
    logger.info("Inicializando banco de dados...")
    init_db()
    
    # Criar coletor
    collector_service = LexMLDataCollector()
    
    try:
        # Menu de opções
        print("\n" + "="*60)
        print("COLETOR DE DADOS DO LEXML - VOZ DA LEI")
        print("="*60)
        print("\nEscolha uma opção:")
        print("1. Coletar TODAS as leis federais (1988-2024)")
        print("2. Coletar leis de um ano específico")
        print("3. Coletar projetos de lei recentes (últimos 5 anos)")
        print("4. Coletar leis sobre um tema específico")
        print("5. Executar pipeline completo (coleta + processamento)")
        print("6. Teste rápido (10 leis do ano atual)")
        print("0. Sair")
        print()
        
        option = input("Digite sua opção: ").strip()
        
        if option == "1":
            # Coletar todas as leis
            confirm = input(
                "\nISTO VAI LEVAR MUITO TEMPO! "
                "Deseja coletar leis de 1988 até hoje? (s/n): "
            ).lower()
            
            if confirm == 's':
                await collector_service.collect_all_laws()
            else:
                print("Operação cancelada.")
                
        elif option == "2":
            # Coletar ano específico
            year = int(input("Digite o ano: "))
            tipo = input("Tipo (Lei/Projeto de Lei): ").strip() or "Lei"
            
            result = await collector_service.collector.collect_from_lexml(
                year=year,
                tipo_documento=tipo,
                limit=1000
            )
            
            print(f"\nColetado: {result.get('collected', 0)} documentos")
            print(f"Falhas: {result.get('failed', 0)}")
            
        elif option == "3":
            # Coletar projetos recentes
            await collector_service.collect_recent_projects(years=5)
            
        elif option == "4":
            # Coletar por tema
            theme = input("Digite o tema (ex: educação, saúde): ").strip()
            limit = int(input("Limite de resultados (padrão 100): ") or "100")
            
            await collector_service.collect_by_theme(theme, limit)
            
        elif option == "5":
            # Pipeline completo
            year = input("Ano (Enter para atual): ").strip()
            year = int(year) if year else None
            
            tipo = input("Tipo (Lei/Projeto de Lei): ").strip() or "Lei"
            limit = int(input("Limite (padrão 50): ") or "50")
            
            await collector_service.run_full_pipeline(
                year=year,
                tipo_documento=tipo,
                limit=limit
            )
            
        elif option == "6":
            # Teste rápido
            print("\nExecutando teste rápido...")
            result = await collector_service.collector.collect_from_lexml(
                year=datetime.now().year,
                tipo_documento="Lei",
                limit=10
            )
            
            print(f"\nColetado: {result.get('collected', 0)} documentos")
            print(f"Falhas: {result.get('failed', 0)}")
            
        elif option == "0":
            print("Saindo...")
        else:
            print("Opção inválida!")
            
    except KeyboardInterrupt:
        logger.info("\nOperação cancelada pelo usuário")
    except Exception as e:
        logger.error(f"Erro durante execução: {str(e)}")
        raise
    finally:
        collector_service.close()
        print("\nConexão fechada. Até logo!")


if __name__ == "__main__":
    asyncio.run(main())
