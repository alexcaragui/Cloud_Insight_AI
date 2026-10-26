<<<<<<< HEAD
# Cloud Insight Ai

YOLO-powered video analysis web application. Upload a video, run object detection with a configurable model and confidence threshold, browse detection events, and fine-tune a custom YOLO model on your own labeled dataset.

**Stack:** React 19 (CRA + TypeScript) · FastAPI · ClickHouse · Ultralytics YOLO · Docker

---

## Quick start

=======
# CloudInsight AI

CloudInsight AI is an AI-powered cloud infrastructure advisor for developers and cloud engineers. It is designed to help teams understand their cloud environments, find optimization opportunities, and ask questions about infrastructure in natural language instead of manually searching dashboards, reports, and configuration files.

The product is intended to work with infrastructure data such as Azure exports, Terraform files, JSON, and CSV reports. Its goal is to ground AI answers in the user's uploaded environment and make cloud architecture and cost information easier to understand.

## Quick start

The repository includes a Docker Compose definition for the frontend, FastAPI backend, ClickHouse, and Ollama services:

>>>>>>> 0952e1b (Update README documentation)
```bash
docker compose up --build
```

| Service | URL | Description |
|---------|-----|-------------|
<<<<<<< HEAD
| Frontend | http://localhost:3000 | React app (nginx) |
| Backend | http://localhost:8000 | FastAPI + YOLO |
| ClickHouse HTTP | http://localhost:8123 | Log storage |

---

## Development (hot reload)

```bash
docker compose --profile dev up --build frontend-dev
```

The dev server runs on port 3000 with file-watching enabled. Source changes in `frontend/src/` reflect immediately without rebuilding the image.

To run the backend locally (outside Docker):

```bash
cd backend
cp e.env .env          # fill in CLICKHOUSE_URL if needed
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

---

## Environment variables

**Backend** (`backend/.env`):

| Variable | Default | Description |
|----------|---------|-------------|
| `CLICKHOUSE_URL` | `clickhouse://core-ch:core-ch@localhost:9000/core` | ClickHouse DSN |
| `YOLO_MODELS_DIR` | `../models` | Directory containing `.pt` weight files |

**Frontend** (`frontend/.env`):

| Variable | Default | Description |
|----------|---------|-------------|
| `REACT_APP_API_URL` | `http://localhost:8000/api` | Backend base URL (baked in at build time) |

---

## Features

### Video analysis

1. Select a YOLO model from the dropdown (custom fine-tuned models appear here automatically).
2. Adjust the confidence threshold slider (0.1 – 1.0).
3. Drop a video file onto the upload zone or click to browse (MP4, AVI, MOV — max 500 MB).
4. Click **Run YOLO** — the backend processes every frame and returns detection events.
5. The **Detection Events** panel shows each frame with timestamp, class labels, and per-detection confidence scores.
6. The stat bar summarises total events, unique class count, and the top 3 most frequent labels.

### Model fine-tuning

1. Prepare a YOLO-format dataset ZIP (`images/`, `labels/`, `data.yaml` at the root).
2. Upload the ZIP in the **Fine-Tune Model** card, set the epoch count, and click **Start Training**.
3. Training progress streams in real time via WebSocket (epoch number + box loss).
4. When training completes the new model is saved to `YOLO_MODELS_DIR` and appears in the model selector.

---

## API reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Healthcheck — returns `{"status": "ok"}` |
| `POST` | `/api/analyze` | Run YOLO on an uploaded video; returns events + processed video URL |
| `GET` | `/api/models` | List available `.pt` model files |
| `GET` | `/api/logs` | Paginated HTTP request logs from ClickHouse |
| `GET` | `/api/logs/summary` | Hourly aggregated log summary |
| `POST` | `/api/anomascan/finetune` | Start fine-tune training job |
| `WS` | `/api/listener/{job_id}` | Stream training progress lines |
| `GET` | `/api/response/{job_id}` | Retrieve trained model path after completion |

`POST /api/analyze` form fields:

| Field | Type | Description |
|-------|------|-------------|
| `file` | `UploadFile` | Video file (MP4 / AVI / MOV) |
| `confidence` | `float` | Detection confidence threshold (default: `0.5`) |
| `model` | `string` | Model filename from `YOLO_MODELS_DIR` (default: `yolov8n.pt`) |

---

## Project structure

