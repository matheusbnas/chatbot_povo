# Queries Avançadas para o LexML

## Sintaxe SRU (Search/Retrieve via URL)

O LexML usa o protocolo SRU com sintaxe CQL (Contextual Query Language).

## Operadores Básicos

| Operador | Uso | Exemplo |
|----------|-----|---------|
| `=` | Igualdade exata | `dc.date="2023"` |
| `!=` | Diferente | `tipoDocumento!="Lei"` |
| `>` | Maior que | `dc.date>"2020"` |
| `<` | Menor que | `dc.date<"2020"` |
| `>=` | Maior ou igual | `dc.date>="2020"` |
| `<=` | Menor ou igual | `dc.date<="2023"` |
| `contains` | Contém | `dc.title contains "educação"` |
| `all` | Todas as palavras | `dc.title all "meio ambiente"` |
| `any` | Qualquer palavra | `dc.title any "saúde educação"` |
| `and` | E lógico | `tipoDocumento="Lei" and dc.date="2023"` |
| `or` | OU lógico | `dc.date="2022" or dc.date="2023"` |
| `not` | Negação | `not dc.title contains "revogada"` |

## Campos Disponíveis

### Campos Dublin Core (dc.*)

- `dc.title` - Título do documento
- `dc.description` - Descrição/ementa
- `dc.date` - Data (formato: YYYY-MM-DD ou YYYY)
- `dc.type` - Tipo de recurso
- `dc.identifier` - Identificador único

### Campos do LexML

- `tipoDocumento` - Tipo de documento (Lei, Projeto de Lei, etc)
- `autoridade` - Autoridade emissora (Senado Federal, etc)
- `localidade` - Localidade (br, sp, rj, etc)
- `facet-tipoDocumento` - Faceta do tipo de documento
- `facet-localidade` - Faceta da localidade
- `facet-autoridade` - Faceta da autoridade
- `urn` - URN do documento

## Exemplos Práticos

### 1. Buscar por Ano

```python
# Leis de 2023
query = 'tipoDocumento="Lei" and dc.date="2023"'

# Leis entre 2020 e 2023
query = 'tipoDocumento="Lei" and dc.date>="2020" and dc.date<="2023"'

# Leis posteriores a 2020
query = 'tipoDocumento="Lei" and dc.date>"2020"'
```

### 2. Buscar por Palavras-Chave

```python
# Título contém "educação"
query = 'dc.title contains "educação"'

# Título ou descrição contém "educação"
query = 'dc.title contains "educação" or dc.description contains "educação"'

# Todas as palavras no título
query = 'dc.title all "meio ambiente sustentável"'

# Qualquer palavra no título
query = 'dc.title any "saúde educação trabalho"'
```

### 3. Buscar por Tipo de Documento

```python
# Apenas leis
query = 'tipoDocumento="Lei"'

# Projetos de lei
query = 'tipoDocumento="Projeto de Lei"'

# Emendas constitucionais
query = 'tipoDocumento="Emenda Constitucional"'

# Decretos
query = 'tipoDocumento="Decreto"'

# Portarias
query = 'tipoDocumento="Portaria"'
```

### 4. Buscar por Autoridade

```python
# Senado Federal
query = 'autoridade="Senado Federal"'

# Câmara dos Deputados
query = 'autoridade="Câmara dos Deputados"'

# Presidência da República
query = 'autoridade="Presidência da República"'

# Assembleia Legislativa de SP
query = 'autoridade="Assembleia Legislativa do Estado de São Paulo"'
```

### 5. Buscar por Localidade

```python
# Federal
query = 'localidade="br"'

# Estado de São Paulo
query = 'localidade="br;sp"'

# Município de São Paulo
query = 'localidade="br;sp;sao.paulo"'

# Estado do Rio de Janeiro
query = 'localidade="br;rj"'
```

### 6. Queries Combinadas

```python
# Leis federais sobre educação de 2023
query = 'tipoDocumento="Lei" and localidade="br" and dc.title contains "educação" and dc.date="2023"'

# Projetos de lei do Senado sobre saúde
query = 'tipoDocumento="Projeto de Lei" and autoridade="Senado Federal" and dc.title contains "saúde"'

# Leis estaduais de SP sobre meio ambiente
query = 'tipoDocumento="Lei" and localidade="br;sp" and dc.title all "meio ambiente"'

# Decretos recentes (últimos 2 anos)
query = 'tipoDocumento="Decreto" and dc.date>="2022"'
```

