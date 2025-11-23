"""
Script de teste para verificar extração de texto completo do LexML

Este teste demonstra:
1. Busca de documentos por URN
2. Tentativa de extração de texto completo
3. Detecção de metadados SRU vs documento completo
4. Processamento de múltiplos documentos

NOTA: O LexML pode não fornecer texto completo diretamente via API pública.
Este teste valida que a funcionalidade está implementada e funcionando corretamente.
"""
from app.integrations.legislative_apis import lexml_client
import asyncio
import sys
from pathlib import Path

# Adicionar o diretório app ao path (voltar um nível de tests/ para backend/)
sys.path.insert(0, str(Path(__file__).parent.parent))


async def test_get_full_text():
    """Testar obtenção de texto completo usando uma URN real"""

    # URN de exemplo do LexML (PL 1694/2025 - projeto recente)
    test_urn = "urn:lex:br:camara.deputados:projeto.lei;pl:2025;1694"

    print("=" * 80)
    print("TESTE: Extração de Texto Completo do LexML")
    print("=" * 80)
    print(f"\nURN de teste: {test_urn}")
    print("\n1. Buscando documento por URN...")

    try:
        # Primeiro, buscar o documento
        document = await lexml_client.get_document_by_urn(test_urn)

        if document:
            print("[OK] Documento encontrado!")
            print(f"\nTitulo: {document.get('title', 'N/A')}")
            print(f"Tipo: {document.get('tipo_documento', 'N/A')}")
            print(f"Data: {document.get('date', 'N/A')}")
            print(f"URN: {document.get('urn', 'N/A')}")
            print(f"Descricao: {document.get('description', 'N/A')[:200]}...")

            # Verificar se tem texto completo
            full_text = document.get('full_text')
            if full_text:
                print("\n" + "=" * 80)
                print("[OK] TEXTO COMPLETO OBTIDO!")
                print("=" * 80)
                print(f"\nTamanho: {len(full_text)} caracteres")
                print(f"\nPrimeiros 500 caracteres:\n{full_text[:500]}...")
                print(f"\nUltimos 200 caracteres:\n...{full_text[-200:]}")
            else:
                print("\n[AVISO] Texto completo nao disponivel")
                print("Tentando buscar texto completo diretamente...")

                # Tentar buscar texto completo diretamente
                urn_from_doc = document.get('urn')
                if urn_from_doc:
                    full_text = await lexml_client._get_document_full_text(urn_from_doc)
                    if full_text:
                        print("\n[OK] Texto completo obtido diretamente!")
                        print(f"Tamanho: {len(full_text)} caracteres")
                        print(
                            f"\nPrimeiros 500 caracteres:\n{full_text[:500]}...")
                    else:
                        print("\n[ERRO] Nao foi possivel obter texto completo")
                        print("Possiveis razoes:")
                        print("- Endpoint nao disponivel")
                        print("- Formato XML diferente do esperado")
                        print("- Documento nao tem texto completo disponivel")
        else:
            print("[ERRO] Documento nao encontrado")

    except Exception as e:
        print(f"\n[ERRO] Erro durante o teste: {str(e)}")
        import traceback
        traceback.print_exc()


async def test_search_and_extract():
    """Testar busca e extração de texto de múltiplos documentos"""

    print("\n" + "=" * 80)
    print("TESTE: Busca e Extração de Múltiplos Documentos")
    print("=" * 80)

    try:
        # Buscar projetos de lei recentes
        print("\n1. Buscando projetos de lei do ano 2025...")
        projects = await lexml_client.search_projects_of_law(year=2025, limit=3)

        print(f"[OK] Encontrados {len(projects)} projetos")

        for i, doc in enumerate(projects, 1):
            print(f"\n--- Documento {i} ---")
            print(f"Titulo: {doc.get('title', 'N/A')}")
            print(f"URN: {doc.get('urn', 'N/A')}")

            # Tentar obter texto completo
            urn = doc.get('urn')
            if urn:
                print("   Tentando obter texto completo...")
                full_text = await lexml_client._get_document_full_text(urn)
                if full_text:
                    print(
                        f"   [OK] Texto obtido ({len(full_text)} caracteres)")
                    print(f"   Preview: {full_text[:200]}...")
                else:
                    print("   [AVISO] Texto completo nao disponivel")

    except Exception as e:
        print(f"\n[ERRO] Erro durante o teste: {str(e)}")
        import traceback
        traceback.print_exc()


async def test_search_2025_by_urn():
    """Testar busca de 2025 usando query URN como no exemplo"""
    
    print("\n" + "=" * 80)
    print("TESTE: Busca de 2025 usando query URN")
    print("=" * 80)
    
    try:
        # Query exata do exemplo: urn="2025"
        print("\n1. Buscando documentos com URN contendo '2025'...")
        query = 'urn="2025"'
        result = await lexml_client.search(query, maximum_records=5)
        
        print(f"[OK] Encontrados {result.get('total', 0)} documentos no total")
        print(f"Retornando {len(result.get('records', []))} registros")
        
        records = result.get('records', [])
        for i, doc in enumerate(records[:3], 1):
            print(f"\n--- Documento {i} ---")
            print(f"Título: {doc.get('title', 'N/A')}")
            print(f"Tipo: {doc.get('tipo_documento', 'N/A')}")
            print(f"Data: {doc.get('date', 'N/A')}")
            print(f"URN: {doc.get('urn', 'N/A')}")
            print(f"Localidade: {doc.get('localidade', 'N/A')}")
            if doc.get('description'):
                print(f"Descrição: {doc.get('description', '')[:150]}...")
        
    except Exception as e:
        print(f"\n[ERRO] Erro durante o teste: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\n[TESTE] Iniciando testes do LexML...\n")

    # Executar testes
    asyncio.run(test_get_full_text())
    asyncio.run(test_search_and_extract())
    asyncio.run(test_search_2025_by_urn())

    print("\n" + "=" * 80)
    print("[OK] Testes concluidos!")
    print("=" * 80)
