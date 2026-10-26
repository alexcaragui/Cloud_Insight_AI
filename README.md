# CloudInsight AI

CloudInsight AI is an AI-powered cloud infrastructure advisor for developers and cloud engineers. It is designed to help users understand their cloud environments, explore infrastructure data in natural language, and identify opportunities to optimize resource usage and cost.

The intended workflow is to upload cloud infrastructure data, retrieve the most relevant context for a question, and use that context to generate an answer or recommendation grounded in the user's environment.

**Technology:** React 19 · TypeScript · Vite · FastAPI · Ollama · ClickHouse · Docker Compose

---

## Quick start

The repository defines a Docker Compose stack with the web frontend, FastAPI backend, ClickHouse, and Ollama:

```bash
docker compose up --build
```

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | CloudInsight AI web application |
| Backend | http://localhost:8000 | FastAPI API |
| ClickHouse HTTP | http://localhost:8123 | Log storage |
| Ollama | http://localhost:11434 | Local language model service |

**Docker note:** The production frontend image expects `frontend/nginx.conf`, which is not present in the repository. The production frontend build needs that file or a corresponding Dockerfile change. Local development instructions are below.

---

## Development

Run the frontend in the Vite development container with the backend and its services:

```bash
docker compose --profile dev up --build clickhouse ollama backend frontend-dev
```

The frontend development server uses port 3000. The Vite configuration does not currently define an API proxy; `VITE_API_BASE_URL` must point to a backend URL reachable from the browser.

