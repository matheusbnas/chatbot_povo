#!/usr/bin/env python3
"""
Script para coleta de dados do Senado Federal
Execute: python scripts/collect_senado_data.py
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path

# Adicionar diretório do backend ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.core.database import SessionLocal, init_db
from app.services.senado_collector import SenadoDataCollector
from loguru import logger


async def main():
    """Função principal"""
    
    # Inicializar banco de dados
    logger.info("Inicializando banco de dados...")
    init_db()
    
    # Criar sessão
    db = SessionLocal()
    collector = SenadoDataCollector(db)
    
    try:
        print("\n" + "="*70)
        print("COLETOR DE DADOS DO SENADO FEDERAL - VOZ DA LEI")
        print("="*70)
        print("\nEscolha uma opção:")
        print("1. Coletar TODAS as normas (leis) - 1988 até hoje")
        print("2. Coletar normas de um período específico")
        print("3. Coletar matérias (projetos de lei) recentes")
        print("4. Coletar matérias por período")
        print("5. Buscar por palavra-chave")
        print("6. Estatísticas dos dados coletados")
        print("7. Teste rápido (normas de 2024)")
        print("0. Sair")
        print()
        
        option = input("Digite sua opção: ").strip()
        
        if option == "1":
            # Coletar todas as normas
            confirm = input(
                "\nISTO VAI LEVAR VÁRIAS HORAS! "
                "Coletar todas as normas de 1988 até hoje? (s/n): "
            ).lower()
            
            if confirm == 's':
                result = await collector.coletar_normas(
                    ano_inicio=1988,
                    ano_fim=datetime.now().year
                )
                
                print(f"\nColeta concluída!")
                print(f"  Coletadas: {result['collected']}")
                print(f"  Falhas: {result['failed']}")
                print(f"  Anos processados: {result['years']}")
            else:
                print("Operação cancelada.")
        
        elif option == "2":
            # Coletar normas por período
            ano_inicio = int(input("Ano inicial: "))
            ano_fim = int(input("Ano final: "))
            
            tipo = input("Tipo (Enter para todos, ou LEI, DEC, MPV, etc): ").strip()
            tipo = tipo.upper() if tipo else None
            
            result = await collector.coletar_normas(
                ano_inicio=ano_inicio,
                ano_fim=ano_fim,
                tipo=tipo
            )
            
            print(f"\nColeta concluída!")
            print(f"  Coletadas: {result['collected']}")
            print(f"  Falhas: {result['failed']}")
        
        elif option == "3":
            # Coletar matérias recentes
            anos = int(input("Quantos anos atrás? (padrão 3): ") or "3")
            
            sigla = input("Sigla (PLS, PEC, PLC ou Enter para todos): ").strip()
            sigla = sigla.upper() if sigla else None
            
            ano_fim = datetime.now().year
            ano_inicio = ano_fim - anos
            
            result = await collector.coletar_materias(
                ano_inicio=ano_inicio,
                ano_fim=ano_fim,
                sigla=sigla,
                tramitando=True
            )
            
            print(f"\nColeta concluída!")
            print(f"  Coletadas: {result['collected']}")
            print(f"  Falhas: {result['failed']}")
        
        elif option == "4":
            # Coletar matérias por período
            ano_inicio = int(input("Ano inicial: "))
            ano_fim = int(input("Ano final: "))
            
            sigla = input("Sigla (PLS, PEC, PLC ou Enter para todos): ").strip()
            sigla = sigla.upper() if sigla else None
            
            tramitando = input("Apenas em tramitação? (s/n): ").lower() == 's'
            
            result = await collector.coletar_materias(
                ano_inicio=ano_inicio,
                ano_fim=ano_fim,
                sigla=sigla,
                tramitando=tramitando
            )
            
            print(f"\nColeta concluída!")
            print(f"  Coletadas: {result['collected']}")
            print(f"  Falhas: {result['failed']}")
        
        elif option == "5":
            # Buscar por palavra-chave
            palavra = input("Palavra-chave: ").strip()
            tipo = input("Tipo (norma/materia): ").strip() or "materia"
            
            ano_str = input("Ano (Enter para todos): ").strip()
            ano = int(ano_str) if ano_str else None
            
            limite = int(input("Limite (padrão 100): ") or "100")
            
            result = await collector.coletar_por_tema(
                palavra_chave=palavra,
                tipo=tipo,
                ano=ano,
                limite=limite
            )
            
            print(f"\nColeta concluída!")
            print(f"  Encontradas: {result['total']}")
            print(f"  Novas coletadas: {result['collected']}")
        
        elif option == "6":
            # Estatísticas
            stats = await collector.estatisticas()
            
            print(f"\nEstatísticas do Senado Federal:")
            print(f"  Total de documentos: {stats['total']}")
            
            print(f"\n  Por tipo:")
            for tipo, count in stats.get('by_type', {}).items():
                print(f"    {tipo}: {count}")
            
            print(f"\n  Por ano (últimos 10):")
            for ano, count in list(stats.get('by_year', {}).items())[:10]:
                print(f"    {ano}: {count}")
        
        elif option == "7":
            # Teste rápido
            print("\nExecutando teste rápido (normas de 2024)...")
            
            result = await collector.coletar_normas(
                ano_inicio=2024,
                ano_fim=2024,
                tipo=None
            )
            
            print(f"\nTeste concluído!")
            print(f"  Coletadas: {result['collected']}")
            print(f"  Falhas: {result['failed']}")
        
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
        db.close()
        print("\nConexão fechada. Até logo!")


if __name__ == "__main__":
    asyncio.run(main())
