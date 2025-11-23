# Guia Completo - API do Senado Federal

## 📚 Sobre a API

A API de Dados Abertos do Senado Federal fornece acesso programático a:

- **Normas** (Leis, Decretos, Medidas Provisórias, etc)
- **Matérias** (Projetos de Lei, PECs, etc)
- **Senadores** (informações e mandatos)
- **Sessões Plenárias** (pauta e votações)
- **Comissões** (permanentes e temporárias)

**Base URL:** `https://legis.senado.leg.br/dadosabertos`
**Documentação:** https://legis.senado.leg.br/dadosabertos/docs/

## 🚀 Quick Start

### 1. Teste Rápido (5 minutos)

```bash
cd voz-da-lei
python scripts/collect_senado_data.py
# Escolha opção 7 (Teste rápido)
```

### 2. Coletar Tudo (Várias horas)

```bash
python scripts/collect_senado_data.py
# Escolha opção 1 (Todas as normas desde 1988)
```

## 📊 Estrutura da API

### Endpoints Principais

#### 1. Normas (Leis e Legislação)

**Listar normas:**
```
GET /norma/listar
Parâmetros:
  - ano: Ano da norma
  - numero: Número da norma
  - tipo: Tipo (LEI, DEC, MPV, etc)
  - tramitando: S/N
  - dataInicio: YYYYMMDD
  - dataFim: YYYYMMDD
  - pagina: Número da página
  - quantidade: Itens por página (máx 100)
```

**Detalhe de norma:**
```
GET /norma/{codigo}
```

**Texto completo:**
```
GET /norma/{codigo}/texto
```

**Normas relacionadas:**
```
GET /norma/{codigo}/relacionadas
```

#### 2. Matérias (Projetos de Lei)

**Listar matérias:**
```
GET /materia/pesquisa/lista
Parâmetros:
  - ano: Ano da matéria
  - numero: Número
  - sigla: Tipo (PLS, PLC, PEC, etc)
  - tramitando: S/N
  - autor: Nome do autor
  - pagina: Número da página
  - quantidade: Itens por página
```

**Detalhe de matéria:**
```
GET /materia/{codigo}
```

**Texto/Inteiro teor:**
```
GET /materia/{codigo}/texto
```

**Autores:**
```
GET /materia/{codigo}/autores
```

**Tramitação:**
```
GET /materia/{codigo}/movimentacoes
```

**Votações:**
```
GET /materia/{codigo}/votacoes
```

#### 3. Senadores

**Listar senadores:**
```
GET /senador/lista/atual
Parâmetros:
  - legislatura: Número da legislatura
  - uf: Estado
  - partido: Sigla do partido
```

**Detalhe de senador:**
```
GET /senador/{codigo}
```

#### 4. Sessões Plenárias

**Listar sessões:**
```
GET /sessao/lista
Parâmetros:
  - dataInicio: YYYYMMDD
  - dataFim: YYYYMMDD
  - tipo: Ordinária, Extraordinária, etc
```

**Ordem do dia:**
```
GET /sessao/{data}/pauta
```

#### 5. Comissões

**Listar comissões:**
```
GET /comissao/lista
```

**Detalhe de comissão:**
```
GET /comissao/{codigo}
```

**Membros:**
```
GET /comissao/{codigo}/membros
```

## 🎯 Casos de Uso

### 1. Coletar Todas as Leis Federais

```python
from app.services.senado_collector import SenadoDataCollector
from app.core.database import SessionLocal

db = SessionLocal()
collector = SenadoDataCollector(db)

# Coletar todas as leis desde 1988
result = await collector.coletar_normas(
    ano_inicio=1988,
    ano_fim=2024,
    tipo="LEI"
)

print(f"Coletadas: {result['collected']} leis")
```

### 2. Coletar Projetos em Tramitação

```python
# PECs (Propostas de Emenda à Constituição) em tramitação
result = await collector.coletar_materias(
    ano_inicio=2020,
    ano_fim=2024,
    sigla="PEC",
    tramitando=True
)
```

### 3. Buscar por Tema

```python
# Buscar matérias sobre "educação"
result = await collector.coletar_por_tema(
    palavra_chave="educação",
    tipo="materia",
    ano=2024,
    limite=100
)
```