```
AnomaScan/
├── models/
│   └── best.pt                  # Custom YOLO weights (bind-mounted into backend)
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py              # FastAPI app, lifespan, router registration
│       ├── settings.py          # Constants and env var defaults
│       ├── database.py          # ClickHouse + logger singletons
│       ├── schemas/
│       │   └── logs.py          # ApiLogEntry / AppLogEntry Pydantic models
│       ├── routes/
│       │   ├── app/             # POST /api/analyze
│       │   ├── models/          # GET /api/models
│       │   ├── logs/            # GET /api/logs, /api/logs/summary
│       │   └── finetune/        # POST /api/anomascan/finetune, WS, GET response
│       ├── db/clickhouse/       # ClickHouseLogAdapter — DDL, inserts, queries
│       ├── queries/             # Raw SQL constants (DDL, INSERT, SELECT)
│       ├── logger/              # AppLogger wrapping the adapter
│       └── events/              # LogLevel constants, lifecycle message templates
├── frontend/
│   ├── Dockerfile               # Multi-stage: node build → nginx serve
│   ├── Dockerfile.dev           # Dev server with hot reload
│   ├── nginx.conf
│   └── src/
│       ├── App.tsx              # Main component — all state and API calls
│       ├── App.css
│       └── components/
│           ├── VideoDropzone.tsx
│           ├── ConfidenceSlider.tsx
│           ├── EventsList.tsx
│           └── StatBar.tsx
└── docker-compose.yml
=======
| Frontend | http://localhost:3000 | CloudInsight AI web application |
| Backend | http://localhost:8000 | FastAPI API |
| ClickHouse HTTP | http://localhost:8123 | Log storage |
| Ollama | http://localhost:11434 | Local language model service |

For local setup without Docker, see [Run locally](#run-locally).

## Development

The Compose file includes an optional Vite development frontend:

```bash
docker compose --profile dev up --build clickhouse ollama backend frontend-dev
```

To run the backend and frontend directly on the host, see [Run locally](#run-locally). The frontend uses Vite on port 3000 by default.

## Environment variables

### Backend

| Variable | Default / source | Description |
|----------|------------------|-------------|
| `CLICKHOUSE_URL` | Defined in `backend/app/settings.py`; the Compose service overrides it | ClickHouse Connect DSN used for application log storage |
| `OLLAMA_URL` | `http://ollama:11434` | Base URL of the Ollama HTTP API |
| `OLLAMA_MODEL` | `qwen2.5:7b` | Model checked by the backend during startup |

`backend/e.env` is the checked-in environment example. The Python application does not load this file automatically; use Uvicorn's `--env-file e.env` option when running locally. For local host-based development, set `OLLAMA_URL` and `CLICKHOUSE_URL` to addresses reachable from the host.

### Frontend

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_BASE_URL` | `/api` | Base URL used by the frontend REST and WebSocket clients |
| `VITE_USE_MOCK` | None | Declared as a production Docker build argument; not read by the frontend source |

For local development against a backend on port 8000, create `frontend/.env.local`:

```dotenv
VITE_API_BASE_URL=http://localhost:8000/api
```

Vite variables are included in browser code; do not put secrets in them.

## Features

### AI infrastructure chat

CloudInsight AI is intended to let users ask questions about their own cloud environment, for example:

- Which virtual machines are underutilized?
- How can I reduce my monthly Azure costs?
- Which resources consume the most storage?
- Can you explain my network architecture?

The intended assistant answers using relevant information retrieved from the user's uploaded infrastructure data, rather than relying only on a general-purpose language model.

### Cloud cost optimization

The product is intended to analyze cloud resource data and identify potential savings opportunities, including:

- Oversized virtual machines
- Unused storage accounts
- Idle databases
- Unnecessary public IP addresses
- Inactive resources

Recommendations are intended to include estimated monthly savings. Savings calculations depend on the availability and quality of resource and pricing data.

### Infrastructure data ingestion

The intended inputs include Azure exports, Terraform files, JSON, and CSV reports. Data is validated and preprocessed so relevant resource details can be searched and used as context in AI conversations.

## AI workflow

The target architecture uses Retrieval-Augmented Generation (RAG) to ground answers in each user's infrastructure:

1. The user uploads infrastructure data.
2. The system validates and preprocesses the files, extracting useful resource and configuration details.
3. Extracted content is converted into vector embeddings and indexed in a vector store for semantic search.
4. When the user asks a question, the system retrieves the most relevant infrastructure context.
5. The retrieved context is supplied to the language model to generate an answer, explanation, or optimization recommendation.

This workflow is intended to keep responses specific to the uploaded environment, reduce unsupported answers, and help explain recommendations.

## Technologies and architecture

- **Frontend:** React 19, TypeScript, Vite, React Router, TanStack Query, Tailwind CSS, and i18next.
- **Backend:** Python 3.12 container, FastAPI, and Uvicorn.
- **Language model runtime:** Ollama, accessed by the backend over HTTP; chat tokens are relayed to the browser over WebSocket.
- **Logging:** ClickHouse, accessed with `clickhouse-connect`. The backend provisions API, application, and chat log tables.
- **Deployment:** Docker Compose defines ClickHouse, Ollama, a model downloader, the backend, a production frontend, and an optional Vite development frontend.

The browser uses the configured API base URL (default `/api`). The backend exposes health, login, Ollama model/chat, and API-log routes. ClickHouse is used for logging; it is not configured as the infrastructure vector store.

## Prerequisites

For local development:

- Python 3.12 (the version used by the backend Docker image; the minimum supported version is not specified).
- Node.js 20 or newer and pnpm.
- A reachable ClickHouse server.
- A reachable Ollama server. The backend requests `qwen2.5:7b` during startup if it is not already installed.

For Docker Compose, install Docker Engine/Desktop with the Compose plugin. The Ollama service reserves an NVIDIA GPU in the Compose configuration, so GPU-enabled Docker support may be required.

## Environment configuration

### Backend

The backend reads these environment variables:

| Variable | Default / source | Purpose |
| --- | --- | --- |
| `CLICKHOUSE_URL` | Required for the selected ClickHouse instance; a default is defined in `backend/app/settings.py` | ClickHouse Connect DSN used for log storage. |
| `OLLAMA_URL` | `http://ollama:11434` | Base URL of the Ollama HTTP API. |
| `OLLAMA_MODEL` | `qwen2.5:7b` | Model the backend checks for at startup. |

