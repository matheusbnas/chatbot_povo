# Guia Completo de Integração LexML - Voz da Lei

## Sobre o LexML

O LexML (Rede de Informação Legislativa e Jurídica) é uma plataforma que agrega todas as leis, projetos de lei e documentos legislativos brasileiros em um único repositório. É mantido pelo governo federal e contém:

- **Leis Federais, Estaduais e Municipais**
- **Projetos de Lei da Câmara e Senado**
- **Emendas Constitucionais**
- **Decretos, Portarias e outros documentos normativos**

## Arquitetura Atual no Voz da Lei

Seu projeto já possui uma integração básica com o LexML. Vamos detalhar e expandir.

### 1. Estrutura Existente

```
backend/
├── app/
│   ├── integrations/
│   │   └── legislative_apis.py  # Cliente LexML já implementado
│   ├── services/
│   │   ├── data_collector.py    # Coleta de dados
│   │   ├── text_processor.py    # Processamento de textos
│   │   └── pipeline_service.py  # Pipeline completo
│   └── api/v1/
│       └── data_pipeline.py     # Endpoints para coleta
```

## 2. Como Funciona a API do LexML

### 2.1. Protocolo SRU (Search/Retrieve via URL)

O LexML usa o protocolo SRU, um padrão internacional para busca em repositórios XML.

**URL Base:** `https://www.lexml.gov.br/busca/SRU`

**Parâmetros principais:**
- `operation`: sempre "searchRetrieve"
- `query`: query de busca (sintaxe CQL - Contextual Query Language)
- `startRecord`: registro inicial (para paginação)
- `maximumRecords`: quantidade de registros
- `recordSchema`: formato dos registros (geralmente "dc" - Dublin Core)

### 2.2. Sintaxe de Queries

```
# Buscar por URN
urn="senado.federal pls 2008"

# Buscar por título
dc.title all "meio ambiente"

# Buscar por tipo de documento
tipoDocumento="Lei"

# Buscar por ano
dc.date="2023"

# Buscar por autoridade
autoridade="Senado Federal"

# Combinar critérios
tipoDocumento="Lei" and dc.date="2023" and dc.title all "educação"
```

## 3. Implementação Atual

### 3.1. Cliente LexML (já implementado)

O arquivo `backend/app/integrations/legislative_apis.py` já contém a classe `LexMLClient`:

```python
class LexMLClient:
    BASE_URL = "https://www.lexml.gov.br/busca/SRU"
    
    async def search(self, query, start_record=1, maximum_records=20):
        # Busca genérica usando SRU
        
    async def search_by_keywords(self, keywords, year=None, tipo_documento=None):
        # Busca por palavras-chave
        
    async def search_projects_of_law(self, year=None, house=None):
        # Busca projetos de lei
        
    async def search_laws(self, year=None, keywords=None):
        # Busca leis
```

### 3.2. Data Collector (já implementado)

O arquivo `backend/app/services/data_collector.py` contém:

```python
class DataCollector:
    async def collect_from_lexml(self, year=None, tipo_documento=None, limit=100):
        # Coleta dados do LexML e salva no banco
```

## 4. Como Usar a Integração Existente

### 4.1. Via API REST

**Endpoint:** `POST /api/v1/data/collect/lexml`

**Parâmetros:**
- `year`: Ano para filtrar (opcional)
- `tipo_documento`: "Lei", "Projeto de Lei", etc. (opcional)
- `limit`: Quantidade máxima de documentos (1-1000)

**Exemplo usando curl:**

```bash
# Coletar leis de 2023
curl -X POST "http://localhost:8000/api/v1/data/collect/lexml?year=2023&tipo_documento=Lei&limit=50"

# Coletar projetos de lei de 2024
curl -X POST "http://localhost:8000/api/v1/data/collect/lexml?year=2024&tipo_documento=Projeto de Lei&limit=100"
```

### 4.2. Pipeline Completo

**Endpoint:** `POST /api/v1/data/pipeline/run`

Este endpoint executa o pipeline completo:
1. Coleta de dados do LexML
2. Pré-processamento e chunking
3. Construção de corpus (pares pergunta-resposta)
4. Geração de embeddings

```bash
curl -X POST "http://localhost:8000/api/v1/data/pipeline/run?source=lexml&year=2023&tipo_documento=Lei&limit=50"
```

### 4.3. Via Python (programaticamente)

```python
from app.services.data_collector import DataCollector
from app.core.database import SessionLocal

# Criar sessão do banco
db = SessionLocal()

# Criar collector
collector = DataCollector(db)

# Coletar dados
result = await collector.collect_from_lexml(
    year=2023,
    tipo_documento="Lei",
    limit=50
)

print(f"Coletados: {result['collected']}")
print(f"Falhas: {result['failed']}")
```

## 5. Expandindo a Coleta de Dados

### 5.1. Coletar TODAS as Leis (Estratégia Recomendada)

Para coletar todas as leis brasileiras, você deve fazer isso em lotes por ano:

```python
# Script de coleta completa
import asyncio
from datetime import datetime

async def collect_all_laws():
    db = SessionLocal()
    collector = DataCollector(db)
    
    # Coletar de 1988 (Constituição) até hoje
    current_year = datetime.now().year
    
    for year in range(1988, current_year + 1):
        print(f"Coletando leis de {year}...")
        
        # Coletar leis
        result = await collector.collect_from_lexml(
            year=year,
            tipo_documento="Lei",
            limit=1000  # Máximo por requisição
        )
        
        print(f"Ano {year}: {result['collected']} leis coletadas")
        
        # Aguardar para não sobrecarregar o servidor
        await asyncio.sleep(1)
    
    db.close()

# Executar
asyncio.run(collect_all_laws())
```

### 5.2. Coletar Projetos de Lei

```python
async def collect_all_projects():
    db = SessionLocal()
    collector = DataCollector(db)
    
    current_year = datetime.now().year
    
    # Últimos 5 anos de projetos
    for year in range(current_year - 5, current_year + 1):
        print(f"Coletando projetos de {year}...")
        
        result = await collector.collect_from_lexml(
            year=year,
            tipo_documento="Projeto de Lei",
            limit=1000
        )
        
        print(f"Ano {year}: {result['collected']} projetos coletados")
        await asyncio.sleep(1)
    
    db.close()
```

### 5.3. Coletar Legislação Municipal

```python
async def collect_municipal_laws(state, city):
    """
    Coletar leis municipais de uma cidade específica
    """
    from app.integrations.legislative_apis import lexml_client
    
    # Buscar leis municipais
    results = await lexml_client.search_by_keywords(
        keywords="",  # Buscar todas
        year=None,
        tipo_documento="Lei",
        autoridade=f"Município de {city}"
    )
    
    return results

# Exemplo: coletar leis de São Paulo
laws_sp = await collect_municipal_laws("SP", "São Paulo")
```

## 6. Estrutura dos Dados Coletados

### 6.1. Campos Principais

Cada documento coletado do LexML contém:

```python
{
    "urn": "urn:lex:br:federal:lei:2023-11-30;14724",
    "title": "Lei nº 14.724, de 30 de novembro de 2023",
    "description": "Dispõe sobre...",
    "date": "2023-11-30",
    "tipo_documento": "Lei",
    "autoridade": "Presidência da República",
    "localidade": "br",
    "facet_localidade": "Federal",
    "full_text": "Art. 1º Esta lei...",
    "lexml_id": "12345"
}
```

### 6.2. Como é Armazenado no Banco

```sql
-- Tabela: legislations
CREATE TABLE legislations (
    id SERIAL PRIMARY KEY,
    external_id VARCHAR,      -- lexml_id
    source VARCHAR,           -- "lexml"
    type VARCHAR,             -- "Lei", "Projeto de Lei"
    number VARCHAR,           -- "14.724"
    year INTEGER,             -- 2023
    title TEXT,               -- Título completo
    summary TEXT,             -- Descrição
    full_text TEXT,           -- Texto completo
    simplified_text TEXT,     -- Texto simplificado pela IA
    status VARCHAR,
    author VARCHAR,           -- Autoridade
    raw_data JSON,            -- Dados brutos do LexML
    created_at TIMESTAMP
);
```

## 7. Processamento Pós-Coleta

Após coletar os dados, o pipeline faz:

### 7.1. Chunking

Divide o texto em partes menores (artigos, parágrafos):

```python
# backend/app/services/text_processor.py
chunks = text_processor.process_legislation_text(
    legislation.full_text,
    legislation.id
)

# Resultado:
[
    {
        "type": "article",
        "number": "1",
        "content": "Art. 1º Esta lei...",
        "normalized_content": "Artigo 1: Esta lei...",
        "word_count": 45,
        "citations": [...]
    },
    ...
]
```

### 7.2. Geração de Corpus

Cria pares pergunta-resposta automaticamente:

```python
# backend/app/services/corpus_builder.py
qa_pairs = [
    {
        "question": "O que diz o artigo 1 da Lei 14.724/2023?",
        "answer": "Art. 1º Esta lei...",
        "question_type": "o_que_diz"
    },
    ...
]
```

### 7.3. Embeddings

Gera vetores para busca semântica:

```python
# backend/app/services/embedding_service.py
embedding = embedding_service.generate_embedding(text)
# Resultado: [0.123, -0.456, 0.789, ...]
```

## 8. Consultas Avançadas no LexML

### 8.1. Buscar Leis sobre um Tema

```python
async def search_laws_by_theme(theme: str):
    """
    Buscar leis relacionadas a um tema específico
    """
    results = await lexml_client.search_by_keywords(
        keywords=theme,
        tipo_documento="Lei",
        limit=100
    )
    return results

# Exemplo
education_laws = await search_laws_by_theme("educação")
health_laws = await search_laws_by_theme("saúde pública")
```

### 8.2. Buscar Projetos em Tramitação

```python
async def search_active_projects():
    """
    Buscar projetos de lei do ano atual
    """
    current_year = datetime.now().year
    
    results = await lexml_client.search_projects_of_law(
        year=current_year,
        limit=100
    )
    return results
```

### 8.3. Buscar por Autor/Autoridade