### 7. Exclusões e Negações

```python
# Leis que NÃO foram revogadas (não contém "revoga" no título)
query = 'tipoDocumento="Lei" and not dc.title contains "revoga"'

# Documentos que NÃO são projetos
query = 'not tipoDocumento="Projeto de Lei"'

# Leis sobre educação mas NÃO sobre ensino superior
query = 'tipoDocumento="Lei" and dc.title contains "educação" and not dc.title contains "ensino superior"'
```

### 8. Buscar por URN

```python
# URN específica
query = 'urn="senado.federal pls 2008 489"'

# Prefixo de URN (todos os documentos do Senado Federal)
query = 'urn all "senado.federal"'

# PLS (Projetos de Lei do Senado) de 2008
query = 'urn all "senado.federal pls 2008"'
```

## Exemplos Completos em Python

### Exemplo 1: Buscar Leis sobre COVID-19

```python
async def search_covid_laws():
    from app.integrations.legislative_apis import lexml_client
    
    query = '''
        tipoDocumento="Lei" and 
        (dc.title contains "covid" or 
         dc.title contains "pandemia" or 
         dc.title contains "coronavírus") and 
        dc.date>="2020"
    '''
    
    result = await lexml_client.search(
        query=query,
        maximum_records=100
    )
    
    return result

# Executar
results = await search_covid_laws()
print(f"Encontradas {results['total']} leis sobre COVID-19")
```

### Exemplo 2: Comparar Leis por Ano

```python
async def compare_laws_by_year(theme, years):
    results = {}
    
    for year in years:
        query = f'tipoDocumento="Lei" and dc.title contains "{theme}" and dc.date="{year}"'
        
        result = await lexml_client.search(query=query, maximum_records=1000)
        results[year] = result['total']
    
    return results

# Executar
theme = "educação"
years = [2020, 2021, 2022, 2023, 2024]
comparison = await compare_laws_by_year(theme, years)

for year, count in comparison.items():
    print(f"{year}: {count} leis sobre {theme}")
```

### Exemplo 3: Buscar Leis por Múltiplos Temas

```python
async def search_by_themes(themes, year=None):
    results = {}
    
    for theme in themes:
        query = f'tipoDocumento="Lei" and dc.title contains "{theme}"'
        
        if year:
            query += f' and dc.date="{year}"'
        
        result = await lexml_client.search(query=query, maximum_records=100)
        results[theme] = {
            'total': result['total'],
            'documents': result['records'][:5]  # Primeiros 5
        }
    
    return results

# Executar
themes = ["educação", "saúde", "trabalho", "meio ambiente"]
results = await search_by_themes(themes, year=2023)

for theme, data in results.items():
    print(f"\n{theme}: {data['total']} leis")
    for doc in data['documents']:
        print(f"  - {doc['title']}")
```

### Exemplo 4: Timeline de Legislação

```python
async def create_legislation_timeline(start_year, end_year, doc_type="Lei"):
    timeline = []
    
    for year in range(start_year, end_year + 1):
        query = f'tipoDocumento="{doc_type}" and dc.date="{year}"'
        
        result = await lexml_client.search(query=query, maximum_records=1000)
        
        timeline.append({
            'year': year,
            'count': result['total'],
            'sample': result['records'][:3]
        })
    
    return timeline

# Executar
timeline = await create_legislation_timeline(2020, 2024)

print("Timeline de Leis (2020-2024):")
for item in timeline:
    print(f"\n{item['year']}: {item['count']} leis")
    print("Exemplos:")
    for doc in item['sample']:
        print(f"  - {doc['title']}")
```

### Exemplo 5: Análise por Estado