`backend/e.env` is the checked-in environment example and defines `CLICKHOUSE_URL`. Review and adjust it for the ClickHouse instance you use. For local execution, Uvicorn can load it with `--env-file e.env`; the Python application does not load `e.env` automatically. When running the backend directly on your host, set `OLLAMA_URL` to an Ollama address reachable from that host (for example, a host-local Ollama instance) instead of relying on the Compose service hostname.

Docker Compose supplies `CLICKHOUSE_URL` and `OLLAMA_URL` to the backend container. ClickHouse credentials and database settings are also set directly in `docker-compose.yml`; change those values there if you need different credentials.

### Frontend

| Variable | Default | Purpose |
| --- | --- | --- |
| `VITE_API_BASE_URL` | `/api` | Base URL used by the frontend REST and WebSocket clients. Set an absolute URL when the browser should contact a separately hosted backend directly. |
| `VITE_USE_MOCK` | Not used by the current frontend source | Declared as a production Docker build argument, but no application code reads it. |

Vite reads frontend variables at build/dev-server startup. For direct local development against a backend on port 8000, create `frontend/.env.local` with:

```dotenv
VITE_API_BASE_URL=http://localhost:8000/api
```

No secrets should be placed in frontend variables: Vite values are available to browser code.

## Run locally

### Start the backend

First make sure ClickHouse and Ollama are running and reachable, then from the repository root:

```powershell
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
uvicorn app.main:app --reload --env-file e.env --port 8000
```

Set or update the backend environment values for your local services before starting. The application initializes ClickHouse log tables during startup; the Ollama model pull may continue in the background.

The API should be available at `http://localhost:8000`. FastAPI's interactive API documentation is available at `http://localhost:8000/docs`.

### Start the frontend

In a second terminal:

```powershell
cd frontend
corepack enable
corepack pnpm install
corepack pnpm dev
```

Open the Vite URL shown in the terminal (the configured port is `3000`). Set `VITE_API_BASE_URL` as described above so the browser can reach the backend. `vite.config.ts` does not configure an `/api` development proxy.

## Docker Compose

The Compose file is intended to start the full stack:

```powershell
docker compose up --build
```

Configured service ports:

| Service | Local address | Purpose |
| --- | --- | --- |
| Frontend | `http://localhost:3000` | Production frontend container |
| Backend | `http://localhost:8000` | FastAPI API |
| ClickHouse HTTP | `http://localhost:8123` | ClickHouse HTTP interface |
| ClickHouse native | `localhost:9000` | ClickHouse native protocol |
| Ollama | `http://localhost:11434` | Ollama API |

