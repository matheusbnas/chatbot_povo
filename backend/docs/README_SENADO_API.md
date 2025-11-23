# API do Senado Federal - Fonte Oficial e Confiável

## Documentação Oficial

- **URL da Documentação**: https://legis.senado.leg.br/dadosabertos/v3/api-docs
- **API Base**: https://legis.senado.leg.br/dadosabertos
- **Versão da API**: 4.0.3.52 (conforme documentação oficial)

## Confiabilidade

Esta é a **API oficial de Dados Abertos Legislativos do Senado Federal e do Congresso Nacional**, fornecida pelo próprio Senado Federal. É uma fonte **100% confiável** para dados legislativos.

### Características

- ✅ **Acesso público**: Não requer autenticação
- ✅ **Fonte oficial**: Fornecida pelo Senado Federal
- ✅ **Documentação completa**: Disponível em formato OpenAPI 3.1.0
- ✅ **Dados atualizados**: Informações em tempo real do processo legislativo

## Limitações de Requisições

Conforme a documentação oficial, a API implementa as seguintes limitações:

1. **Rate Limiting**: 
   - Máximo de **10 requisições por segundo**
   - Requisições acima deste limite retornam **HTTP 429 (Too Many Requests)**

2. **Horários de Pico**:
   - Evitar requisições em horários arredondados (00:00:00, 01:00:00, etc)
   - Podem causar picos de acesso simultâneo

3. **Alta Demanda**:
   - Em momentos de muita demanda, pode retornar **HTTP 503 (Service Unavailable)**

## Implementação no Projeto

O cliente `SenadoAPIClient` em `backend/app/integrations/senado_api.py` implementa:

- ✅ Rate limiting automático (máximo 10 req/s)
- ✅ Retry automático para erros 429 e 503
- ✅ Tratamento adequado de erros HTTP
- ✅ Fallback para endpoints alternativos quando necessário

## Endpoints Principais

### Normas (Leis, Decretos, etc)
- `GET /norma/listar` - Listar normas
- `GET /norma/{codigo}` - Detalhes de uma norma
- `GET /norma/{codigo}/texto` - Texto completo da norma

### Matérias (Projetos de Lei)
- `GET /materia/pesquisa/lista` - Listar matérias
- `GET /materia/{codigo}` - Detalhes de uma matéria
- `GET /materia/{codigo}/texto` - Texto completo da matéria
- `GET /materia/{codigo}/tramitacao` - Tramitação da matéria

### Processos Legislativos
- `GET /processo/{id}` - Detalhes de um processo
- `GET /processo/{id}/eventos` - Eventos do processo
- `GET /processo/{id}/documentos` - Documentos do processo

### Votações
- `GET /votacaoComissao/materia/{sigla}/{numero}/{ano}` - Votações em comissão
- `GET /votacaoPlenario/{sigla}/{numero}/{ano}` - Votações no plenário

## Formatos Disponíveis

A API suporta múltiplos formatos de saída:

- **application/json** (padrão usado no projeto)
- **application/xml**
- **text/csv**

Para escolher o formato, adicione o cabeçalho HTTP `Accept` ou o sufixo do formato na URL (ex: `.json`, `.xml`, `.csv`).

## Serviços Depreciados

Alguns serviços podem estar marcados como `Deprecated` na documentação. Quando isso acontecer, a API retorna os seguintes cabeçalhos HTTP:

- `Deprecation`: Data de início da depreciação
- `Sunset`: Data da desativação completa
- `Link`: URL do serviço substituto

O cliente verifica esses cabeçalhos e registra avisos quando necessário.

## Uso no Chatbot

O chatbot usa esta API como **fonte oficial e confiável** para:

1. Buscar legislação federal
2. Obter detalhes de projetos de lei
3. Consultar tramitação de matérias
4. Verificar votações
5. Acessar textos completos de normas

Todas as respostas do chatbot que citam dados do Senado Federal são baseadas nesta API oficial.

## Referências

- [Documentação Oficial da API](https://legis.senado.leg.br/dadosabertos/v3/api-docs)
- [Página de Dados Abertos do Senado](https://www12.senado.leg.br/dados-abertos)
- [Cliente Python no Projeto](../app/integrations/senado_api.py)

