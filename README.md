# CIMut Backend API

## Project Description

This is the backend API component of the CIMut project, developed in FastAPI. It implements an agent management system for mutation testing and fault injection in Continuous Integration (CI) environments. The system allows connecting multiple agents via WebSocket and executing controlled code modification operations to validate application robustness.

**Note**: This repository contains only the backend API. The complete CIMut project includes additional components for the full mutation testing ecosystem.

## Main Features

- **Agent Management**: Connection and control of multiple agents via WebSocket
- **Fault Injection**: Controlled file modification for mutation testing
- **Code Verification**: Reading specific lines in files
- **Monitoring**: Listing connected agents and their status
- **Observability**: Integrated OpenTelemetry instrumentation

## Architecture

The project uses an architecture based on:

- **FastAPI**: Web framework for API development
- **WebSocket**: Real-time communication with agents
- **Docker**: Containerization to facilitate deployment
- **OpenTelemetry**: Distributed monitoring and tracing

## Project Structure

```
cimut-api/
├── main.py                 # Application entry point
├── src/
│   ├── server.py          # FastAPI server configuration
│   └── app/
│       ├── api/
│       │   ├── controllers/
│       │   │   └── agent_controller.py  # API controllers
│       │   └── schemas/
│       │       └── requests/           # Pydantic schemas
│       └── services/
│           └── agent_service.py        # Agent business logic
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
└── docker-compose.yml    # Container orchestration
```

## API Endpoints

### WebSocket
- `GET /api/agent/connect` - WebSocket connection for agents

### HTTP
- `GET /api/agents` - List all connected agents
- `POST /api/agents/{agent_id}/fault` - Inject fault in file
- `POST /api/agents/{agent_id}/verify` - Verify specific line content

## How to Run

### Prerequisites

- Python 3.12+
- Docker (optional)

### Local Execution

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

### Docker Execution

1. Build the image:
```bash
docker-compose build
```

2. Run the containers:
```bash
docker-compose up
```

## API Usage

### Connecting an Agent

Agents should connect via WebSocket by sending a JSON message with the agent ID:

```json
{
  "agent_id": "agent-001",
  "name": "Test Agent",
  "version": "1.0.0"
}
```

### Injecting Faults

```bash
curl -X POST "http://localhost:8000/api/agents/agent-001/fault" \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "/path/to/file.py",
    "line_number": 10,
    "new_content": "modified_line_content"
  }'
```

### Verifying Code

```bash
curl -X POST "http://localhost:8000/api/agents/agent-001/verify" \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "/path/to/file.py",
    "line_number": 10
  }'
```

## Development

For local development with auto-reload:

```bash
uvicorn src.server:app --reload --host 0.0.0.0 --port 8000
```

## Technologies Used

- **FastAPI**: Asynchronous web framework
- **Uvicorn**: ASGI server
- **Pydantic**: Data validation
- **OpenTelemetry**: Observability
- **Docker**: Containerization
- **Python 3.12**: Programming language

## Author

Developed by Guilherme Silva

## License

This project is under the MIT license.
