# 📚 Guia Completo de Integração LexML - Voz da Lei

## 🎯 Visão Geral

Este guia contém tudo que você precisa para coletar, processar e utilizar dados do LexML (todas as leis brasileiras) na plataforma Voz da Lei.

## 📑 Documentação Disponível

### 1. **COMO_COLETAR.md** 🚀
**Para começar rapidamente**
- Guia de início rápido
- 3 opções diferentes de coleta
- Estratégias por tempo disponível
- Exemplos práticos
- Troubleshooting comum

👉 **Comece por aqui se você quer começar imediatamente!**

### 2. **lexml_integration_guide.md** 📖
**Documentação técnica completa**
- Sobre o LexML e sua importância
- Arquitetura do sistema
- API SRU do LexML em detalhes
- Como funciona a integração existente
- Estrutura dos dados coletados
- Processamento pós-coleta
- Boas práticas e otimizações

👉 **Leia para entender em profundidade como tudo funciona**

### 3. **QUERIES_AVANCADAS.md** 🔍
**Referência de queries SRU**
- Sintaxe completa do SRU/CQL
- Operadores e campos disponíveis
- 50+ exemplos práticos
- Queries combinadas complexas
- Dicas de performance
- Troubleshooting de queries

👉 **Use como referência quando precisar fazer buscas específicas**

### 4. **PLANO_EXECUCAO.md** 📅
**Roadmap para coleta completa**
- Cronograma detalhado (10 dias)
- Metas e estimativas
- Scripts de automação
- Monitoramento e backup
- Checklist de conclusão
- Estatísticas esperadas

👉 **Siga este plano para coletar TODOS os dados do LexML**

## 🛠️ Ferramentas Disponíveis

### Scripts Python

#### **collect_lexml_data.py**
Script interativo principal com menu de opções:
```bash
python scripts/collect_lexml_data.py
```

**Opções:**
1. Coletar TODAS as leis federais (1988-2024)
2. Coletar leis de um ano específico
3. Coletar projetos de lei recentes
4. Coletar leis sobre um tema
5. Executar pipeline completo
6. Teste rápido

#### **test_lexml_api.sh**
Scripts bash para testar a API REST:
```bash
bash scripts/test_lexml_api.sh
```

### Notebooks Jupyter

#### **lexml_exploration.ipynb**
Notebook interativo para exploração de dados:
```bash
jupyter notebook notebooks/lexml_exploration.ipynb
```

**Conteúdo:**
- Busca básica no LexML
- Análise por tema
- Análise temporal
- Visualizações
- Exportação de dados

## 🎓 Como Usar Este Guia

### Para Iniciantes

1. **Leia:** `COMO_COLETAR.md` (15 min)
2. **Execute:** Teste rápido (5 min)
   ```bash
   python scripts/collect_lexml_data.py
   # Opção 6
   ```
3. **Explore:** Notebook Jupyter (30 min)
   ```bash
   jupyter notebook notebooks/lexml_exploration.ipynb
   ```

### Para Desenvolvimento

1. **Leia:** `lexml_integration_guide.md` (30 min)
2. **Consulte:** `QUERIES_AVANCADAS.md` quando precisar
3. **Desenvolva:** Use os exemplos como base

### Para Produção

1. **Siga:** `PLANO_EXECUCAO.md` (10 dias)
2. **Monitore:** Use scripts de status e backup
3. **Otimize:** Ajuste conforme necessário

## 📊 Estrutura do Projeto

```
voz-da-lei/
├── backend/
│   ├── app/
│   │   ├── integrations/
│   │   │   └── legislative_apis.py    # Cliente LexML
│   │   ├── services/
│   │   │   ├── data_collector.py      # Coleta
│   │   │   ├── text_processor.py      # Processamento
│   │   │   ├── corpus_builder.py      # Corpus QA
│   │   │   ├── embedding_service.py   # Embeddings
│   │   │   └── pipeline_service.py    # Pipeline completo
│   │   └── api/v1/
│   │       ├── data_pipeline.py       # Endpoints
│   │       └── legislation.py         # Consultas
│   └── requirements.txt
├── scripts/
│   ├── collect_lexml_data.py         # Script principal
│   └── test_lexml_api.sh             # Testes API
├── notebooks/
│   └── lexml_exploration.ipynb       # Exploração
└── docs/
    ├── COMO_COLETAR.md              # Guia rápido
    ├── lexml_integration_guide.md   # Documentação completa
    ├── QUERIES_AVANCADAS.md         # Referência de queries
    └── PLANO_EXECUCAO.md            # Roadmap
```

## 🚀 Quick Start (5 minutos)

