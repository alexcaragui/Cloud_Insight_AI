
import os

from fastapi import APIRouter
from app.settings import YOLO_MODELS_DIR

router = APIRouter(prefix="/api/models", tags=["models"])  # mounts all model endpoints under /api/models


@router.get("")
def list_models():
    """Return available YOLO model weights from YOLO_MODELS_DIR plus the bundled base model."""
    models = [{"name": "yolov8n (base)", "path": "yolov8n.pt"}]  # base model always available
    if os.path.isdir(YOLO_MODELS_DIR):
        for fname in sorted(os.listdir(YOLO_MODELS_DIR)):
            if fname.endswith(".pt"):  # only expose PyTorch weight files
                models.append({"name": fname.replace(".pt", ""), "path": fname})
    return models
