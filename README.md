# CIMut API - Backend

Uma API REST para injeção de falhas em sistemas remotos via SSH, construída com FastAPI e Paramiko.

## Características

- ✅ FastAPI para criação da API REST
- ✅ Uvicorn como servidor ASGI
- ✅ Validação de dados com Pydantic
- ✅ CORS configurado
- ✅ Documentação automática (Swagger UI)
- ✅ Conexão SSH remota com Paramiko
- ✅ Injeção de falhas em arquivos remotos
- ✅ Verificação de conteúdo de linhas específicas
- ✅ OpenTelemetry para instrumentação
- ✅ Dockerização completa
- ✅ Tratamento robusto de erros

## Requisitos

- Python 3.12+
- Docker e Docker Compose (para execução via containers)
- Acesso SSH aos sistemas remotos onde as falhas serão injetadas

## Instalação e Execução

### Opção 1: Usando Docker (Recomendado)

1. Clone o repositório:
   ```bash
   git clone <repository-url>
   cd cimut-api
   ```

2. Execute com Docker Compose:
   ```bash
   docker-compose up --build
   ```

A API estará disponível em: `http://localhost:8000`

### Opção 2: Execução Local

1. Crie um ambiente virtual:
   ```bash
   python -m venv venv
   ```

2. Ative o ambiente virtual:
   ```bash
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Execute a aplicação:
   ```bash
   python main.py
   ```

### Ou usando uvicorn diretamente:
```bash
uvicorn src.server:app --reload --host 0.0.0.0 --port 8000
```

A API estará disponível em: `http://localhost:8000`

## Documentação

Após iniciar o servidor, você pode acessar:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

## Endpoints Disponíveis

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/` | Endpoint raiz - status da API |
| POST | `/fault` | Injetar falha em arquivo remoto |
| POST | `/verify` | Verificar conteúdo de linha específica |

### Detalhes dos Endpoints

#### POST `/fault` - Injeção de Falha
Modifica o conteúdo de uma linha específica em um arquivo remoto via SSH.

**Request Body:**
```json
{
  "host": "192.168.1.100",
  "port": 22,
  "user": "username",
  "password": "password",
  "file_path": "/path/to/remote/file.txt",
  "line_number": 10,
  "new_content": "novo conteúdo da linha"
}
```

#### POST `/verify` - Verificar Linha
Obtém o conteúdo de uma linha específica de um arquivo remoto.

**Request Body:**
```json
{
  "host": "192.168.1.100",
  "port": 22,
  "user": "username",
  "password": "password",
  "remote_file_path": "/path/to/remote/file.txt",
  "line_number": 10
}
```

## Exemplo de Uso

### Injetar uma falha:
```bash
curl -X POST "http://localhost:8000/fault" \
     -H "Content-Type: application/json" \
     -d '{
       "host": "192.168.1.100",
       "port": 22,
       "user": "testuser",
       "password": "testpass",
       "file_path": "/opt/app/config.txt",
       "line_number": 5,
       "new_content": "modified_config=true"
     }'
```

### Verificar conteúdo de uma linha:
```bash
curl -X POST "http://localhost:8000/verify" \
     -H "Content-Type: application/json" \
     -d '{
       "host": "192.168.1.100",
       "port": 22,
       "user": "testuser",
       "password": "testpass",
       "remote_file_path": "/opt/app/config.txt",
       "line_number": 5
     }'
```

## Estrutura do Projeto

```
back/
├── docker-compose.yml           # Configuração Docker Compose
├── Dockerfile                   # Imagem Docker da aplicação
├── main.py                     # Arquivo principal da aplicação
├── requirements.txt            # Dependências do projeto
├── README.md                   # Este arquivo
└── src/
    ├── server.py              # Configuração do servidor FastAPI
    └── app/
        ├── api/
        │   ├── controllers/
        │   │   ├── __init__.py
        │   │   └── fault_controller.py  # Controladores dos endpoints
        │   └── schemas/
        │       ├── __init__.py
        │       └── requests/
        │           ├── __init__.py
        │           ├── InjectionFault.py # Schema para injeção de falhas
        │           └── VerifyLine.py     # Schema para verificação
        └── services/
            ├── __init__.py
            └── fault_service.py         # Serviços de SSH e manipulação de arquivos
```

## Dependências Principais

- **FastAPI**: Framework web moderno e de alta performance
- **Uvicorn**: Servidor ASGI para produção
- **Paramiko**: Biblioteca SSH para Python
- **Pydantic**: Validação de dados
- **OpenTelemetry**: Instrumentação e observabilidade

## Segurança

⚠️ **Importante**: Esta API manipula sistemas remotos via SSH. Certifique-se de:

- Usar conexões seguras (SSH keys ao invés de senhas quando possível)
- Validar todos os inputs
- Implementar autenticação e autorização adequadas
- Monitorar todas as operações
- Usar em ambientes controlados e de teste

## Próximos Passos

Para expandir esta API, considere adicionar:

- 🔐 Autenticação e autorização (JWT, OAuth2)
- 🔑 Suporte a chaves SSH ao invés de senhas
- 📊 Logging detalhado e auditoria
- 🧪 Testes automatizados (pytest)
- 📈 Métricas e monitoramento avançado
- 🔄 Rollback automático de mudanças
- 🚀 Deploy em produção com Kubernetes
- 💾 Persistência de logs de mutações em banco de dados
