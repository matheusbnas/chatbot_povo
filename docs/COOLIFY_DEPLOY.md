# 🚀 Deploy no Coolify - Voz da Lei

Guia passo a passo para fazer deploy do projeto no **Coolify**.

## 📋 Pré-requisitos

1. **Coolify instalado e rodando** (self-hosted ou cloud)
2. **Acesso ao painel do Coolify**
3. **Repositório Git**: https://github.com/matheusbnas/chatbot_voz_da_lei

## 🎯 Passo a Passo

### 1. Criar Aplicação Backend

1. No painel do Coolify, clique em **"New Resource"** → **"Application"**
2. Escolha **"Git Repository"**
3. Configure:
   - **Repository URL**: `https://github.com/matheusbnas/chatbot_voz_da_lei`
   - **Branch**: `main`
   - **Build Pack**: `Dockerfile`
   - **Base Directory**: `backend/` ⚠️ **IMPORTANTE**: Use `backend/` como base!
   - **Dockerfile Location**: `Dockerfile` (relativo ao Base Directory)
   - **Docker Build Stage Target**: `production`
   - **Port**: `8080` (porta interna do container)
   - **Name**: `vozdalei-backend` (ou outro nome de sua preferência)

### 2. Configurar Network do Backend ⚠️ **CRÍTICO**

Na seção **"Configuration"** → **"Network"** do backend:

**⚠️ CONFIGURAÇÃO CORRETA DE PORTAS:**

- **Ports Exposes**: `8080` (porta interna do container)
- **Ports Mappings**: `8080:8080` ⚠️ **IMPORTANTE**: Deve mapear porta interna 8080 para externa 8080

**❌ ERRADO:** `3000:3000` (não funciona, pois o backend escuta na porta 8080)

**✅ CORRETO:** `8080:8080` (mapeia corretamente a porta interna)

**Nota:** Se quiser usar outra porta externa, use `8080:PORTA_EXTERNA` (ex: `8080:3000`)

### 3. Configurar Variáveis de Ambiente do Backend

#### Opção A: Importar de Arquivo .env (Recomendado) ⚡

**Método Rápido - Copiar e Colar:**

1. **Crie seu arquivo `.env` localmente:**

   ```bash
   cd backend
   cp .env.coolify.example .env
   # Edite o .env com suas configurações reais
   ```

2. **Use o script para formatar:**

   ```bash
   # Linux/Mac:
   chmod +x scripts/import-env-to-coolify.sh
   ./scripts/import-env-to-coolify.sh backend/.env

   # Windows (PowerShell):
   .\scripts\import-env-to-coolify.ps1 backend\.env
   ```

3. **No Coolify:**
   - Vá em **"Environment Variables"** do backend
   - Clique em **"Add"** ou use o campo de texto grande
   - **Cole todas as linhas de uma vez** (o Coolify aceita múltiplas linhas)
   - Clique em **"Save"**

**💡 Dica:** O Coolify aceita múltiplas variáveis coladas de uma vez! Basta colar o conteúdo do arquivo `.env`.

#### Opção B: Adicionar Manualmente (Uma por Uma)

Se preferir adicionar manualmente, use estas variáveis:

```env
# Database (use o serviço PostgreSQL do Coolify ou externo)
DATABASE_URL=postgresql://vozdalei:SUA_SENHA@postgres:5432/vozdalei_bd

# Redis (use o serviço Redis do Coolify ou externo)
REDIS_URL=redis://:SUA_SENHA@redis:6379

# API Keys
GROQ_API_KEY=sua_chave_groq_aqui
OPENAI_API_KEY=sua_chave_openai_aqui

# Security
SECRET_KEY=GERE_UMA_CHAVE_SECRETA_FORTE_AQUI
DEBUG=false
CORS_ORIGINS=https://chatbot-voz-da-lei.vercel.app,https://*.vercel.app,https://seudominio.com
```

**⚠️ IMPORTANTE**:

- Gere `SECRET_KEY` com: `openssl rand -hex 32`
- Se usar serviços do Coolify, o host será o nome do serviço (ex: `postgres`, `redis`)
- **CORS_ORIGINS**: Se o frontend estiver no Vercel, adicione o domínio do Vercel na lista
- **No Coolify, você pode colar múltiplas linhas de uma vez!** Basta copiar todo o conteúdo do `.env` e colar

