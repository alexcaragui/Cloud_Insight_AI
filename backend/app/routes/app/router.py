
import os
import pathlib
import subprocess
import uuid
from app.settings import YOLO_MODELS_DIR, FPS, ALLOWED_VIDEO_EXTS
from ultralytics import YOLO 

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from app.database import get_ch


router = APIRouter(prefix="/api", tags=["app"])  # mounts all log-viewer endpoints under /api/logs


def _process_video(video_path: str, confidence: float, video_id: str) -> tuple[list[dict], str]:
    """Run YOLO inference, save the output, and convert it via FFmpeg."""
    
    model_path = os.path.join(YOLO_MODELS_DIR, "best.pt")
    print(f"\n{'='*50}\nCAUT MODELUL FIX AICI: {model_path}\n{'='*50}\n", flush=True) 
    
    if not os.path.exists(model_path):
        model_path = "yolov8n.pt" 
    model = YOLO(model_path)

    events = []
    frame_idx = 0 

    # YOLO salvează rezultatul în /app/public/yolo_out
    for result in model.predict(source=video_path, stream=True, conf=confidence, verbose=False, save=True, project="/app/public", name="yolo_out", exist_ok=True):
        if result.boxes is not None and len(result.boxes) > 0:
            detections = []
            for box in result.boxes:
                label = result.names[int(box.cls[0])] 
                conf_val = float(box.conf[0]) 
                x1, y1, x2, y2 = [round(v) for v in box.xyxy[0].tolist()] 
                detections.append({
                    "label": label,
                    "confidence": round(conf_val, 4),
                    "box": [x1, y1, x2, y2],
                })
            events.append({
                "frame": frame_idx,
                "timestamp_s": round(frame_idx / FPS, 3), 
                "detections": detections,
            })
        frame_idx += 1 

    # Căutăm clipul .avi generat de YOLO și îl convertim cu FFmpeg
    base_name = os.path.basename(video_path)
    name_without_ext = os.path.splitext(base_name)[0]
    yolo_out_avi = f"/app/public/yolo_out/{name_without_ext}.avi"
    
    final_mp4_name = f"result_{video_id}.mp4"
    final_mp4_path = f"/app/public/{final_mp4_name}"

    if os.path.exists(yolo_out_avi):
        subprocess.run(["ffmpeg", "-y", "-i", yolo_out_avi, "-vcodec", "libx264", final_mp4_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    return events, f"http://localhost:8000/public/{final_mp4_name}"

@router.post("/analyze")
async def analyze_video(
    file: UploadFile = File(...), 
    confidence: float = Form(0.5),
):
    """Accept a video file, run YOLO inference, and return events + video + bot alert."""
    ext = pathlib.Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_VIDEO_EXTS: 
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file format '{ext}'. Allowed: {', '.join(sorted(ALLOWED_VIDEO_EXTS))}",
        )

    video_id = uuid.uuid4().hex
    tmp_path = f"/tmp/input_{video_id}{ext}"
    
    with open(tmp_path, "wb") as tmp:
        tmp.write(await file.read())

    try:
        events, final_video_url = _process_video(tmp_path, confidence, video_id) 
        
        # LOGICA PENTRU ANOMASCAN MONITOR 
        bot_alert = None
        if len(events) > 0:
            first_event_time = events[0]["timestamp_s"]
            total_events = len(events)
            bot_alert = (
                f"🚨 **Alertă AnomaScan Monitor** 🚨\n"
                f"Analiza video a fost finalizată. Au fost detectate {total_events} anomalii de tip 'spaghetti'.\n"
                f"Prima eroare critică apare la secunda {first_event_time}s.\n"
                f"Vă rugăm să verificați imediat integritatea liniei de printare."
            )

    except Exception as exc: 
        raise HTTPException(status_code=500, detail=f"YOLO processing failed: {exc}") from exc
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path) 

    return {
        "status": "success",
        "message": "Video analyzed successfully",
        "events": events,
        "video_url": final_video_url,
        "bot_alert_message": bot_alert 
    }
