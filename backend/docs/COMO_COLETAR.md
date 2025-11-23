# Como Coletar Dados do LexML - Guia Rápido

## 🚀 Início Rápido

### Opção 1: Via Script Python (Recomendado)

```bash
# 1. Entre no diretório do projeto
cd voz-da-lei

# 2. Ative o ambiente virtual
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# 3. Execute o script de coleta
python scripts/collect_lexml_data.py
```

**Menu interativo:**
```
1. Coletar TODAS as leis federais (1988-2024) ⚠️ DEMORADO
2. Coletar leis de um ano específico
3. Coletar projetos de lei recentes (últimos 5 anos)
4. Coletar leis sobre um tema específico
5. Executar pipeline completo (coleta + processamento)
6. Teste rápido (10 leis do ano atual)
```

### Opção 2: Via API REST

```bash
# 1. Inicie o servidor backend
cd backend
uvicorn app.main:app --reload

# 2. Em outro terminal, execute os testes
cd scripts
bash test_lexml_api.sh
```

**Ou use curl diretamente:**

```bash
# Coletar leis de 2023
curl -X POST "http://localhost:8000/api/v1/data/collect/lexml?year=2023&tipo_documento=Lei&limit=20"

# Executar pipeline completo
curl -X POST "http://localhost:8000/api/v1/data/pipeline/run?source=lexml&year=2023&limit=10"

# Ver legislações em destaque
curl -X GET "http://localhost:8000/api/v1/legislation/trending?limit=10"
```

### Opção 3: Jupyter Notebook (Exploração Interativa)

```bash
# 1. Instale Jupyter
pip install jupyter matplotlib

# 2. Inicie o Jupyter
jupyter notebook notebooks/lexml_exploration.ipynb
```

## 📊 Estratégias de Coleta

### 1. Teste Inicial (Rápido - 2 minutos)

```bash
python scripts/collect_lexml_data.py
# Escolha opção 6 (Teste rápido)
```

Isso vai coletar 10 leis do ano atual para você testar.

### 2. Coleta por Tema (Médio - 5-10 minutos)

```bash
python scripts/collect_lexml_data.py
# Escolha opção 4
# Digite: educação (ou saúde, trabalho, etc)
# Limite: 100
```

### 3. Coleta Anual (Médio - 10-30 minutos)

```bash
python scripts/collect_lexml_data.py
# Escolha opção 2
# Digite o ano: 2023
# Tipo: Lei
```

### 4. Coleta Completa (Longo - 6-12 horas)

```bash
python scripts/collect_lexml_data.py
# Escolha opção 1
# Confirme com 's'
```

⚠️ **ATENÇÃO:** Isso vai coletar TODAS as leis de 1988 até hoje!

## 🎯 Exemplos Práticos

### Exemplo 1: Coletar Leis sobre Educação

```python
from app.integrations.legislative_apis import lexml_client

# Buscar leis sobre educação
results = await lexml_client.search_by_keywords(
    keywords="educação",
    tipo_documento="Lei",
    limit=50
)

print(f"Encontradas {len(results)} leis sobre educação")
```

### Exemplo 2: Coletar Projetos de Lei do Senado

```python
results = await lexml_client.search_projects_of_law(
    year=2024,
    house="senado",
    limit=100
)
```

### Exemplo 3: Pipeline Completo (Coleta + Processamento)

```python
from app.services.pipeline_service import PipelineService
from app.core.database import SessionLocal

db = SessionLocal()
pipeline = PipelineService(db)

# Executar pipeline completo
result = await pipeline.run_full_pipeline(
    source="lexml",
    year=2023,
    tipo_documento="Lei",
    limit=50
)

print(f"Coletados: {result['collected']}")
print(f"Processados: {result['processed']}")
print(f"Chunks criados: {result['chunks_created']}")
print(f"Pares QA: {result['corpus_pairs']}")
print(f"Embeddings: {result['embeddings_generated']}")
```

## 🗄️ Estrutura dos Dados

### Tabela: legislations