```bash
# 1. Clone e configure
cd voz-da-lei
source venv/bin/activate

# 2. Inicie o servidor (terminal 1)
cd backend
uvicorn app.main:app --reload

# 3. Teste rápido (terminal 2)
cd voz-da-lei
python scripts/collect_lexml_data.py
# Escolha opção 6 (Teste rápido)

# 4. Verifique os dados
psql -U vozdalei -d vozdalei -c "SELECT COUNT(*) FROM legislations;"

# 5. Teste o chat
cd frontend
npm run dev
# Acesse http://localhost:3000/chat
```

## 📈 Fluxo de Dados

```
LexML API (XML/SRU)
        ↓
 Data Collector
        ↓
    Database
        ↓
 Text Processor (Chunking)
        ↓
 Corpus Builder (QA Pairs)
        ↓
Embedding Service (Vectors)
        ↓
   Search Engine
        ↓
    Chat API
        ↓
    Frontend
```

## 🔧 Configuração

### Variáveis de Ambiente (.env)

```bash
# Database
DATABASE_URL=postgresql://vozdalei:vozdalei123@localhost:5432/vozdalei

# APIs de IA (escolha uma)
GROQ_API_KEY=seu_groq_key_aqui          # Gratuita
OPENAI_API_KEY=seu_openai_key_aqui      # Paga
ANTHROPIC_API_KEY=seu_anthropic_key_aqui # Paga

# LexML (não precisa de key)
LEXML_API_URL=https://www.lexml.gov.br/busca/SRU
```

## 🎯 Casos de Uso

### 1. Pesquisa Acadêmica
```bash
# Coletar leis sobre um tema específico
python scripts/collect_lexml_data.py
# Opção 4 - Tema: "propriedade intelectual"
```

### 2. Análise de Políticas Públicas
```python
# Comparar legislação por período
results = await compare_laws_by_year("educação", [2020, 2021, 2022, 2023])
```

### 3. Assistente Jurídico
```python
# Pipeline completo para chat inteligente
await pipeline.run_full_pipeline(
    source="lexml",
    year=2023,
    tipo_documento="Lei",
    limit=100
)
```

### 4. Monitoramento Legislativo
```python
# Coletar projetos em tramitação
await collector.collect_recent_projects(years=1)
```

## 💡 Dicas Importantes

### Performance
- Use limites razoáveis (100-1000 por vez)
- Adicione delays entre requisições (1-2s)
- Execute coletas longas overnight
- Monitore uso de memória

### Qualidade dos Dados
- Valide dados coletados
- Verifique duplicatas
- Teste pipeline completo antes de coletar tudo
- Faça backups regulares

### Custos
- LexML: **Gratuito** ✅
- Banco de dados: **Local/gratuito** ✅
- APIs de IA:
  - Groq: **Gratuito** ✅
  - OpenAI: Pago (~$0.50/1M tokens)
  - Anthropic: Pago (~$3.00/1M tokens)

## 🆘 Suporte

### Problemas Comuns

**1. "Connection refused"**
→ Servidor não está rodando
→ `uvicorn app.main:app --reload`

**2. "Database não existe"**
→ `createdb -U vozdalei vozdalei`

**3. "Rate limit exceeded"**
→ Adicione delays mais longos
→ Reduza `limit` nas queries

**4. Timeout**
→ Aumente timeout nas requisições
→ Divida coleta em lotes menores

### Onde Encontrar Ajuda

- **Logs:** `backend/logs/app.log`
- **Status da API:** http://localhost:8000/docs
- **Documentação LexML:** https://www.lexml.gov.br
- **Código-fonte:** https://github.com/lexml

## 📊 Estatísticas Esperadas

Após coleta completa:

| Métrica | Quantidade Estimada |
|---------|-------------------|
| Legislações | 100.000 - 200.000 |
| Chunks | 500.000 - 1.000.000 |
| Pares QA | 2.000.000 - 5.000.000 |
| Embeddings | 2.500.000 - 6.000.000 |
| Espaço em Disco | 15-25 GB |
| Tempo Total | 10-15 dias |

## 🎓 Próximos Passos

Após completar a coleta:

1. ✅ **Teste o chat** com perguntas reais
2. ✅ **Valide a qualidade** das respostas
3. ✅ **Otimize prompts** e configurações
4. ✅ **Deploy em produção**
5. ✅ **Configure monitoramento**
6. ✅ **Implemente atualizações automáticas**

## 📞 Contato

- **Projeto:** Voz da Lei
- **GitHub:** [Link do seu repo]
- **Email:** [Seu email]

---

## 🎉 Você está pronto!

Escolha seu caminho:

- **🚀 Iniciante?** → Leia `COMO_COLETAR.md`
- **📖 Quer entender tudo?** → Leia `lexml_integration_guide.md`
- **🔍 Precisa de queries?** → Consulte `QUERIES_AVANCADAS.md`
- **📅 Vai fazer coleta completa?** → Siga `PLANO_EXECUCAO.md`

**Comece agora:**
```bash
python scripts/collect_lexml_data.py
```

Boa coleta! 🎯