### 4. Monitorar Votações

```python
from app.integrations.senado_api import senado_client

# Obter votações de uma matéria
codigo_materia = "123456"
votacoes = await senado_client.votacoes_materia(codigo_materia)

for votacao in votacoes:
    print(f"Data: {votacao['data']}")
    print(f"Resultado: {votacao['resultado']}")
    print(f"Sim: {votacao['sim']}, Não: {votacao['nao']}")
```

### 5. Acompanhar Tramitação

```python
# Ver tramitação completa de um projeto
tramitacao = await senado_client.tramitacao_materia(codigo_materia)

for movimento in tramitacao:
    print(f"{movimento['data']}: {movimento['descricao']}")
```

## 📋 Tipos de Documentos

### Normas (Leis)

| Tipo | Descrição | Exemplo |
|------|-----------|---------|
| LEI | Lei ordinária | Lei nº 8.112/1990 |
| LCP | Lei complementar | LCP nº 101/2000 |
| DEC | Decreto | Decreto nº 9.203/2017 |
| MPV | Medida Provisória | MPV nº 1.234/2024 |
| EMC | Emenda Constitucional | EMC nº 95/2016 |

### Matérias (Projetos)

| Sigla | Descrição |
|-------|-----------|
| PLS | Projeto de Lei do Senado |
| PLC | Projeto de Lei da Câmara (tramitando no Senado) |
| PEC | Proposta de Emenda à Constituição |
| PRS | Projeto de Resolução do Senado |
| PDL | Projeto de Decreto Legislativo |
| MSF | Mensagem do Senado Federal |
| SUB | Substitutivo |

## 💻 Exemplos Práticos

### Exemplo 1: Script de Coleta Diária

```python
#!/usr/bin/env python3
"""
Script para atualização diária de dados do Senado
"""
import asyncio
from datetime import datetime, timedelta

async def atualizacao_diaria():
    db = SessionLocal()
    collector = SenadoDataCollector(db)
    
    # Data de ontem
    ontem = datetime.now() - timedelta(days=1)
    data_str = ontem.strftime("%Y%m%d")
    
    # Coletar normas de ontem
    from app.integrations.senado_api import senado_client
    
    normas = await senado_client.listar_normas(
        data_inicio=data_str,
        data_fim=data_str
    )
    
    # Coletar matérias atualizadas ontem
    materias = await senado_client.listar_materias(
        data_inicio=data_str,
        data_fim=data_str,
        tramitando=True
    )
    
    print(f"Normas novas: {len(normas['normas'])}")
    print(f"Matérias atualizadas: {len(materias['materias'])}")
    
    db.close()

if __name__ == "__main__":
    asyncio.run(atualizacao_diaria())
```

### Exemplo 2: Análise de Votações

```python
async def analisar_votacoes_periodo(data_inicio, data_fim):
    """
    Analisar votações de um período
    """
    from app.integrations.senado_api import senado_client
    
    # Listar sessões do período
    sessoes = await senado_client.listar_sessoes(
        data_inicio=data_inicio,
        data_fim=data_fim
    )
    
    total_votacoes = 0
    aprovadas = 0
    rejeitadas = 0
    
    for sessao in sessoes:
        # Obter pauta de cada sessão
        pauta = await senado_client.ordem_do_dia(sessao['data'])
        
        for item in pauta:
            if 'votacao' in item:
                total_votacoes += 1
                if item['votacao']['resultado'] == 'Aprovado':
                    aprovadas += 1
                else:
                    rejeitadas += 1
    
    return {
        'total': total_votacoes,
        'aprovadas': aprovadas,
        'rejeitadas': rejeitadas,
        'taxa_aprovacao': (aprovadas / total_votacoes * 100) if total_votacoes > 0 else 0
    }
```

### Exemplo 3: Relatório de Senador