```sql
id              -- ID único
external_id     -- ID do LexML
source          -- "lexml"
type            -- "Lei", "Projeto de Lei", etc
number          -- Número da lei
year            -- Ano
title           -- Título completo
summary         -- Ementa/descrição
full_text       -- Texto completo (se disponível)
author          -- Autoridade/autor
raw_data        -- JSON com dados brutos do LexML
created_at      -- Data de coleta
```

### Verificar Dados Coletados

```bash
# Via psql
psql -U vozdalei -d vozdalei -c "SELECT COUNT(*) FROM legislations;"

# Ver últimas 10 leis
psql -U vozdalei -d vozdalei -c "SELECT id, type, number, year, title FROM legislations ORDER BY created_at DESC LIMIT 10;"
```

## 📈 Monitoramento

### Via API

```bash
# Status de um job
curl http://localhost:8000/api/v1/data/jobs/1

# Legislações coletadas
curl http://localhost:8000/api/v1/legislation/trending?limit=20
```

### Via Banco de Dados

```sql
-- Total de documentos por tipo
SELECT type, COUNT(*) 
FROM legislations 
GROUP BY type;

-- Documentos por ano
SELECT year, COUNT(*) 
FROM legislations 
GROUP BY year 
ORDER BY year DESC;

-- Documentos coletados hoje
SELECT COUNT(*) 
FROM legislations 
WHERE created_at::date = CURRENT_DATE;
```

## ⚡ Dicas de Performance

### 1. Use Limites Razoáveis

```python
# ❌ Muito: pode demorar e sobrecarregar
limit=10000

# ✅ Bom: equilíbrio entre velocidade e quantidade
limit=100
```

### 2. Adicione Delays

```python
import asyncio

for year in range(2020, 2025):
    await collector.collect_from_lexml(year=year, limit=100)
    await asyncio.sleep(1)  # Esperar 1 segundo entre anos
```

### 3. Use Jobs em Background

```python
# Execute coletas longas em background
from celery import Celery

@celery_app.task
def collect_all_laws_task():
    # Coleta em background
    pass
```

### 4. Monitore o Progresso

```python
from app.models.models import DataCollectionJob

# Verificar status do job
job = db.query(DataCollectionJob).filter_by(id=job_id).first()
print(f"Progresso: {job.processed_items}/{job.total_items}")
```

## 🐛 Troubleshooting

### Erro: "Connection refused"

**Problema:** Servidor não está rodando.

**Solução:**
```bash
cd backend
uvicorn app.main:app --reload
```

### Erro: "Database não existe"

**Problema:** Banco de dados não foi criado.

**Solução:**
```bash
# Criar banco
createdb -U vozdalei vozdalei

# Rodar migrations
cd backend
python -c "from app.core.database import init_db; init_db()"
```

### Erro: "401 Unauthorized"

**Problema:** Chave de API não configurada.

**Solução:**
```bash
# Editar .env
cd backend
nano .env

# Adicionar:
OPENAI_API_KEY=sua_chave_aqui
# ou
ANTHROPIC_API_KEY=sua_chave_aqui
# ou
GROQ_API_KEY=sua_chave_aqui
```

### Timeout em Requisições

**Problema:** LexML está lento ou indisponível.

**Solução:**
```python
# Aumentar timeout
async with aiohttp.ClientSession(
    timeout=aiohttp.ClientTimeout(total=120)
) as session:
    # requisições
```

## 📚 Recursos Adicionais

- **Documentação Completa:** `lexml_integration_guide.md`
- **Script de Coleta:** `scripts/collect_lexml_data.py`
- **Notebook de Exploração:** `notebooks/lexml_exploration.ipynb`
- **API REST:** http://localhost:8000/docs

## 💡 Próximos Passos

1. ✅ Teste rápido (opção 6)
2. ✅ Coletar leis de 2023 e 2024
3. ✅ Explorar dados no notebook
4. ✅ Executar pipeline completo
5. 🚀 Coletar dados históricos (1988-2024)

## 🤝 Suporte

Se encontrar problemas:

1. Verifique os logs: `backend/logs/app.log`
2. Consulte a documentação: `lexml_integration_guide.md`
3. Teste a API do LexML diretamente: https://www.lexml.gov.br/busca/SRU

---

**Pronto para começar?** 🎉

```bash
python scripts/collect_lexml_data.py
```
