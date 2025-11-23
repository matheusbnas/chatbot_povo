#!/usr/bin/env python3
"""
Script de teste para validar os coletores SEM banco de dados
Execute: python scripts/test_collectors.py
"""

from loguru import logger
from app.integrations.senado_api import senado_client
from app.integrations.legislative_apis import lexml_client
import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Adicionar diretório do backend ao path
sys.path.insert(0, str(Path(__file__).parent.parent))


async def test_lexml_collector():
    """Testar coleta do LexML sem banco de dados"""

    print("\n" + "="*70)
    print("TESTE: COLETOR LEXML (SEM BANCO DE DADOS)")
    print("="*70)

    try:
        # Teste 1: Buscar leis de 2025
        print("\n1. Buscando leis de 2025...")
        leis = await lexml_client.search_laws(year=2025, limit=5)

        if leis:
            print(f"   [OK] Encontradas {len(leis)} leis")
            for i, lei in enumerate(leis[:3], 1):
                print(f"   {i}. {lei.get('title', 'Sem título')[:80]}...")
        else:
            print("   [AVISO] Nenhuma lei encontrada")

        # Teste 2: Buscar projetos de lei
        print("\n2. Buscando projetos de lei de 2025...")
        projetos = await lexml_client.search_projects_of_law(year=2025, limit=3)

        if projetos:
            print(f"   [OK] Encontrados {len(projetos)} projetos")
            for i, projeto in enumerate(projetos[:3], 1):
                print(f"   {i}. {projeto.get('title', 'Sem título')[:80]}...")
        else:
            print("   [AVISO] Nenhum projeto encontrado")

        # Teste 3: Buscar por palavras-chave
        print("\n3. Buscando por palavra-chave 'educação'...")
        resultados = await lexml_client.search_by_keywords(
            keywords="educação",
            tipo_documento="Lei",
            limit=3
        )

        if resultados:
            print(f"   [OK] Encontrados {len(resultados)} documentos")
            for i, doc in enumerate(resultados[:3], 1):
                print(f"   {i}. {doc.get('title', 'Sem título')[:80]}...")
        else:
            print("   [AVISO] Nenhum documento encontrado")

        print("\n[OK] Teste do LexML concluido com sucesso!")
        return True

    except Exception as e:
        print(f"\n[ERRO] Erro no teste do LexML: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_senado_collector():
    """Testar coleta do Senado sem banco de dados"""

    print("\n" + "="*70)
    print("TESTE: COLETOR SENADO (SEM BANCO DE DADOS)")
    print("="*70)

    try:
        # Teste 1: Listar normas (leis)
        print("\n1. Listando normas (leis) de 2024...")
        resultado = await senado_client.listar_normas(ano=2024, quantidade=5)

        normas = resultado.get("normas", [])
        if normas:
            print(f"   [OK] Encontradas {len(normas)} normas")
            for i, norma in enumerate(normas[:3], 1):
                numero = norma.get("numero", "N/A")
                tipo = norma.get("tipo", {})
                tipo_sigla = tipo.get(
                    "sigla", "N/A") if isinstance(tipo, dict) else "N/A"
                ementa = norma.get("ementa", "Sem ementa")
                print(f"   {i}. {tipo_sigla} {numero}: {ementa[:60]}...")
        else:
            print(
                "   [AVISO] Nenhuma norma encontrada (pode ser problema de endpoint)")

        # Teste 2: Listar matérias (projetos)
        print("\n2. Listando matérias (projetos) de 2024...")
        resultado = await senado_client.listar_materias(ano=2024, quantidade=5)

        materias = resultado.get("materias", [])
        if materias:
            print(f"   [OK] Encontradas {len(materias)} materias")
            for i, materia in enumerate(materias[:3], 1):
                numero = materia.get("numero", "N/A")
                sigla = materia.get("siglaTipo", "N/A")
                ementa = materia.get("ementa", "Sem ementa")
                print(f"   {i}. {sigla} {numero}: {ementa[:60]}...")
        else:
            print(
                "   [AVISO] Nenhuma materia encontrada (pode ser problema de endpoint)")

        # Teste 3: Buscar por palavra-chave
        print("\n3. Buscando por palavra-chave 'educação'...")
        resultados = await senado_client.buscar_por_palavra_chave(
            palavra_chave="educação",
            tipo="materia",
            quantidade=3
        )

        if resultados:
            print(f"   [OK] Encontradas {len(resultados)} materias")
            for i, materia in enumerate(resultados[:3], 1):
                numero = materia.get("numero", "N/A")
                ementa = materia.get("ementa", "Sem ementa")
                print(f"   {i}. {numero}: {ementa[:60]}...")
        else:
            print("   [AVISO] Nenhuma materia encontrada")

        # Teste 4: Métodos de compatibilidade
        print("\n4. Testando metodos de compatibilidade...")
        resultados = await senado_client.search_legislation(
            keywords="educacao",
            year=2024,
            limit=3
        )

        if resultados:
            print(
                f"   [OK] Metodo search_legislation funcionando: {len(resultados)} resultados")
        else:
            print("   [AVISO] Metodo search_legislation retornou vazio")

        print("\n[OK] Teste do Senado concluido!")
        return True

    except Exception as e:
        print(f"\n[ERRO] Erro no teste do Senado: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Função principal"""

    print("\n" + "="*70)
    print("TESTE DE COLETORES - SEM BANCO DE DADOS")
    print("="*70)
    print("\nEste script testa as APIs sem precisar de banco de dados.")
    print("Ele apenas valida se as APIs estão respondendo corretamente.\n")

    resultados = {
        "lexml": False,
        "senado": False
    }

    # Testar LexML
    resultados["lexml"] = await test_lexml_collector()

    # Aguardar um pouco entre testes
    await asyncio.sleep(2)

    # Testar Senado
    resultados["senado"] = await test_senado_collector()

    # Resumo
    print("\n" + "="*70)
    print("RESUMO DOS TESTES")
    print("="*70)
    print(f"LexML:  {'[OK]' if resultados['lexml'] else '[ERRO]'}")
    print(f"Senado: {'[OK]' if resultados['senado'] else '[ERRO]'}")
    print("="*70)

    if all(resultados.values()):
        print("\n[SUCESSO] Todos os testes passaram! As APIs estao funcionando.")
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
