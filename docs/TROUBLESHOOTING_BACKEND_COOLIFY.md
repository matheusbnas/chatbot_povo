# 🐛 Troubleshooting: Backend não responde no Coolify

## ❌ Erro: ERR_EMPTY_RESPONSE

**Sintoma:** Ao acessar `http://31.97.16.142:8080/health`, aparece:
- "Esta página não está funcionando"
- "Nenhum dado foi enviado por 31.97.16.142"
- `ERR_EMPTY_RESPONSE`

## 🔍 Diagnóstico Passo a Passo

### 1. Verificar se o Container está Rodando

**No Coolify:**
1. Vá na aplicação do backend
2. Verifique o status:
   - Deve estar **"Running"** (verde)
   - Se estiver **"Stopped"** ou **"Failed"**, clique em **"Start"** ou **"Restart"**

### 2. Verificar Logs do Backend

**No Coolify:**
1. Vá na aplicação do backend
2. Clique em **"Logs"**
3. Procure por:
   - ✅ **Sucesso:** `Application startup complete` ou `Uvicorn running on http://0.0.0.0:8080`
   - ❌ **Erro:** Mensagens de erro em vermelho

**Erros comuns nos logs:**

**Erro de conexão com banco:**
```
sqlalchemy.exc.OperationalError: could not connect to server
```
**Solução:** Verifique `DATABASE_URL` nas variáveis de ambiente

**Erro de importação:**
```
ModuleNotFoundError: No module named 'app'
```
**Solução:** Verifique se `Base Directory = backend/` está correto

**Erro de porta:**
```
Address already in use
```
**Solução:** Verifique se outra aplicação não está usando a porta 8080

### 3. Verificar Configuração de Network

**No Coolify → Configuration → Network:**

- [ ] **Ports Exposes:** `8080` (porta interna)
- [ ] **Ports Mappings:** `8080:8080` ⚠️ **CRÍTICO** (não `3000:3000`!)

**Se estiver errado:**
1. Corrija para `8080:8080`
2. Salve
3. Reinicie o backend (botão **Restart**)

### 4. Verificar Build

**No Coolify → Configuration → Build:**

- [ ] **Base Directory:** `backend/`
- [ ] **Dockerfile Location:** `Dockerfile`
- [ ] **Docker Build Stage Target:** `production` ⚠️ **OBRIGATÓRIO**

**Se estiver faltando:**
1. Preencha o campo **Docker Build Stage Target** com `production`
2. Salve
3. Faça **Redeploy**

### 5. Verificar Variáveis de Ambiente

**No Coolify → Environment Variables:**

Verifique se estão configuradas:
- [ ] `DATABASE_URL` (obrigatório)
- [ ] `OPENAI_API_KEY` ou `GROQ_API_KEY` (pelo menos uma)
- [ ] `SECRET_KEY` (obrigatório)
- [ ] `CORS_ORIGINS` (recomendado)
- [ ] `DEBUG=false` (para produção)

**Se faltar alguma:**
1. Adicione a variável
2. Salve
3. Reinicie o backend

### 6. Testar Conectividade

**Do seu computador:**

```bash
# Teste se a porta está aberta
telnet 31.97.16.142 8080
# ou
nc -zv 31.97.16.142 8080
```

**Se não conectar:**
- Firewall pode estar bloqueando
- Porta não está exposta corretamente
- Backend não está rodando

### 7. Verificar Firewall

**No servidor do Coolify:**
- Verifique se a porta 8080 está aberta no firewall
- Se necessário, abra a porta:
  ```bash
  # Ubuntu/Debian
  sudo ufw allow 8080/tcp
  
  # CentOS/RHEL
  sudo firewall-cmd --add-port=8080/tcp --permanent
  sudo firewall-cmd --reload
  ```

## ✅ Soluções Rápidas

### Solução 1: Reiniciar o Backend

1. No Coolify, vá na aplicação do backend
2. Clique em **Restart**
3. Aguarde alguns segundos
4. Teste novamente: `http://31.97.16.142:8080/health`

### Solução 2: Fazer Redeploy

1. No Coolify, vá na aplicação do backend
2. Clique em **Redeploy**
3. Aguarde o build completar
4. Teste novamente

### Solução 3: Verificar e Corrigir Ports Mappings

1. Vá em **Configuration → Network**
2. Verifique **Ports Mappings**
3. Se não for `8080:8080`, corrija
4. Salve e reinicie

### Solução 4: Verificar Logs e Corrigir Erros

1. Vá em **Logs**
2. Identifique o erro
3. Corrija conforme o erro (ex: variável de ambiente faltando)
4. Reinicie

## 🧪 Teste Após Correções

```bash
# 1. Health check
curl http://31.97.16.142:8080/health
# Deve retornar: {"status": "healthy", "version": "1.0.0"}

# 2. Endpoint raiz
curl http://31.97.16.142:8080/
# Deve retornar JSON com informações da API

# 3. Documentação
# Acesse no navegador: http://31.97.16.142:8080/docs
```

## 📋 Checklist Completo

- [ ] Container está rodando (status "Running")
- [ ] Logs mostram "Application startup complete"
- [ ] Ports Exposes = `8080`
- [ ] Ports Mappings = `8080:8080`
- [ ] Base Directory = `backend/`
- [ ] Docker Build Stage Target = `production`
- [ ] Variáveis de ambiente configuradas
- [ ] Firewall permite porta 8080
- [ ] Teste `curl http://31.97.16.142:8080/health` funciona

## 🔗 Próximos Passos

Se após todas as verificações ainda não funcionar:

1. **Compartilhe os logs** do backend no Coolify
2. **Verifique a configuração** de Network
3. **Teste localmente** primeiro para garantir que o código funciona
4. **Verifique se o servidor Coolify** está acessível

---

**Dica:** Sempre verifique os **Logs** primeiro - eles geralmente mostram o problema!