For host-based development, start the backend and frontend separately as described in [Run locally](#run-locally).

---

## Environment variables

### Backend

| Variable | Default | Description |
|----------|---------|-------------|
| `CLICKHOUSE_URL` | Set in `backend/e.env`; Compose overrides it for its ClickHouse service | ClickHouse Connect DSN used for application logs |
| `OLLAMA_URL` | `http://ollama:11434` | Base URL of the Ollama HTTP API |
| `OLLAMA_MODEL` | `qwen2.5:7b` | Model checked by the backend during startup |

For local execution, `backend/e.env` is an example environment file. Uvicorn can load it with `--env-file e.env`; the application does not load it automatically. Set service URLs to addresses reachable from the host when running outside Docker.

### Frontend

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_BASE_URL` | `/api` | Base URL used by frontend REST and WebSocket clients |

For local development with the backend on port 8000, create `frontend/.env.local`:

```dotenv
VITE_API_BASE_URL=http://localhost:8000/api
```

Vite variables are exposed to browser code; do not put secrets in them.

---

## Features and intended use

### AI infrastructure chat

The advisor is intended to answer questions about a user's uploaded environment, such as:

- Which virtual machines are underutilized?
- How can I reduce my monthly Azure costs?
- Which resources consume the most storage?
- Can you explain my network architecture?

Answers should be grounded in relevant infrastructure data, rather than generated only from a general-purpose model's prior knowledge.

### Cloud cost optimization

The platform is intended to identify potential savings opportunities, including:

- Oversized virtual machines
- Unused storage accounts
- Idle databases
- Unnecessary public IP addresses
- Inactive resources

Recommendations are intended to include estimated monthly savings when the uploaded resource and pricing data are sufficient.

### Infrastructure data

The intended input formats include Azure exports, Terraform files, JSON, and CSV reports. Data should be validated and preprocessed to make resource details useful for search and analysis.

---

## AI workflow

CloudInsight AI is designed around a Retrieval-Augmented Generation (RAG) workflow:

1. A user uploads infrastructure data.
2. The system validates and preprocesses the files and extracts resource and configuration details.
3. Extracted content is converted into vector embeddings and indexed for semantic search.
4. When the user asks a question, the system retrieves relevant infrastructure context.
5. The retrieved context is provided to a language model to generate a grounded answer or recommendation.

This approach is intended to make responses specific to the user's cloud environment, explain complex configurations, and support practical optimization recommendations.

---

## Technologies and architecture

- **Frontend:** React 19, TypeScript, Vite, React Router, TanStack Query, Tailwind CSS, and i18next.
- **Backend:** Python 3.12 container, FastAPI, and Uvicorn.
- **Language model:** Ollama, called by the backend over HTTP. Chat responses are streamed to the browser over WebSocket.
- **Logging:** ClickHouse, accessed through `clickhouse-connect`; the backend provisions API, application, and chat log tables.
- **Deployment:** Docker Compose defines ClickHouse, Ollama, a model downloader, the backend, and production and development frontend services.

The repository currently includes Ollama model management and chat endpoints, ClickHouse log storage and log-query routes, and a frontend upload widget. The upload widget calls `/api/plugin/cloudInsightAI/upload`, which is not implemented by this repository's FastAPI backend. A vector database and the infrastructure ingestion/RAG API are not configured in the checked-in backend.

---

## Prerequisites

For local development:

- Python 3.12 (the version used in the backend image; a minimum supported version is not specified).
- Node.js 20 or newer and pnpm.
- A reachable ClickHouse server.
- A reachable Ollama server.

For Docker, install Docker Engine or Docker Desktop with the Docker Compose plugin. The Compose Ollama service requests an NVIDIA GPU, so GPU-enabled Docker support may be needed for that configuration.

---

## Run locally

### Start the backend

Start ClickHouse and Ollama first, and ensure the backend environment points to addresses reachable from your machine. Then, from the repository root:

```powershell
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
uvicorn app.main:app --reload --env-file e.env --port 8000
```

The backend creates its ClickHouse log tables at startup and checks for the configured Ollama model. The API is available at `http://localhost:8000`; interactive API documentation is at `http://localhost:8000/docs`.

### Start the frontend

In a second terminal:

```powershell
cd frontend
corepack enable
corepack pnpm install
corepack pnpm dev
```

Open the Vite URL shown in the terminal (port 3000 by default). Configure `VITE_API_BASE_URL` as described above to connect to the local backend.

---

## Docker Compose

Start the full configured stack with:

```powershell
docker compose up --build
```

Compose publishes the frontend on port 3000, the backend on port 8000, ClickHouse on ports 8123 and 9000, and Ollama on port 11434. Named volumes persist ClickHouse data and Ollama model state. The model-downloader service pulls `qwen2.5:7b` and `nomic-embed-text:latest`.

To run the Vite development frontend with the backend and its dependencies:

```powershell
docker compose --profile dev up --build clickhouse ollama backend frontend-dev
```

Do not run the production and development frontend services together; both use port 3000. The production frontend build currently requires the missing `frontend/nginx.conf`.

---

## API reference

These are the routes currently defined by the FastAPI backend. An infrastructure upload endpoint and the RAG/vector-search API are not defined in this backend.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Health check; returns `{"status":"ok"}` |
| `POST` | `/api/auth/login` | Accepts `email` and `password`; returns a generated demo token and user |
| `GET` | `/api/ollama/models` | Lists models available in Ollama |
| `POST` | `/api/ollama/models/pull` | Accepts `{"name":"<model>"}` and streams model-download progress as server-sent events |
| `DELETE` | `/api/ollama/models/{name}` | Deletes an Ollama model |
| `WS` | `/api/ollama/chat/ws` | Accepts a model and chat messages; streams response tokens and completion/error events |
| `GET` | `/api/logs` | Returns paginated API log rows and a total count |
| `GET` | `/api/logs/summary` | Returns an hourly summary of API logs |

`POST /api/auth/login` currently does not validate credentials. Do not treat this route as production authentication.

### Log query parameters

`GET /api/logs` supports:

- `limit` (default `100`, maximum `500`)
- `offset` (default `0`, minimum `0`)
- `event_type`, `owner`, and `level`
- `from` and `to` datetime filters

`GET /api/logs/summary` supports:

- `from` and `to` datetime filters
- `event_type` and `path`
- `limit` (default `500`, maximum `2000`)
- `offset` (default `0`, minimum `0`)

If dates are omitted, the ClickHouse adapter queries from the start of the current month through the current time.

The chat WebSocket accepts messages shaped like:

```json
{
  "model": "qwen2.5:7b",
  "messages": [
    { "role": "user", "content": "Which resources should I review?" }
  ]
}
```

It streams JSON messages such as `{"type":"token","content":"..."}` followed by `{"type":"done"}`. The backend logs completed chat exchanges in ClickHouse.

---

## Testing

No backend test suite or frontend test script is configured. The frontend provides these checks:

```powershell
cd frontend
corepack pnpm lint
corepack pnpm build
```

---

## Project structure

```text
.
├── docker-compose.yml
├── backend/
│   ├── Dockerfile
│   ├── e.env
│   ├── requirements.txt
│   └── app/
│       ├── main.py
│       ├── settings.py
│       ├── database.py
│       ├── routes/
│       │   ├── auth/
│       │   ├── logs/
│       │   └── ollama/
│       ├── services/
│       ├── db/clickhouse/
│       ├── queries/
│       ├── schemas/
│       ├── logger/
│       └── events/
└── frontend/
    ├── Dockerfile
    ├── Dockerfile.dev
    ├── package.json
    └── src/
        ├── App.tsx
        ├── pages/
        ├── components/
        ├── context/
        ├── services/
        ├── modules/
        └── i18n/
```
