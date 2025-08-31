# 🧪 Guia de Testes - CIMut API

## 🚀 Como Expor Localhost para Testes

### Opção 1: ngrok (Recomendado)

1. **Instalar ngrok:**
   ```bash
   # Windows (com chocolatey)
   choco install ngrok
   
   # Ou baixe de: https://ngrok.com/download
   ```

2. **Método Manual:**
   ```bash
   # Terminal 1: Inicie a API
   python main.py
   
   # Terminal 2: Inicie o ngrok
   ngrok http 8000
   ```

3. **Método Automático:**
   ```bash
   # Inicia API + ngrok automaticamente
   python start_with_tunnel.py
   ```

### Opção 2: Outras Alternativas

**tunnelmole (Open Source):**
```bash
npm install -g tunnelmole
tmole 8000  # Com sua API rodando
```

**localtunnel:**
```bash
npm install -g localtunnel
lt --port 8000
```

**serveo (Via SSH):**
```bash
ssh -R 80:localhost:8000 serveo.net
```

## 🧪 Testando a API

### Teste Automático
```bash
# Teste local
python test_api.py

# Teste com URL do tunnel
python test_api.py https://abc123.ngrok-free.app
```

### Teste Manual com curl

**1. Encontrar arquivo alvo para falha:**
```bash
curl -X POST "https://sua-url.ngrok-free.app/api/agents/test-agent/find-fault-target" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "quero causar falha na criação de instâncias do Nova"
  }'
```

**2. Usar LLM para mutação:**
```bash
curl -X POST "https://sua-url.ngrok-free.app/api/agents/mutation" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Como posso causar timeout na API do OpenStack Nova?"
  }'
```

## 📋 Variáveis de Ambiente Necessárias

Certifique-se de ter configurado:
```bash
export GROQ_API_KEY=sua_chave_groq_aqui
```

## 🔍 Endpoints Disponíveis

- `GET /` - Health check
- `POST /api/agents/{agent_id}/find-fault-target` - Encontra alvo para injeção de falha
- `POST /api/agents/{agent_id}/fault` - Injeta falha em arquivo
- `POST /api/agents/{agent_id}/verify` - Verifica conteúdo de linha
- `POST /api/agents/mutation` - Consulta LLM para mutações
- `GET /api/agent/connect` - WebSocket para agentes

## 💡 Dicas

1. **ngrok free** tem limitações:
   - 1 tunnel simultâneo
   - URL muda a cada restart
   - Limite de conexões

2. **Para produção**, considere:
   - ngrok pago
   - Deploy no Render/Heroku/Railway
   - Configurar domínio próprio

3. **Debug**:
   - Logs da API: verifique terminal
   - Logs do ngrok: interface web em http://127.0.0.1:4040
   - Use `curl -v` para debug detalhado

## 🛠️ Troubleshooting

**API não inicia:**
```bash
# Verifique dependências
pip install -r requirements.txt

# Verifique se a porta 8000 está livre
netstat -an | findstr :8000
```

**ngrok não conecta:**
```bash
# Verifique versão
ngrok version

# Teste conexão
ngrok http 8000 --log=stdout
```

**Modelo CodeBERT demora para carregar:**
- É normal na primeira execução (lazy loading)
- Próximas chamadas serão mais rápidas
- Modelo é liberado da memória após uso