```python
async def search_by_authority(authority: str):
    """
    Buscar documentos de uma autoridade específica
    """
    results = await lexml_client.search_by_keywords(
        keywords="",
        autoridade=authority,
        limit=100
    )
    return results

# Exemplos
senate_docs = await search_by_authority("Senado Federal")
chamber_docs = await search_by_authority("Câmara dos Deputados")
```

## 9. Monitoramento e Jobs

### 9.1. Verificar Status de Coleta

```bash
# GET /api/v1/data/jobs/{job_id}
curl http://localhost:8000/api/v1/data/jobs/1
```

Resposta:
```json
{
  "id": 1,
  "job_type": "lexml",
  "status": "completed",
  "total_items": 150,
  "processed_items": 148,
  "failed_items": 2,
  "started_at": "2024-01-01T10:00:00",
  "completed_at": "2024-01-01T10:15:00"
}
```

## 10. Boas Práticas

### 10.1. Respeitar Rate Limits

```python
import asyncio

async def collect_with_rate_limit(years: list):
    for year in years:
        await collector.collect_from_lexml(year=year, limit=100)
        # Aguardar entre requisições
        await asyncio.sleep(1)
```

### 10.2. Processar em Background

Use Celery para jobs longos:

```python
# backend/app/tasks.py
from celery import Celery

celery_app = Celery('voz_da_lei', broker='redis://localhost:6379/0')

@celery_app.task
def collect_laws_task(year):
    # Executar coleta em background
    pass
```

### 10.3. Validar Dados

```python
def validate_legislation(data: dict) -> bool:
    required_fields = ['title', 'tipo_documento', 'date']
    return all(field in data for field in required_fields)
```

## 11. Exemplos Práticos

### 11.1. Coletar Últimas Leis Aprovadas

```python
async def collect_recent_laws():
    current_year = datetime.now().year
    
    # Leis do ano atual
    result = await collector.collect_from_lexml(
        year=current_year,
        tipo_documento="Lei",
        limit=100
    )
    
    return result
```

### 11.2. Buscar Leis de um Estado

```python
async def collect_state_laws(state: str):
    """
    Coletar leis estaduais
    """
    results = await lexml_client.search_by_keywords(
        keywords="",
        tipo_documento="Lei",
        autoridade=f"Assembleia Legislativa do Estado de {state}"
    )
    
    return results
```

### 11.3. Pipeline Completo Automatizado

```python
async def run_daily_update():
    """
    Executar atualização diária
    """
    from app.services.pipeline_service import PipelineService
    
    db = SessionLocal()
    pipeline = PipelineService(db)
    
    # Coletar, processar e gerar embeddings
    result = await pipeline.run_full_pipeline(
        source="lexml",
        year=datetime.now().year,
        limit=50
    )
    
    print(f"Pipeline concluído: {result}")
    db.close()
```

## 12. Próximos Passos

### 12.1. Implementar Busca de Texto Completo

O LexML pode retornar URLs para o texto completo. Implemente:

```python
async def fetch_full_text(urn: str) -> str:
    """
    Baixar texto completo de uma lei
    """
    # Construir URL baseada na URN
    url = f"https://www.lexml.gov.br/urn/{urn}"
    # Fazer download e extrair texto
    pass
```

### 12.2. Adicionar Versionamento

Leis podem ser alteradas. Implemente controle de versão:

```sql
ALTER TABLE legislations ADD COLUMN version INTEGER;
ALTER TABLE legislations ADD COLUMN previous_version_id INTEGER;
```

### 12.3. Criar Índices para Busca Rápida

```sql
CREATE INDEX idx_legislation_type ON legislations(type);
CREATE INDEX idx_legislation_year ON legislations(year);
CREATE INDEX idx_legislation_title ON legislations USING gin(to_tsvector('portuguese', title));
```

## 13. Troubleshooting

### 13.1. Erro 401/403

**Problema:** O LexML não requer autenticação, mas pode bloquear requisições excessivas.

**Solução:** 
- Adicione delays entre requisições
- Use User-Agent apropriado

```python
headers = {
    "User-Agent": "VozDaLei/1.0 (contato@vozdalei.com.br)"
}
```

### 13.2. Timeout em Requisições

**Problema:** Requisições demoram muito.

**Solução:**
```python
async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60)) as session:
    # requisições
```

### 13.3. XML Malformado

**Problema:** Alguns documentos têm XML inválido.

**Solução:**
```python
try:
    root = ET.fromstring(xml_content)
except ET.ParseError:
    # Tentar limpar o XML
    xml_content = re.sub(r'[^\x09\x0A\x0D\x20-\xD7FF\xE000-\xFFFD]', '', xml_content)
    root = ET.fromstring(xml_content)
```

## Conclusão

Você já tem uma excelente base de integração com o LexML. Para coletar todas as leis:

1. **Execute o pipeline por ano** (1988-2024)
2. **Processe os dados** (chunking, corpus, embeddings)
3. **Configure jobs recorrentes** para manter atualizado
4. **Monitore a qualidade** dos dados coletados

A arquitetura já está pronta - basta executar! 🚀
