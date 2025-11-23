#!/usr/bin/env python3
"""
Teste dos endpoints de Legislação da API do Senado
Execute: python backend/tests/test_legislacao_api.py
"""

from loguru import logger
from app.integrations.senado_api import senado_client
import asyncio
import sys
from pathlib import Path

# Adicionar diretório do backend ao path
sys.path.insert(0, str(Path(__file__).parent.parent))


async def test_legislacao_tipos():
    """Testar obtenção de tipos de norma e publicação"""

    print("\n" + "="*70)
    print("TESTE: TIPOS DE LEGISLAÇÃO")
    print("="*70)

    try:
        # Teste 1: Tipos de Norma
        print("\n1. Obtendo tipos de norma...")
        tipos_norma = await senado_client.legislacao_tipos_norma()
        if tipos_norma:
            print(f"   [OK] Encontrados {len(tipos_norma)} tipos de norma")
            for i, tipo in enumerate(tipos_norma[:5], 1):
                print(f"   {i}. {tipo}")
        else:
            print("   [AVISO] Nenhum tipo de norma encontrado")

        # Teste 2: Tipos de Publicação
        print("\n2. Obtendo tipos de publicação...")
        tipos_publicacao = await senado_client.legislacao_tipos_publicacao()
        if tipos_publicacao:
            print(
                f"   [OK] Encontrados {len(tipos_publicacao)} tipos de publicação")
            for i, tipo in enumerate(tipos_publicacao[:5], 1):
                print(f"   {i}. {tipo}")
        else:
            print("   [AVISO] Nenhum tipo de publicação encontrado")

        # Teste 3: Classes de Legislação
        print("\n3. Obtendo classes de legislação...")
        classes = await senado_client.legislacao_classes()
        if classes:
            print(f"   [OK] Encontradas {len(classes)} classes")
            for i, classe in enumerate(classes[:5], 1):
                print(f"   {i}. {classe}")
        else:
            print("   [AVISO] Nenhuma classe encontrada")

        return True

    except Exception as e:
        print(f"\n[ERRO] Erro nos testes de tipos: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_legislacao_lista():
    """Testar pesquisa de normas federais"""

    print("\n" + "="*70)
    print("TESTE: PESQUISA DE LEGISLAÇÃO")
    print("="*70)

    try:
        # Teste 1: Buscar leis de 2024
        print("\n1. Buscando legislação de 2024...")
        resultado = await senado_client.legislacao_lista(ano=2024, quantidade=5)
        if resultado:
            print(f"   [OK] Resultado obtido")
            # A estrutura pode variar, vamos ver o que veio
            if isinstance(resultado, dict):
                print(f"   Chaves disponíveis: {list(resultado.keys())[:10]}")
                # Tentar encontrar lista de normas
                for key in ['normas', 'dados', 'lista', 'resultado']:
                    if key in resultado:
                        items = resultado[key]
                        if isinstance(items, list) and items:
                            print(f"   Encontradas {len(items)} normas")
                            break
            else:
                print(f"   Tipo de resultado: {type(resultado)}")
        else:
            print("   [AVISO] Nenhum resultado encontrado")

        # Teste 2: Buscar por tipo
        print("\n2. Buscando leis (tipo LEI)...")
        resultado = await senado_client.legislacao_lista(tipo="LEI", quantidade=3)
        if resultado:
            print(f"   [OK] Resultado obtido")
        else:
            print("   [AVISO] Nenhum resultado encontrado")

        return True

    except Exception as e:
        print(f"\n[ERRO] Erro na pesquisa de legislação: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_legislacao_termos():
    """Testar pesquisa de termos"""

    print("\n" + "="*70)
    print("TESTE: PESQUISA DE TERMOS")
    print("="*70)

    try:
        print("\n1. Pesquisando termos do catálogo...")
        termos = await senado_client.legislacao_termos()
        if termos:
            print(f"   [OK] Encontrados {len(termos)} termos")
            for i, termo in enumerate(termos[:5], 1):
                print(f"   {i}. {termo}")
        else:
            print("   [AVISO] Nenhum termo encontrado")

        return True

    except Exception as e:
        print(f"\n[ERRO] Erro na pesquisa de termos: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_legislacao_por_identificacao():
    """Testar busca por identificação (tipo/numero/ano)"""

    print("\n" + "="*70)
    print("TESTE: LEGISLAÇÃO POR IDENTIFICAÇÃO")
    print("="*70)

    try:
        # Exemplo: Lei 13.979 de 2020 (sobre COVID-19)
        print("\n1. Buscando Lei 13.979/2020...")
        resultado = await senado_client.legislacao_por_identificacao(
            tipo="LEI",
            numdata="13979",
            anoseq="2020"
        )
        if resultado:
            print(f"   [OK] Resultado obtido")
            if isinstance(resultado, dict):
                print(f"   Chaves disponíveis: {list(resultado.keys())[:10]}")
        else:
            print("   [AVISO] Nenhum resultado encontrado")

        return True

    except Exception as e:
        print(f"\n[ERRO] Erro na busca por identificação: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Função principal"""

    print("\n" + "="*70)
    print("TESTE DOS ENDPOINTS DE LEGISLAÇÃO - API DO SENADO")
    print("="*70)
    print("\nTestando os novos endpoints de legislação da API oficial.")
    print("Documentação: https://legis.senado.leg.br/dadosabertos/v3/api-docs\n")

    resultados = {
        "tipos": False,
        "lista": False,
        "termos": False,
        "identificacao": False
    }

    # Testar tipos
    resultados["tipos"] = await test_legislacao_tipos()
    await asyncio.sleep(1)  # Rate limiting

    # Testar lista
    resultados["lista"] = await test_legislacao_lista()
    await asyncio.sleep(1)

    # Testar termos
    resultados["termos"] = await test_legislacao_termos()
    await asyncio.sleep(1)

    # Testar identificação
    resultados["identificacao"] = await test_legislacao_por_identificacao()

    # Resumo
    print("\n" + "="*70)
    print("RESUMO DOS TESTES")
    print("="*70)
    print(
        f"Tipos de Legislação:  {'[OK]' if resultados['tipos'] else '[ERRO]'}")
    print(
        f"Pesquisa de Legislação: {'[OK]' if resultados['lista'] else '[ERRO]'}")
    print(
        f"Pesquisa de Termos: {'[OK]' if resultados['termos'] else '[ERRO]'}")
    print(
        f"Busca por Identificação: {'[OK]' if resultados['identificacao'] else '[ERRO]'}")
    print("="*70)

    if all(resultados.values()):
        print("\n[SUCESSO] Todos os testes passaram!")
    else:
        print("\n[AVISO] Alguns testes falharam. Verifique os erros acima.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nOperação cancelada pelo usuário.")
    except Exception as e:
        print(f"\n\nErro fatal: {str(e)}")
        import traceback
        traceback.print_exc()
