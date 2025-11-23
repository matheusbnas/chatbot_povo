# Endpoints de Legislação - API do Senado

## Métodos Implementados

Todos os endpoints oficiais de Legislação da API do Senado foram implementados no `SenadoAPIClient`.

### 1. Detalhes por Código

```python
await senado_client.legislacao_por_codigo(codigo: str) -> Dict[str, Any]
```

**Endpoint**: `GET /dadosabertos/legislacao/{codigo}`

**Descrição**: Obter detalhes de uma Norma Jurídica pelo código

**Exemplo**:

```python
norma = await senado_client.legislacao_por_codigo("123456")
```

---

### 2. Detalhes por Identificação

```python
await senado_client.legislacao_por_identificacao(
    tipo: str,
    numdata: str,
    anoseq: str
) -> Dict[str, Any]
```

**Endpoint**: `GET /dadosabertos/legislacao/{tipo}/{numdata}/{anoseq}`

**Descrição**: Obter detalhes de uma Norma Jurídica pela identificação (sigla / número / ano)

**Parâmetros**:

- `tipo`: Tipo/sigla da norma (ex: LEI, DEC, MPV)
- `numdata`: Número/data da norma
- `anoseq`: Ano/sequência da norma

**Exemplo**:

```python
norma = await senado_client.legislacao_por_identificacao(
    tipo="LEI",
    numdata="13979",
    anoseq="2020"
)
```

---

### 3. Classes de Legislação

```python
await senado_client.legislacao_classes() -> List[Dict[str, Any]]
```

**Endpoint**: `GET /dadosabertos/legislacao/classes`

**Descrição**: Listar Classificação de Normas Jurídicas, Projetos e Pronunciamentos

**Exemplo**:

```python
classes = await senado_client.legislacao_classes()
```

---

### 4. Pesquisa de Normas Federais

```python
await senado_client.legislacao_lista(
    ano: Optional[int] = None,
    tipo: Optional[str] = None,
    numero: Optional[str] = None,
    data_inicio: Optional[str] = None,  # YYYYMMDD
    data_fim: Optional[str] = None,  # YYYYMMDD
    pagina: Optional[int] = None,
    quantidade: Optional[int] = None
) -> Dict[str, Any]
```

**Endpoint**: `GET /dadosabertos/legislacao/lista`

**Descrição**: Pesquisar Normas Federais

**Parâmetros**:

- `ano`: Ano da norma
- `tipo`: Tipo da norma (LEI, DEC, MPV, etc)
- `numero`: Número da norma
- `data_inicio`: Data de início (formato YYYYMMDD)
- `data_fim`: Data de fim (formato YYYYMMDD)
- `pagina`: Número da página
- `quantidade`: Quantidade de resultados por página

**Exemplo**:

```python
# Buscar leis de 2024
resultado = await senado_client.legislacao_lista(ano=2024, quantidade=10)

# Buscar leis de um tipo específico
resultado = await senado_client.legislacao_lista(tipo="LEI", quantidade=5)
```

---

### 5. Pesquisa de Termos

```python
await senado_client.legislacao_termos(
    termo: Optional[str] = None,
    tipo: Optional[str] = None
) -> List[Dict[str, Any]]
```

**Endpoint**: `GET /dadosabertos/legislacao/termos`

**Descrição**: Pesquisar Termos do Catálogo

**Parâmetros**:

- `termo`: Termo a pesquisar
- `tipo`: Tipo de termo (opcional)

**Exemplo**:

```python
termos = await senado_client.legislacao_termos(termo="educação")
```

---

### 6. Tipos de Declaração - Detalhes

```python
await senado_client.legislacao_tipos_declaracao_detalhe() -> List[Dict[str, Any]]
```

**Endpoint**: `GET /dadosabertos/legislacao/tiposdeclaracao/detalhe`

**Descrição**: Listar Detalhes de Declaração

**Exemplo**:

```python
tipos = await senado_client.legislacao_tipos_declaracao_detalhe()
```

---

### 7. Tipos de Norma

```python
await senado_client.legislacao_tipos_norma() -> List[Dict[str, Any]]
```

**Endpoint**: `GET /dadosabertos/legislacao/tiposNorma`

**Descrição**: Listar Tipos de Norma disponíveis

**Exemplo**:

```python
tipos = await senado_client.legislacao_tipos_norma()
```

---

### 8. Tipos de Publicação

```python
await senado_client.legislacao_tipos_publicacao() -> List[Dict[str, Any]]
```

**Endpoint**: `GET /dadosabertos/legislacao/tiposPublicacao`

**Descrição**: Listar Tipos de Publicação disponíveis

**Exemplo**:

```python
tipos = await senado_client.legislacao_tipos_publicacao()
```

---

### 9. Tipos Vide (Declaração)

```python
await senado_client.legislacao_tipos_vide() -> List[Dict[str, Any]]
```

**Endpoint**: `GET /dadosabertos/legislacao/tiposVide`

**Descrição**: Listar Tipos de Declaração (vide)

**Exemplo**:

```python
tipos = await senado_client.legislacao_tipos_vide()
```

---

### 10. Detalhes por URN

```python
await senado_client.legislacao_por_urn(urn: str) -> Dict[str, Any]
```

**Endpoint**: `GET /dadosabertos/legislacao/urn`

**Descrição**: Obter detalhes de uma Norma Jurídica pela URN (Uniform Resource Name)

**Parâmetros**:

- `urn`: URN da norma jurídica

**Exemplo**:

```python
norma = await senado_client.legislacao_por_urn("urn:lex:br:federal:lei:2020:13979")
```

---

## Características Comuns

Todos os métodos implementados:

- ✅ Usam o método auxiliar `_make_request()` que implementa:

  - Rate limiting automático (máximo 10 req/s)
  - Retry automático para erros HTTP 429 e 503
  - Tratamento adequado de erros HTTP

- ✅ Retornam estruturas de dados consistentes:

  - Dicionários para detalhes individuais
  - Listas para coleções
  - Tratamento de diferentes formatos de resposta da API

- ✅ Incluem tratamento de erros robusto:
  - Logging de erros
  - Retorno de valores padrão ({} ou []) em caso de erro
  - Não interrompem a execução em caso de falha

## Testes

Execute o script de teste para validar os endpoints:

```bash
python backend/tests/test_legislacao_api.py
```

## Documentação Oficial

- **API Docs**: https://legis.senado.leg.br/dadosabertos/v3/api-docs
- **Código**: `backend/app/integrations/senado_api.py`
