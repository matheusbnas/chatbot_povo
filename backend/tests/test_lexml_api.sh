#!/bin/bash
# Scripts para testar coleta de dados do LexML via API REST

# Configuração
API_URL="http://localhost:8000/api/v1"

echo "================================"
echo "SCRIPTS DE COLETA - VOZ DA LEI"
echo "================================"
echo ""

# Função para exibir resultado
show_result() {
    echo "Resposta:"
    echo "$1" | python3 -m json.tool
    echo ""
}

# 1. Coletar leis de 2023
echo "1. Coletando leis de 2023 (limite: 20)..."
response=$(curl -s -X POST "$API_URL/data/collect/lexml?year=2023&tipo_documento=Lei&limit=20")
show_result "$response"

# 2. Coletar projetos de lei de 2024
echo "2. Coletando projetos de lei de 2024 (limite: 20)..."
response=$(curl -s -X POST "$API_URL/data/collect/lexml?year=2024&tipo_documento=Projeto%20de%20Lei&limit=20")
show_result "$response"

# 3. Executar pipeline completo
echo "3. Executando pipeline completo para leis de 2023 (limite: 10)..."
response=$(curl -s -X POST "$API_URL/data/pipeline/run?source=lexml&year=2023&tipo_documento=Lei&limit=10")
show_result "$response"

# 4. Verificar legislações em destaque
echo "4. Buscando legislações em destaque..."
response=$(curl -s -X GET "$API_URL/legislation/trending?limit=10")
show_result "$response"

# 5. Buscar no LexML por palavras-chave
echo "5. Buscando leis sobre 'educação'..."
response=$(curl -s -X GET "$API_URL/legislation/lexml/by-keywords?keywords=educa%C3%A7%C3%A3o&limit=5")
show_result "$response"

# 6. Buscar projetos de lei
echo "6. Buscando projetos de lei do ano atual..."
response=$(curl -s -X GET "$API_URL/legislation/lexml/projects?year=$(date +%Y)&limit=5")
show_result "$response"

# 7. Verificar status de um job
echo "7. Verificando status do job 1..."
response=$(curl -s -X GET "$API_URL/data/jobs/1")
show_result "$response"

echo "Testes concluídos!"
