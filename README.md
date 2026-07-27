# AnomaScan

YOLO-powered video analysis web application. Upload a video, run object detection with a configurable model and confidence threshold, browse detection events, and fine-tune a custom YOLO model on your own labeled dataset.

**Stack:** React 19 (CRA + TypeScript) · FastAPI · ClickHouse · Ultralytics YOLO · Docker

---

## Quick start

```bash
docker compose up --build
```

| Service | URL | Description |
|---------|-----|-------------|
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
```