```python
async def relatorio_senador(codigo_senador):
    """
    Gerar relatório completo de um senador
    """
    from app.integrations.senado_api import senado_client
    
    # Dados básicos
    senador = await senado_client.detalhe_senador(codigo_senador)
    
    # Matérias de autoria
    materias = await senado_client.listar_materias(
        autor=senador['nome'],
        tramitando=True
    )
    
    return {
        'nome': senador['nome'],
        'partido': senador['partido'],
        'uf': senador['uf'],
        'total_projetos': len(materias['materias']),
        'projetos_tramitando': len([m for m in materias['materias'] if m['tramitando']])
    }
```

### Exemplo 4: Dashboard de Comissões

```python
async def dashboard_comissoes():
    """
    Dashboard com informações de todas as comissões
    """
    from app.integrations.senado_api import senado_client
    
    comissoes = await senado_client.listar_comissoes()
    
    dados = []
    for comissao in comissoes:
        codigo = comissao['codigo']
        
        # Membros
        membros = await senado_client.membros_comissao(codigo)
        
        dados.append({
            'nome': comissao['nome'],
            'sigla': comissao['sigla'],
            'tipo': comissao['tipo'],
            'total_membros': len(membros)
        })
    
    return dados
```

## 🔄 Estratégias de Coleta

### Estratégia 1: Coleta Histórica Completa

**Objetivo:** Coletar todos os dados desde 1988

**Tempo estimado:** 6-12 horas

```python
# 1. Normas (Leis)
await collector.coletar_normas(
    ano_inicio=1988,
    ano_fim=2024
)

# 2. Matérias (Projetos) - Últimos 10 anos
await collector.coletar_materias(
    ano_inicio=2014,
    ano_fim=2024,
    tramitando=False  # Incluir arquivados
)
```

### Estratégia 2: Coleta Incremental

**Objetivo:** Atualizar dados regularmente

**Frequência:** Diária

```python
from datetime import datetime, timedelta

hoje = datetime.now()
ontem = hoje - timedelta(days=1)

# Normas publicadas ontem
await collector.coletar_normas(
    ano_inicio=ontem.year,
    ano_fim=hoje.year
)

# Matérias atualizadas ontem
await collector.coletar_materias(
    ano_inicio=ontem.year,
    ano_fim=hoje.year,
    tramitando=True
)
```

### Estratégia 3: Coleta Temática

**Objetivo:** Focar em temas específicos

```python
temas = [
    "educação",
    "saúde",
    "meio ambiente",
    "segurança pública",
    "economia"
]

for tema in temas:
    # Normas sobre o tema
    await collector.coletar_por_tema(
        palavra_chave=tema,
        tipo="norma",
        limite=200
    )
    
    # Projetos sobre o tema
    await collector.coletar_por_tema(
        palavra_chave=tema,
        tipo="materia",
        limite=200
    )
```

## 📊 Estrutura dos Dados Coletados

### Tabela: legislations

```sql
-- Normas do Senado
external_id: "senado_12345"
source: "senado"
type: "LEI", "DEC", "MPV", etc
number: "8112"
year: 1990
title: "Lei nº 8.112, de 11 de dezembro de 1990"
summary: "Dispõe sobre o regime jurídico..."
full_text: "Art. 1º Esta Lei institui..."
author: "Senado Federal"
raw_data: {JSON completo da API}

-- Matérias do Senado
external_id: "senado_mat_67890"
source: "senado"
type: "PLS", "PEC", "PLC"
number: "489"
year: 2008
title: "PLS nº 489/2008"
summary: "Ementa do projeto..."
full_text: "Texto completo..."
status: "Em tramitação"
author: "Senador XYZ"
raw_data: {JSON com detalhes, autores, tramitação}
```

## 🎯 Monitoramento

### Via Banco de Dados

```sql
-- Total de documentos do Senado
SELECT COUNT(*) FROM legislations WHERE source = 'senado';

-- Por tipo
SELECT type, COUNT(*) 
FROM legislations 
WHERE source = 'senado' 
GROUP BY type;

-- Matérias em tramitação
SELECT COUNT(*) 
FROM legislations 
WHERE source = 'senado' 
  AND status LIKE '%tramita%';

-- Normas por ano
SELECT year, COUNT(*) 
FROM legislations 
WHERE source = 'senado' AND type = 'LEI'
GROUP BY year 
ORDER BY year DESC;
```

### Via API