```python
async def analyze_state_laws(state_code):
    """
    Analisar leis de um estado específico
    
    Códigos: br;sp (SP), br;rj (RJ), br;mg (MG), etc
    """
    
    # Total de leis
    query = f'tipoDocumento="Lei" and localidade="{state_code}"'
    total_result = await lexml_client.search(query=query, maximum_records=1000)
    
    # Leis recentes (últimos 5 anos)
    current_year = datetime.now().year
    recent_query = f'{query} and dc.date>="{current_year - 5}"'
    recent_result = await lexml_client.search(query=recent_query, maximum_records=1000)
    
    # Por tema
    themes = ["educação", "saúde", "segurança"]
    by_theme = {}
    
    for theme in themes:
        theme_query = f'{query} and dc.title contains "{theme}"'
        theme_result = await lexml_client.search(query=theme_query, maximum_records=100)
        by_theme[theme] = theme_result['total']
    
    return {
        'state': state_code,
        'total_laws': total_result['total'],
        'recent_laws': recent_result['total'],
        'by_theme': by_theme
    }

# Executar para São Paulo
sp_analysis = await analyze_state_laws("br;sp")

print(f"Análise de Leis - São Paulo")
print(f"Total: {sp_analysis['total_laws']}")
print(f"Recentes (últimos 5 anos): {sp_analysis['recent_laws']}")
print(f"Por tema:")
for theme, count in sp_analysis['by_theme'].items():
    print(f"  - {theme}: {count}")
```

### Exemplo 6: Buscar Leis Complementares

```python
async def search_complementary_laws(theme=None):
    query = 'tipoDocumento="Lei Complementar"'
    
    if theme:
        query += f' and dc.title contains "{theme}"'
    
    result = await lexml_client.search(query=query, maximum_records=100)
    
    return result

# Executar
comp_laws = await search_complementary_laws(theme="tributário")
print(f"Leis Complementares sobre tributário: {comp_laws['total']}")
```

### Exemplo 7: Buscar Alterações de Lei

```python
async def search_law_amendments(original_law_number):
    """
    Buscar leis que alteram uma lei específica
    """
    query = f'tipoDocumento="Lei" and dc.title contains "altera" and dc.title contains "{original_law_number}"'
    
    result = await lexml_client.search(query=query, maximum_records=100)
    
    return result

# Executar
amendments = await search_law_amendments("8.112")
print(f"Leis que alteram a Lei 8.112: {amendments['total']}")
```

### Exemplo 8: Buscar por Múltiplas Autoridades

```python
async def search_by_authorities(authorities, year=None):
    results = {}
    
    for authority in authorities:
        query = f'autoridade="{authority}"'
        
        if year:
            query += f' and dc.date="{year}"'
        
        result = await lexml_client.search(query=query, maximum_records=100)
        results[authority] = result['total']
    
    return results

# Executar
authorities = [
    "Senado Federal",
    "Câmara dos Deputados",
    "Presidência da República"
]

results = await search_by_authorities(authorities, year=2023)

print("Documentos por autoridade (2023):")
for auth, count in results.items():
    print(f"  {auth}: {count}")
```

## Dicas Avançadas

### 1. Paginação

```python
async def paginate_results(query, total_needed=500):
    """Coletar mais de 100 resultados usando paginação"""
    all_records = []
    start_record = 1
    max_per_page = 100
    
    while len(all_records) < total_needed:
        result = await lexml_client.search(
            query=query,
            start_record=start_record,
            maximum_records=max_per_page
        )
        
        records = result.get('records', [])
        if not records:
            break
        
        all_records.extend(records)
        start_record += max_per_page
        
        # Respeitar rate limit
        await asyncio.sleep(0.5)
    
    return all_records[:total_needed]
```

### 2. Busca Fuzzy (Aproximada)

```python
# Usar variações ortográficas
query = '''
    dc.title contains "educação" or
    dc.title contains "educacao" or
    dc.title contains "educaçao"
'''
```

### 3. Filtros Complexos

```python
# Leis sobre tecnologia, mas não sobre telecomunicações
query = '''
    tipoDocumento="Lei" and
    (dc.title contains "tecnologia" or dc.title contains "digital") and
    not dc.title contains "telecomunicações"
'''
```

## Troubleshooting de Queries

### Query retorna 0 resultados

1. Verifique a sintaxe
2. Teste partes da query separadamente
3. Verifique se os valores existem (ex: autoridade exata)

### Query muito lenta

1. Reduza `maximum_records`
2. Adicione mais filtros específicos
3. Use paginação

### Caracteres especiais

```python
# Escapar aspas
query = 'dc.title contains "lei\\"complementar\\""'

# OU usar aspas simples/duplas alternadas
query = "dc.title contains \"lei 'especial'\""
```

## Recursos

- **Documentação SRU:** http://www.loc.gov/standards/sru/
- **LexML:** https://www.lexml.gov.br
- **Código do LexML:** https://github.com/lexml