Compose defines named volumes for ClickHouse data, Ollama state, the backend's `/app/data` mount, and frontend development dependencies. The `model-downloader` service pulls `qwen2.5:7b` and `nomic-embed-text:latest`; the backend's chat endpoint defaults to `qwen2.5:7b`.

To start the optional Vite development container instead of the production frontend:

```powershell
docker compose --profile dev up --build clickhouse ollama backend frontend-dev
```

This starts the development frontend together with its backend and data/model services. The development and production frontend services both bind port 3000, so do not run both at the same time. The Compose development service sets `API_PROXY_TARGET`, but the current Vite configuration does not use that variable or define a proxy; configure `VITE_API_BASE_URL` appropriately if API requests do not reach the backend.

`frontend/Dockerfile` copies `frontend/nginx.conf`, which is not present in the repository. The production frontend image build therefore requires that file to be supplied or the Dockerfile to be updated.

## API reference

These are the HTTP and WebSocket routes currently defined by the FastAPI backend. The infrastructure upload formats and upload API contract are not specified by the backend routes.

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/api/health` | Health check; returns `{"status":"ok"}`. |
| `POST` | `/api/auth/login` | Accepts JSON with `email` and `password` strings and returns a generated token and demo user. It does not validate credentials. |
| `GET` | `/api/ollama/models` | Returns the model list from Ollama (`/api/tags`). |
| `POST` | `/api/ollama/models/pull` | Accepts `{"name":"<model>"}` and streams Ollama pull progress as server-sent events. |
| `DELETE` | `/api/ollama/models/{name}` | Deletes the named Ollama model. The model name may contain path segments. |
| `WS` | `/api/ollama/chat/ws` | Receives JSON with `model` and `messages`; streams `token`, then `done` messages, or an `error`. |
| `GET` | `/api/logs` | Returns paginated API request log rows and a total count. |
| `GET` | `/api/logs/summary` | Returns an hourly aggregation of API request logs and a total count. |

### Log query parameters

`GET /api/logs` supports:

- `limit` (default `100`, maximum `500`)
- `offset` (default `0`, minimum `0`)
- `event_type`, `owner`, and `level` filters
- `from` and `to` datetime filters

`GET /api/logs/summary` supports:

- `from` and `to` datetime filters
- `event_type` and `path` filters
- `limit` (default `500`, maximum `2000`)
- `offset` (default `0`, minimum `0`)

When no dates are supplied, the ClickHouse adapter defaults the time window to the current month through the current time.

The chat WebSocket accepts messages shaped like:

```json
{
  "model": "qwen2.5:7b",
  "messages": [
    { "role": "user", "content": "Hello" }
  ]
}
```

The client receives JSON objects such as `{"type":"token","content":"..."}` and `{"type":"done"}`. Completed exchanges are written to the ClickHouse `chat_logs` table.

## Testing and quality checks

There is no backend test suite or frontend test script configured in the repository. The frontend defines these validation commands:

```powershell
cd frontend
corepack pnpm lint
corepack pnpm build
```

The backend dependencies do not include a configured test runner or test files.

## Project structure

```text
.
├── docker-compose.yml
├── backend/
│   ├── Dockerfile
│   ├── e.env                    # backend environment example
│   ├── requirements.txt
│   └── app/
│       ├── main.py              # FastAPI app, startup, health route
│       ├── settings.py          # ClickHouse and Ollama settings
│       ├── database.py          # ClickHouse/logger initialization
│       ├── routes/
│       │   ├── auth/router.py   # authentication route
│       │   ├── logs/router.py   # API log query endpoints
│       │   └── ollama/router.py # model and chat endpoints
│       ├── services/            # Ollama HTTP and streaming operations
│       ├── db/clickhouse/        # ClickHouse adapter
│       ├── queries/              # ClickHouse DDL and query constants
│       ├── schemas/              # Log entry models
│       ├── logger/               # Application and request log writer
│       └── events/               # Lifecycle event helpers
└── frontend/
    ├── Dockerfile                # production Vite build + nginx image
    ├── Dockerfile.dev            # Vite development image
    ├── package.json
    └── src/
        ├── App.tsx               # Browser routes
        ├── pages/                # Dashboard, chat, models, login, etc.
        ├── components/           # Layout and route guards
        ├── context/              # Auth, model, and theme state
        ├── services/             # Backend API and WebSocket clients
        ├── modules/              # Upload widget and toast UI
        └── i18n/                 # English and Romanian translations
>>>>>>> 0952e1b (Update README documentation)
```