```bash
# Estatísticas gerais
curl http://localhost:8000/api/v1/senado/stats

# Últimas coletas
curl http://localhost:8000/api/v1/senado/recent
```

## 🔧 Integração com o Sistema

### Adicionar ao Pipeline Existente

```python
# backend/app/services/pipeline_service.py

from app.services.senado_collector import SenadoDataCollector

class PipelineService:
    def __init__(self, db_session: Session):
        self.db = db_session
        self.senado_collector = SenadoDataCollector(db_session)
    
    async def run_full_pipeline(self, source: str = "all", **kwargs):
        if source in ["senado", "all"]:
            # Coletar do Senado
            result = await self.senado_collector.coletar_normas(
                ano_inicio=2020,
                ano_fim=2024
            )
            
            # Processar dados...
```

### Endpoints da API

```python
# backend/app/api/v1/senado.py

from fastapi import APIRouter, Depends
from app.services.senado_collector import SenadoDataCollector

router = APIRouter()

@router.post("/collect/normas")
async def collect_normas(
    ano_inicio: int,
    ano_fim: int,
    db: Session = Depends(get_db)
):
    collector = SenadoDataCollector(db)
    result = await collector.coletar_normas(ano_inicio, ano_fim)
    return result

@router.post("/collect/materias")
async def collect_materias(
    ano_inicio: int,
    ano_fim: int,
    db: Session = Depends(get_db)
):
    collector = SenadoDataCollector(db)
    result = await collector.coletar_materias(ano_inicio, ano_fim)
    return result

@router.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    collector = SenadoDataCollector(db)
    stats = await collector.estatisticas()
    return stats
```

## 📝 Boas Práticas

### 1. Rate Limiting

```python
import asyncio

# Adicionar delays entre requisições
async def coletar_com_delay():
    for ano in range(1988, 2025):
        await collector.coletar_normas(ano_inicio=ano, ano_fim=ano)
        await asyncio.sleep(2)  # 2 segundos entre anos
```

### 2. Tratamento de Erros

```python
try:
    result = await collector.coletar_normas(ano_inicio=2024, ano_fim=2024)
except Exception as e:
    logger.error(f"Erro na coleta: {e}")
    # Notificar, tentar novamente, etc
```

### 3. Logs Detalhados

```python
from loguru import logger

logger.add("logs/senado_collector.log", rotation="500 MB")

logger.info(f"Iniciando coleta de normas do ano {ano}")
logger.debug(f"Parâmetros: tipo={tipo}, tramitando={tramitando}")
logger.success(f"Coletadas {total} normas com sucesso")
logger.error(f"Erro ao processar norma {codigo}: {erro}")
```

### 4. Cache de Dados

```python
from functools import lru_cache
from datetime import timedelta

@lru_cache(maxsize=100)
async def get_cached_norma(codigo: str):
    """Cache de normas por 1 hora"""
    return await senado_client.detalhe_norma(codigo)
```

## 🆘 Troubleshooting

### Erro: "Connection timeout"

**Causa:** API do Senado está lenta

**Solução:**
```python
# Aumentar timeout
import aiohttp

async with aiohttp.ClientSession(
    timeout=aiohttp.ClientTimeout(total=120)
) as session:
    # requisições
```

### Erro: "Código inválido"

**Causa:** Formato do código está incorreto

**Solução:**
```python
# Validar código antes de usar
if codigo and isinstance(codigo, (str, int)):
    result = await client.detalhe_norma(str(codigo))
```

### Erro: "Muitos registros"

**Causa:** Tentando coletar muitos dados de uma vez

**Solução:**
```python
# Usar paginação
pagina = 1
while True:
    resultado = await client.listar_normas(ano=2024, pagina=pagina)
    if not resultado['normas']:
        break
    # processar
    pagina += 1
```

## 🎉 Conclusão

A integração com o Senado Federal está completa! Você pode:

✅ Coletar todas as leis desde 1988
✅ Coletar projetos de lei em tramitação
✅ Buscar por palavras-chave
✅ Monitorar votações e tramitação
✅ Obter informações de senadores
✅ Acessar dados de comissões

**Próximo passo:**
```bash
python scripts/collect_senado_data.py
```
