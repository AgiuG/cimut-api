# API FastAPI - Backend

Uma API REST construída com FastAPI e Uvicorn.

## Características

- ✅ FastAPI para criação da API REST
- ✅ Uvicorn como servidor ASGI
- ✅ Validação de dados com Pydantic
- ✅ CORS configurado
- ✅ Documentação automática (Swagger UI)
- ✅ Endpoints CRUD básicos
- ✅ Tratamento de erros

## Requisitos

- Python 3.8+
- pip

## Instalação

1. Clone o repositório ou navegue até a pasta do projeto
2. Crie um ambiente virtual (recomendado):
   ```bash
   python -m venv venv
   ```

3. Ative o ambiente virtual:
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

4. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

## Execução

### Modo de desenvolvimento (com reload automático):
```bash
python main.py
```

### Ou usando uvicorn diretamente:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
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
| GET | `/` | Endpoint raiz |
| GET | `/health` | Verificação de saúde |
| GET | `/items` | Listar todos os itens |
| GET | `/items/{id}` | Obter item por ID |
| POST | `/items` | Criar novo item |
| PUT | `/items/{id}` | Atualizar item |
| DELETE | `/items/{id}` | Deletar item |

## Exemplo de Uso

### Criar um item:
```bash
curl -X POST "http://localhost:8000/items" \
     -H "Content-Type: application/json" \
     -d '{"name": "Produto Teste", "description": "Descrição do produto", "price": 29.99}'
```

### Listar itens:
```bash
curl http://localhost:8000/items
```

## Estrutura do Projeto

```
back/
├── main.py              # Arquivo principal da aplicação
├── requirements.txt     # Dependências do projeto
└── README.md           # Este arquivo
```

## Próximos Passos

Para expandir esta API, considere adicionar:

- 📁 Organização em módulos (`routers/`, `models/`, `services/`)
- 🗄️ Integração com banco de dados (SQLAlchemy, PostgreSQL, etc.)
- 🔐 Autenticação e autorização (JWT)
- 📊 Logging e monitoramento
- 🧪 Testes automatizados (pytest)
- 🐳 Dockerização
- 🚀 Deploy em produção
