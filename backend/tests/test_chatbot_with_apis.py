#!/usr/bin/env python3
"""
Teste do chatbot com dados reais das APIs
Execute: python backend/tests/test_chatbot_with_apis.py
"""

from loguru import logger
from app.ai.simplification import chat_service
from app.services.legislation_search import unified_search
import asyncio
import sys
from pathlib import Path

# Adicionar diretório do backend ao path
sys.path.insert(0, str(Path(__file__).parent.parent))


async def test_search_apis():
    """Testar busca nas APIs"""

    print("\n" + "="*70)
    print("TESTE 1: BUSCA NAS APIs")
    print("="*70)

    test_queries = [
        ("leis de 2025", 2025),
        ("projetos de lei educação", None),
        ("Lei 13.979", 2020),
        ("legislação sobre saúde", None)
    ]

    for query, expected_year in test_queries:
        print(f"\n--- Buscando: '{query}' ---")
        try:
            results = await unified_search.search(query, limit=3)

            if results:
                print(f"   [OK] Encontrados {len(results)} resultados")
                for i, result in enumerate(results[:3], 1):
                    title = result.get('title', 'Sem título')[:80]
                    source = result.get('source', 'N/A')
                    date = result.get('date', 'N/A')
                    print(f"   {i}. {title}")
                    print(f"      Fonte: {source} | Data: {date}")

                # Verificar se encontrou dados de 2025 quando esperado
                if expected_year == 2025:
                    has_2025 = any(
                        str(2025) in str(r.get('date', '')) or
                        str(2025) in str(r.get('year', ''))
                        for r in results
                    )
                    if has_2025:
                        print(f"   [OK] Encontrou dados de 2025!")
                    else:
                        print(
                            f"   [AVISO] Não encontrou dados de 2025 especificamente")
            else:
                print(f"   [AVISO] Nenhum resultado encontrado")

        except Exception as e:
            print(f"   [ERRO] Erro na busca: {str(e)}")
            import traceback
            traceback.print_exc()

        await asyncio.sleep(1)  # Rate limiting


async def test_chatbot_responses():
    """Testar respostas do chatbot"""

    print("\n" + "="*70)
    print("TESTE 2: RESPOSTAS DO CHATBOT")
    print("="*70)

    test_questions = [
        "Quais leis foram aprovadas em 2025?",
        "O que é um projeto de lei?",
        "Existem leis sobre educação em 2025?",
        "Me explique sobre a Lei 13.979"
    ]

    for question in test_questions:
        print(f"\n{'='*70}")
        print(f"PERGUNTA: {question}")
        print("="*70)

        try:
            # Buscar contexto primeiro
            context = await unified_search.get_relevant_context(question, max_results=3)
            if context:
                print(f"\n[CONTEXTO ENCONTRADO]:")
                print(context[:500] + "..." if len(context) > 500 else context)
            else:
                print("\n[AVISO] Nenhum contexto encontrado nas APIs")

            # Testar resposta do chatbot
            print(f"\n[RESPOSTA DO CHATBOT]:")
            response = await chat_service.chat(question)

            message = response.get("message", "")
            sources = response.get("sources", [])

            print(message[:500] + "..." if len(message) > 500 else message)

            # Verificar se menciona limitação de data incorreta
            if "outubro de 2023" in message.lower() or "até 2023" in message.lower():
                print("\n[ERRO] Chatbot mencionou limitação de data incorreta!")
            elif "2025" in question and "2025" in message:
                print("\n[OK] Chatbot mencionou 2025 corretamente")

            if sources:
                print(f"\n[FONTES]: {len(sources)} fonte(s)")
                for i, source in enumerate(sources[:3], 1):
                    print(f"   {i}. {source.get('title', 'N/A')[:60]}...")
                    print(f"      {source.get('source', 'N/A')}")

        except Exception as e:
            print(f"\n[ERRO] Erro ao processar pergunta: {str(e)}")
            import traceback
            traceback.print_exc()

        await asyncio.sleep(2)  # Rate limiting entre perguntas