### 4. Configurar Build do Backend

Na seção **"General"** → **"Build"**:

- **Base Directory**: `/` (raiz do projeto)
- **Dockerfile Location**: `backend/Dockerfile`
- **Docker Build Stage Target**: `production` ⚠️ **IMPORTANTE**: Preencha este campo!

**Nota**: O Coolify vai fazer o build a partir da raiz, mas o Dockerfile está em `backend/`, então o build context será a pasta `backend/`.

### 5. Criar Serviço PostgreSQL (se não tiver)

1. **New Resource** → **"Database"** → **"PostgreSQL"**
2. Configure:
   - **Name**: `postgres` (importante para o DATABASE_URL)
   - **Database**: `vozdalei_bd`
   - **User**: `vozdalei`
   - **Password**: (senha forte)
3. Anote a senha para usar no `DATABASE_URL` do backend

### 6. Criar Serviço Redis (se não tiver)

1. **New Resource** → **"Database"** → **"Redis"**
2. Configure:
   - **Name**: `redis` (importante para o REDIS_URL)
   - **Password**: (senha forte)
3. Anote a senha para usar no `REDIS_URL` do backend

### 7. Criar Aplicação Frontend

1. **New Resource** → **"Application"**
2. Escolha **"Git Repository"**
3. Configure:
   - **Repository URL**: `https://github.com/matheusbnas/chatbot_voz_da_lei`
   - **Branch**: `main`
   - **Build Pack**: `Dockerfile`
   - **Base Directory**: `frontend/` ⚠️ **IMPORTANTE**: Use `frontend/` como base!
   - **Dockerfile Location**: `Dockerfile` (relativo ao Base Directory)
   - **Docker Build Stage Target**: `production`
   - **Port**: `3002`
   - **Name**: `vozdalei-frontend` (ou outro nome de sua preferência)

### 8. Configurar Network do Frontend

Na seção **"Configuration"** → **"Network"** do frontend:

- **Ports Exposes**: `3002` (porta interna do container)
- **Ports Mappings**: `3002:3002` (mapeia porta interna 3002 para externa 3002)

### 9. Configurar Variáveis de Ambiente do Frontend

#### Opção A: Importar de Arquivo .env (Recomendado) ⚡

1. **Crie seu arquivo `.env` localmente:**

   ```bash
   cd frontend
   cp .env.coolify.example .env
   # Edite o .env com a URL real do backend
   ```

2. **No Coolify:**
   - Vá em **"Environment Variables"** do frontend
   - **Cole todo o conteúdo do arquivo `.env` de uma vez**
   - O Coolify aceita múltiplas linhas!
   - Clique em **"Save"**

#### Opção B: Adicionar Manualmente

Adicione estas variáveis:

```env
NEXT_PUBLIC_API_URL=http://SEU_IP:8080
NODE_ENV=production
PORT=3002
```

**💡 Dica:** Você pode copiar e colar múltiplas variáveis de uma vez no Coolify!

**⚠️ IMPORTANTE para Frontend no Vercel:**

Se o frontend estiver no **Vercel** (não no Coolify), você precisa:

1. **Descobrir a URL do backend:**

   - Se usar IP: `http://31.97.16.142:8080` (ou a porta externa configurada)
   - Se tiver domínio: `https://backend.seudominio.com`

2. **Configurar no Vercel:**

   - Vá em **Settings** → **Environment Variables**
   - Adicione: `NEXT_PUBLIC_API_URL` = URL do backend
   - Faça **redeploy** do frontend

3. **Testar a URL do backend:**
   ```bash
   curl http://SEU_IP:8080/health
   # Deve retornar: {"status": "healthy"}
   ```

### 10. Configurar Build do Frontend

Na seção **"General"** → **"Build"**:

- **Base Directory**: `/` (raiz do projeto)
- **Dockerfile Location**: `frontend/Dockerfile`
- **Docker Build Stage Target**: `production` ⚠️ **IMPORTANTE**: Preencha este campo!

### 11. Configurar Domínio (Opcional)

Para cada aplicação (backend e frontend):

