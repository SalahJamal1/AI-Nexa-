# AI-Nexa

An AI microservices platform: a Spring Cloud backbone (config server, service discovery, API gateway) secured by Keycloak, fronting three Python/FastAPI AI services and an n8n automation workflow. Everything runs with a single `docker compose up`.

## Architecture

```
Client ──► Gateway :8000 (Spring Cloud Gateway, JWT validation via Keycloak)
              │
              ├─ /api/v1/vision       ──► Vision AI            :8001
              ├─ /api/v1/resume       ──► Resume Intelligence  :8002 ──► host Ollama :11434 (+ ChromaDB)
              └─ /api/v1/recruitment  ──► AI Hiring Assistant  :8003 ──► n8n :5678 (webhook)

Config Server :8888 ─ centralized config for Spring services
Discovery (Eureka) :8761 ─ all services register here
Keycloak :8080 ─ realm `ai-agentic`, client `ai-agentic-api`
```

## Services

| Service | Stack | Port | Description |
|---|---|---|---|
| `config` | Spring Boot | 8888 | Spring Cloud Config Server |
| `discovery` | Spring Boot | 8761 | Eureka service registry |
| `gateway` | Spring Boot | 8000 | API gateway, OAuth2 resource server, aggregated Swagger UI |
| `keycloak` | Keycloak 26 | 8080 | Identity provider (realm imported from `keycloak/realm-export.json`) |
| `vision-ai` | FastAPI, PyTorch | 8001 | Food image classification (Food-101, ViT) — `POST /predict` |
| `resume-intelligence` | FastAPI, LangChain, ChromaDB | 8002 | LLM-based resume analysis — `POST /analyze` |
| `ai-hiring-assistant` | FastAPI | 8003 | Candidate screening, triggers n8n workflow — `POST /screen` |
| `n8n` | n8n | 5678 | Workflow automation |

## Getting started

### Prerequisites
- Docker and Docker Compose
- [Ollama](https://ollama.com) installed and running on the host (`ollama serve`, port 11434)
- Enough disk/RAM for PyTorch and Ollama models

### Run

```bash
docker compose up --build
```

Services start in dependency order (config → discovery → keycloak → gateway/AI services), gated by health checks. The first start can take several minutes.

Ollama is not part of the compose stack: Resume Intelligence reaches the Ollama running on your machine via `host.docker.internal:11434`. Override with `OLLAMA_HOST=... docker compose up` if needed.

Pull the models Resume Intelligence uses on the host:

```bash
ollama pull qwen3:1.7b
```

Also pull the embedding model configured in `Resume Intelligence/graph/rag/vectorstore.py`.

### Useful URLs

- Gateway Swagger UI (aggregates all services): http://localhost:8000/swagger-ui.html
- Eureka dashboard: http://localhost:8761
- Keycloak admin console: http://localhost:8080 (dev default `admin` / `admin`)
- n8n: http://localhost:5678

## Authentication

Requests go through the gateway and require a Keycloak-issued JWT from realm `ai-agentic`. Swagger UI uses the `ai-agentic-api` client with Authorization Code + PKCE.

> The credentials in `docker-compose.yml` (Keycloak `admin`/`admin`) and the realm export are for local development only. Change them before any real deployment.

## Project layout

```
config/                 Spring Cloud Config Server (+ per-service config in src/main/resources/configurations)
discovery/              Eureka server
gateway/                Spring Cloud Gateway
keycloak/               Realm export imported on startup
Vision AI/              Image classification service
Resume Intelligence/    Resume analysis service
AI Hiring Assistant/    Candidate screening service
docker-compose.yml      Full-stack orchestration
```

## Local development (individual Python services)

Each Python service uses [uv](https://github.com/astral-sh/uv) and requires Python 3.13+:

```bash
cd "Vision AI"   # or "Resume Intelligence" / "AI Hiring Assistant"
uv sync
uv run python main.py
```

Spring services use the Maven wrapper: `cd gateway && ./mvnw spring-boot:run`.