async def test_specific_2025_search():
    """Teste específico para verificar busca de 2025"""

    print("\n" + "="*70)
    print("TESTE 3: BUSCA ESPECÍFICA DE 2025")
    print("="*70)

    queries_2025 = [
        "leis 2025",
        "projetos de lei 2025",
        "legislação 2025"
    ]

    for query in queries_2025:
        print(f"\n--- Buscando: '{query}' ---")
        try:
            # Buscar com ano explícito
            results = await unified_search.search(query, limit=5, year=2025)

            if results:
                print(f"   [OK] Encontrados {len(results)} resultados")

                # Contar quantos são de 2025
                count_2025 = 0
                for result in results:
                    date_str = str(result.get('date', '')) + \
                        str(result.get('year', ''))
                    if '2025' in date_str:
                        count_2025 += 1
                        title = result.get('title', 'Sem título')[:70]
                        source = result.get('source', 'N/A')
                        print(f"   ✓ {title}")
                        print(f"     Fonte: {source}")

                if count_2025 > 0:
                    print(
                        f"\n   [SUCESSO] Encontrados {count_2025} resultados de 2025!")
                else:
                    print(
                        f"\n   [AVISO] Nenhum resultado especificamente de 2025 encontrado")
            else:
                print(f"   [AVISO] Nenhum resultado encontrado")

        except Exception as e:
            print(f"   [ERRO] Erro na busca: {str(e)}")
            import traceback
            traceback.print_exc()

        await asyncio.sleep(1)


async def test_lexml_direct():
    """Testar busca direta no LexML"""

    print("\n" + "="*70)
    print("TESTE 4: BUSCA DIRETA NO LEXML")
    print("="*70)

    try:
        from app.integrations.legislative_apis import lexml_client

        print("\n1. Buscando leis de 2025 no LexML...")
        leis = await lexml_client.search_laws(year=2025, limit=5)

        if leis:
            print(f"   [OK] Encontradas {len(leis)} leis de 2025")
            for i, lei in enumerate(leis[:3], 1):
                title = lei.get('title', 'Sem título')[:80]
                print(f"   {i}. {title}")
        else:
            print("   [AVISO] Nenhuma lei de 2025 encontrada")

        print("\n2. Buscando projetos de lei de 2025 no LexML...")
        projetos = await lexml_client.search_projects_of_law(year=2025, limit=3)

        if projetos:
            print(f"   [OK] Encontrados {len(projetos)} projetos de 2025")
            for i, projeto in enumerate(projetos[:3], 1):
                title = projeto.get('title', 'Sem título')[:80]
                print(f"   {i}. {title}")
        else:
            print("   [AVISO] Nenhum projeto de 2025 encontrado")

    except Exception as e:
        print(f"\n[ERRO] Erro ao buscar no LexML: {str(e)}")
        import traceback
        traceback.print_exc()


async def main():
    """Função principal"""

    print("\n" + "="*70)
    print("TESTE COMPLETO DO CHATBOT COM APIs")
    print("="*70)
    print("\nEste teste valida:")
    print("1. Busca nas APIs (LexML, Senado, Câmara)")
    print("2. Respostas do chatbot")
    print("3. Verificação de dados de 2025")
    print("4. Busca direta no LexML")
    print("\n" + "="*70)

    resultados = {
        "busca_apis": False,
        "chatbot": False,
        "busca_2025": False,
        "lexml_direto": False
    }

    try:
        # Teste 1: Busca nas APIs
        await test_search_apis()
        resultados["busca_apis"] = True
        await asyncio.sleep(2)

        # Teste 2: Respostas do chatbot
        await test_chatbot_responses()
        resultados["chatbot"] = True
        await asyncio.sleep(2)

        # Teste 3: Busca específica de 2025
        await test_specific_2025_search()
        resultados["busca_2025"] = True
        await asyncio.sleep(2)

        # Teste 4: LexML direto
        await test_lexml_direct()
        resultados["lexml_direto"] = True

    except Exception as e:
        print(f"\n[ERRO FATAL] {str(e)}")
        import traceback
        traceback.print_exc()

    # Resumo
    print("\n" + "="*70)
    print("RESUMO DOS TESTES")
    print("="*70)
    print(
        f"Busca nas APIs:        {'[OK]' if resultados['busca_apis'] else '[ERRO]'}")
    print(
        f"Respostas do Chatbot:  {'[OK]' if resultados['chatbot'] else '[ERRO]'}")
    print(
        f"Busca de 2025:         {'[OK]' if resultados['busca_2025'] else '[ERRO]'}")
    print(
        f"LexML Direto:          {'[OK]' if resultados['lexml_direto'] else '[ERRO]'}")
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