1. Vá em **"Settings"** → **"Domains"**
2. Adicione seu domínio:
   - Backend: `api.seudominio.com` ou `backend.seudominio.com`
   - Frontend: `seudominio.com` ou `www.seudominio.com`
3. O Coolify gerencia SSL automaticamente (Let's Encrypt)

### 12. Deploy

1. Clique em **"Deploy"** em cada aplicação
2. O Coolify irá:
   - Clonar o repositório
   - Fazer build da imagem Docker
   - Iniciar o container
   - Configurar SSL (se tiver domínio)

### 13. Verificar Deploy

**Backend:**

```bash
# Health check
curl https://api.seudominio.com/health

# Docs
curl https://api.seudominio.com/docs
```

**Frontend:**

```bash
curl https://seudominio.com
```

## 🔧 Configurações Avançadas

### Health Checks

1. Vá em **"Configuration"** → **"Healthcheck"**
2. Configure:
   - **Backend**:
     - **Path**: `/health`
     - **Port**: `8080`
   - **Frontend**:
   - **Path**: `/`
   - **Port**: `3002`

### Custom Docker Options (Opcional)

Se precisar de opções customizadas (como no seu caso), vá em **"General"** → **"Build"** → **"Custom Docker Options"**:

Para backend (se necessário):

```
--build-arg BUILD_TARGET=production
```

**Nota**: Geralmente não é necessário, pois o target já está configurado.

### Recursos (Resources)

Configure limites de recursos se necessário:

- **CPU**: 1-2 cores
- **RAM**: 512MB - 1GB
- **Storage**: Conforme necessário

### Variáveis de Ambiente Sensíveis

Use **"Secrets"** do Coolify para variáveis sensíveis:

1. Vá em **"Settings"** → **"Secrets"**
2. Adicione secrets (ex: `GROQ_API_KEY`, `SECRET_KEY`)
3. Use nos environment variables como: `${{ secrets.GROQ_API_KEY }}`

## 🔄 Atualizar Aplicação

1. Faça push para o repositório Git
2. No Coolify, clique em **"Redeploy"** na aplicação
3. Ou configure **"Auto Deploy"** para deploy automático em cada push

## 📊 Monitoramento

O Coolify fornece:

- **Logs** em tempo real
- **Métricas** de CPU/RAM
- **Status** dos containers
- **Health checks** automáticos

## 🐛 Troubleshooting

### Build Falha

1. Verifique os logs de build no Coolify
2. Confirme que o Dockerfile está correto
3. Verifique se todas as dependências estão no repositório

### Aplicação não inicia

1. Verifique os logs da aplicação
2. Confirme variáveis de ambiente
3. Verifique conexão com PostgreSQL/Redis

### Erro de conexão com banco

1. Confirme que o serviço PostgreSQL está rodando
2. Verifique o `DATABASE_URL` (host deve ser o nome do serviço)
3. Confirme usuário, senha e nome do banco

### Frontend não conecta ao backend

**Sintomas:** Erro CORS ou "Network Error" no console

**Soluções:**

1. **Verificar Ports Mappings do Backend:**

   - Deve ser `8080:8080` (não `3000:3000`)
   - Se estiver errado, corrija e reinicie o backend

2. **Verificar URL do Backend:**

   - Teste: `curl http://SEU_IP:8080/health`
   - Deve retornar: `{"status": "healthy"}`

3. **Verificar `NEXT_PUBLIC_API_URL`:**

   - No Coolify (frontend): Verifique se está configurado
   - No Vercel: Vá em **Settings** → **Environment Variables**
   - Deve ser a URL pública do backend (não `localhost`)
   - Exemplo: `http://31.97.16.142:8080` ou `https://backend.seudominio.com`

4. **Verificar CORS no Backend:**

   - No Coolify (backend): Verifique `CORS_ORIGINS`
   - Deve incluir o domínio do frontend (Vercel ou Coolify)
   - Exemplo: `https://chatbot-voz-da-lei.vercel.app,https://*.vercel.app`

5. **Fazer Redeploy:**
   - Após mudar variáveis, faça redeploy do frontend
   - No Vercel: **Deployments** → **Redeploy**
   - No Coolify: Clique em **Redeploy**

## ✅ Checklist

### Backend

- [ ] Backend criado no Coolify
- [ ] **Base Directory**: `backend/` configurado
- [ ] **Dockerfile Location**: `Dockerfile` configurado
- [ ] **Docker Build Stage Target**: `production` preenchido
- [ ] **Ports Exposes**: `8080` configurado
- [ ] **Ports Mappings**: `8080:8080` configurado ⚠️ **CRÍTICO**
- [ ] PostgreSQL configurado (ou serviço externo)
- [ ] Redis configurado (ou serviço externo)
- [ ] Variáveis de ambiente configuradas (incluindo CORS_ORIGINS)
- [ ] CORS_ORIGINS inclui domínio do frontend (Vercel ou Coolify)
- [ ] Backend respondendo em `/health`
- [ ] URL pública do backend identificada

### Frontend (Coolify)

- [ ] Frontend criado no Coolify
- [ ] **Base Directory**: `frontend/` configurado
- [ ] **Dockerfile Location**: `Dockerfile` configurado
- [ ] **Docker Build Stage Target**: `production` preenchido
- [ ] **Ports Exposes**: `3002` configurado
- [ ] **Ports Mappings**: `3002:3002` configurado
- [ ] **NEXT_PUBLIC_API_URL** configurado com URL pública do backend
- [ ] Frontend acessível
- [ ] Frontend conectando ao backend

### Frontend (Vercel) - Se usar Vercel

- [ ] Frontend conectado ao repositório no Vercel
- [ ] **Root Directory**: `frontend` configurado no Vercel
- [ ] **NEXT_PUBLIC_API_URL** configurado no Vercel (Settings → Environment Variables)
- [ ] URL do backend testada e funcionando
- [ ] Redeploy feito após configurar variáveis
- [ ] Frontend acessível no Vercel
- [ ] Frontend conectando ao backend (sem erros CORS)

## 📝 Notas Importantes

1. **Repositório**: https://github.com/matheusbnas/chatbot_voz_da_lei
2. **Porta Backend**: `8080` (interna do container)
3. **Porta Frontend**: `3002` (interna do container)
4. **Banco de Dados**: `vozdalei_bd`
5. **Dockerfile Target**: Use `production` para ambos
6. **Base Directory**: `/` (raiz do projeto)
7. **Dockerfile Location Backend**: `backend/Dockerfile`
8. **Dockerfile Location Frontend**: `frontend/Dockerfile`

## ⚠️ Problemas Comuns

### Build Context

Se o build falhar com erro de arquivo não encontrado:

**Solução**: O Coolify precisa que o Dockerfile esteja configurado corretamente:

- **Base Directory**: `backend/` ou `frontend/` (pasta do serviço)
- **Dockerfile Location**: `Dockerfile` (relativo ao Base Directory)

O Dockerfile já está configurado para usar o contexto correto (`COPY . .` dentro da pasta backend/frontend).

### Ports Mappings Incorretos

**Erro:** Backend não acessível ou frontend não conecta

**Sintomas:**

- Erro "Connection refused"
- Erro CORS
- Frontend tenta `localhost:8000`

**Solução:**

1. **Backend:**

   - **Ports Exposes**: `8080`
   - **Ports Mappings**: `8080:8080` (não `3000:3000`)

2. **Frontend:**

   - **Ports Exposes**: `3002`
   - **Ports Mappings**: `3002:3002`

3. **Verificar URL:**
   - Teste: `curl http://SEU_IP:8080/health`
   - Use esta URL no `NEXT_PUBLIC_API_URL`

### Frontend no Vercel não conecta ao Backend

**Sintomas:** Erro CORS ou Network Error

**Solução:**

1. **No Coolify (Backend):**

   - Adicione `CORS_ORIGINS` com domínio do Vercel
   - Exemplo: `https://chatbot-voz-da-lei.vercel.app,https://*.vercel.app`
   - Reinicie o backend

2. **No Vercel (Frontend):**

   - Vá em **Settings** → **Environment Variables**
   - Adicione `NEXT_PUBLIC_API_URL` = URL pública do backend
   - **NÃO use** `localhost:8000` - use a URL pública!
   - Faça **redeploy** do frontend

3. **Testar:**
   - Acesse o frontend no Vercel
   - Abra o Console do navegador (F12)
   - Verifique se não há erros CORS

---

**Boa sorte com o deploy no Coolify! 🚀**
