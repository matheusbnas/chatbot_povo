# Comparação: collect_senado_data.py vs collect_lexml_data.py

## 📊 Diferenças Principais

### 1. **collect_senado_data.py** - API Específica do Senado

**Fonte:** API REST do Senado Federal (`https://legis.senado.leg.br/dadosabertos`)

**O que coleta:**
- ✅ Normas (leis federais) do Senado
- ✅ Matérias (PLS, PEC, PLC) do Senado
- ✅ **Detalhes de tramitação** (movimentações, status)
- ✅ **Votações** (resultados, votos)
- ✅ **Autores** (senadores que propuseram)
- ✅ **Textos completos** atualizados
- ✅ **Normas relacionadas** (alterações, revogações)

**Vantagens:**
- Dados **mais detalhados** e **atualizados**
- Informações de **tramitação em tempo real**
- **Votações** e resultados
- API moderna (REST/JSON)

**Limitações:**
- Apenas dados do **Senado Federal**
- Não inclui Câmara, estados ou municípios

---

### 2. **collect_lexml_data.py** - Agregador Universal

**Fonte:** LexML - Rede de Informação Legislativa (`https://www.lexml.gov.br`)

**O que coleta:**
- ✅ Leis **federais** (de todas as fontes)
- ✅ Leis **estaduais** (todos os estados)
- ✅ Leis **municipais** (municípios)
- ✅ Projetos de lei (federal, estadual, municipal)
- ✅ Decretos, portarias, etc.
- ✅ Histórico completo (desde 1800s)

**Vantagens:**
- **Cobertura ampla** (federal, estadual, municipal)
- **Histórico completo** (décadas de dados)
- **Busca unificada** em todas as fontes
- Protocolo padrão (SRU)

**Limitações:**
- Menos detalhes de **tramitação**
- Sem informações de **votações**
- Textos completos podem não estar disponíveis
- API mais lenta (XML/SRU)

---

## 🔄 Sobreposição e Redundância

### Há sobreposição? **SIM, mas com diferenças:**

| Aspecto | LexML | Senado |
|---------|-------|--------|
| **Leis do Senado** | ✅ Sim (básico) | ✅ Sim (detalhado) |
| **Tramitação** | ❌ Não | ✅ Sim |
| **Votações** | ❌ Não | ✅ Sim |
| **Autores** | ⚠️ Parcial | ✅ Completo |
| **Texto completo** | ⚠️ Parcial | ✅ Sim |
| **Leis estaduais** | ✅ Sim | ❌ Não |
| **Leis municipais** | ✅ Sim | ❌ Não |
| **Câmara** | ✅ Sim | ❌ Não |

### Exemplo de sobreposição:

**Lei Federal aprovada no Senado:**
- **LexML**: Tem a lei básica (título, data, texto)
- **Senado**: Tem a lei + tramitação + votações + autores + normas relacionadas

---

## ✅ Faz Sentido Ter Ambos?

### **SIM, mas com estratégia:**

### **Cenário 1: Cobertura Completa (Recomendado)**
```
1. LexML → Coletar TUDO (federal, estadual, municipal)
   - Cobertura ampla
   - Histórico completo
   
2. Senado → Complementar com detalhes
   - Tramitação
   - Votações
   - Informações atualizadas
```

### **Cenário 2: Foco em Federal**
```
1. Senado → Dados detalhados do Senado
2. LexML → Apenas para Câmara e outras fontes
```

### **Cenário 3: Foco em Municipal/Estadual**
```
1. LexML → Principal (única fonte)
2. Senado → Apenas para complementar federal
```

---

## 🎯 Recomendações

### **Estratégia Híbrida (Melhor Abordagem):**

1. **Coleta Inicial:**
   - LexML → Coletar tudo (federal, estadual, municipal)
   - Senado → Coletar apenas detalhes de tramitação/votação

2. **Atualização Contínua:**
   - LexML → Atualizar semanalmente (novas leis)
   - Senado → Atualizar diariamente (tramitação, votações)

3. **Deduplicação:**
   - Identificar leis duplicadas (mesmo número/ano)
   - Priorizar dados do Senado quando disponível (mais detalhado)
   - Manter LexML para leis estaduais/municipais

### **Melhorias Sugeridas:**

1. **Criar script unificado** que:
   - Coleta do LexML (cobertura ampla)
   - Complementa com Senado (detalhes)
   - Remove duplicatas inteligentemente

2. **Adicionar campo `canonical_id`** para identificar leis duplicadas:
   - Ex: `"LEI_8112_1990"` (mesma lei, fontes diferentes)

3. **Priorização de fontes:**
   - Senado > LexML (para leis federais)
   - LexML (única opção para estadual/municipal)

---

## 📝 Conclusão

**SIM, faz sentido ter ambos**, mas com estratégia clara:

- **LexML**: Cobertura ampla (todas as fontes)
- **Senado**: Detalhes específicos (tramitação, votações)

**Ideal:** Usar LexML como base e Senado como complemento para detalhes.

