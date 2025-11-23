#!/usr/bin/env python3
"""
Teste específico para busca de lei específica (ex: Lei nº 2025)
Execute: python backend/tests/test_lei_especifica.py
"""

import asyncio
import sys
from pathlib import Path

# Adicionar diretório do backend ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.legislation_search import unified_search
from app.ai.simplification import chat_service
from loguru import logger


async def test_busca_lei_2025():
    """Testar busca específica da Lei nº 2025"""
    
    print("\n" + "="*70)
    print("TESTE: BUSCA DA LEI Nº 2025")
    print("="*70)
    
    queries = [
        "Lei nº 2025",
        "Lei n° 2025",
        "Lei 2025",
        "Lei número 2025",
        "Lei 2025 de 2025"
    ]
    
    for query in queries:
        print(f"\n--- Buscando: '{query}' ---")
        try:
            results = await unified_search.search(query, limit=5)
            
            if results:
                print(f"   [OK] Encontrados {len(results)} resultados")
                
                # Procurar especificamente pela Lei 2025
                encontrou_lei_2025 = False
                for i, result in enumerate(results, 1):
                    title = result.get('title', '')
                    number = result.get('number', '')
                    
                    # Verificar se é a Lei 2025
                    if '2025' in title and ('lei' in title.lower() or 'Lei' in title):
                        encontrou_lei_2025 = True
                        print(f"   [ENCONTRADA] {i}. {title[:80]}")
                        print(f"      Fonte: {result.get('source', 'N/A')}")
                        print(f"      Data: {result.get('date', 'N/A')}")
                        print(f"      Número: {number}")
                    else:
                        print(f"   {i}. {title[:80]}")
                
                if encontrou_lei_2025:
                    print(f"\n   [SUCESSO] Lei 2025 encontrada!")
                else:
                    print(f"\n   [AVISO] Lei 2025 não encontrada especificamente")
            else:
                print(f"   [AVISO] Nenhum resultado encontrado")
                
        except Exception as e:
            print(f"   [ERRO] Erro na busca: {str(e)}")
            import traceback
            traceback.print_exc()
        
        await asyncio.sleep(1)


async def test_chatbot_lei_2025():
    """Testar resposta do chatbot sobre Lei 2025"""
    
    print("\n" + "="*70)
    print("TESTE: CHATBOT SOBRE LEI Nº 2025")
    print("="*70)
    
    pergunta = "Me explique sobre a Lei nº 2025, de 26 de junho de 2025"
    
    print(f"\nPERGUNTA: {pergunta}")
    print("="*70)
    
    try:
        # Buscar contexto primeiro
        context = await unified_search.get_relevant_context(pergunta, max_results=5)
        
        if context:
            print(f"\n[CONTEXTO ENCONTRADO]:")
            print(context)
        else:
            print("\n[AVISO] Nenhum contexto encontrado")
        
        # Testar resposta do chatbot
        print(f"\n[RESPOSTA DO CHATBOT]:")
        response = await chat_service.chat(pergunta)
        
        message = response.get("message", "")
        sources = response.get("sources", [])
        
        # Mostrar resposta (limitado para evitar problemas de encoding)
        print(message[:800] + "..." if len(message) > 800 else message)
        
        # Verificar se menciona a Lei 2025
        if "2025" in message and ("lei" in message.lower() or "Lei" in message):
            print("\n[OK] Chatbot mencionou a Lei 2025")
        else:
            print("\n[AVISO] Chatbot pode não ter mencionado a Lei 2025 corretamente")
        
        # Verificar se diz que não encontrou (erro)
        if "não encontrei" in message.lower() or "não tenho" in message.lower():
            if context:
                print("\n[ERRO] Chatbot disse que não encontrou, mas havia contexto disponível!")
            else:
                print("\n[OK] Chatbot disse que não encontrou e realmente não havia contexto")
        
        if sources:
            print(f"\n[FONTES]: {len(sources)} fonte(s)")
            for i, source in enumerate(sources[:3], 1):
                print(f"   {i}. {source.get('title', 'N/A')[:60]}...")
                print(f"      {source.get('source', 'N/A')}")
        
    except Exception as e:
        print(f"\n[ERRO] Erro ao processar: {str(e)}")
        import traceback
        traceback.print_exc()


async def main():
    """Função principal"""
    
    print("\n" + "="*70)
    print("TESTE: BUSCA DE LEI ESPECÍFICA (Lei nº 2025)")
    print("="*70)
    print("\nEste teste valida se o chatbot encontra e responde corretamente")
    print("sobre a Lei nº 2025, de 26 de junho de 2025.\n")
    
    try:
        # Teste 1: Busca direta
        await test_busca_lei_2025()
        await asyncio.sleep(2)
        
        # Teste 2: Resposta do chatbot
        await test_chatbot_lei_2025()
        
    except Exception as e:
        print(f"\n[ERRO FATAL] {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nOperação cancelada pelo usuário.")
    except Exception as e:
        print(f"\n\nErro fatal: {str(e)}")
        import traceback
        traceback.print_exc()

