import os
import uuid
import json
import shutil
import sys
from pathlib import Path
from datetime import datetime
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional

from fastapi import FastAPI, BackgroundTasks, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Ensure pipeline_runner is discoverable from api/
sys.path.append(str(Path(__file__).resolve().parent.parent))
from pipeline_runner import run_pipeline

# --- Pydantic Models ---

class JobStatusResponse(BaseModel):
    """Response model for job status checking."""
    job_id: str
    status: str = Field(description="pending, processing, completed, or failed")
    progress_percent: Optional[float] = 0.0
    result_path: Optional[str] = None
    error: Optional[str] = None

class HealthResponse(BaseModel):
    """Response model for API health check."""
    api_version: str
    status: str
    timestamp: str

class VideoAnalyzeResponse(BaseModel):
    """Response model for video upload endpoint."""
    job_id: str
    message: str

# --- Global State & Configuration ---

# Simple in-memory dictionary to store job states
JOB_STORE: Dict[str, Dict[str, Any]] = {}

UPLOAD_DIR = "data/raw/uploads"
OUTPUT_DIR = "data/processed/outputs"

# --- Lifecycle ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager to handle startup and shutdown events.
    Creates necessary directories on startup.
    """
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    yield
    # Cleanup operations could go here if needed

# --- Application Initialization ---

app = FastAPI(
    title="RetailEye AI Backend Analytics API",
    description="FastAPI backend for processing retail CCTV footage using YOLOv8, DeepSORT, and OpenCV",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Background Task Worker ---

def process_video_task(job_id: str, video_path: str, model_path: str, output_path: str) -> None:
    """
    The background worker function that executes the heavy CV pipeline.
    
    Args:
        job_id (str): Unique job identifier modifying the job store.
        video_path (str): File path of the uploaded video.
        model_path (str): File path to weights file.
        output_path (str): File path for final rendered output video.
    """
    JOB_STORE[job_id]["status"] = "processing"
    
    try:
        # Blocks and runs the analytics orchestration explicitly
        run_pipeline(
            video_path=video_path,
            model_path=model_path,
            output_path=output_path,
            show_live=False,
            save_analytics_json=True
        )
        
        # Mark completion
        JOB_STORE[job_id]["status"] = "completed"
        JOB_STORE[job_id]["progress_percent"] = 100.0
        JOB_STORE[job_id]["result_path"] = output_path
        
    except Exception as e:
        JOB_STORE[job_id]["status"] = "failed"
        JOB_STORE[job_id]["error"] = str(e)


# --- Endpoints ---

@app.post("/analyze/video", response_model=VideoAnalyzeResponse)
async def analyze_video(
    background_tasks: BackgroundTasks,
    video: UploadFile = File(...),
    model_path: str = Form(...)
) -> VideoAnalyzeResponse:
    """
    Accepts a video file upload and model path, triggers the background pipeline processing task, 
    and returns a tracking job ID.
    """
    # Generate unique UUID for this operation
    job_id = str(uuid.uuid4())
    
    # Secure random paths for processing
    safe_filename = f"{job_id}_{video.filename}"
    video_path = os.path.join(UPLOAD_DIR, safe_filename)
    output_path = os.path.join(OUTPUT_DIR, f"{job_id}_annotated.mp4")
    
    # Stream the file to disk avoiding memory limits completely
    try:
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(video.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save uploaded file: {str(e)}")
        
    # Initialize the job in the in-memory dict
    JOB_STORE[job_id] = {
        "job_id": job_id,
        "status": "pending",
        "progress_percent": 0.0,
        "result_path": None,
        "error": None
    }
    
    # Launch async background thread passing straight into our orchestrator
    background_tasks.add_task(process_video_task, job_id, video_path, model_path, output_path)
    
    return VideoAnalyzeResponse(
        job_id=job_id, 
        message="Video uploaded successfully. Processing started in the background."
    )


@app.get("/job/status/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str) -> JobStatusResponse:
    """
    Returns the current status of an analytics job based on tracking UUID.
    """
    if job_id not in JOB_STORE:
        raise HTTPException(status_code=404, detail=f"Job ID '{job_id}' not found in registry.")
        
    return JobStatusResponse(**JOB_STORE[job_id])


@app.get("/analytics/{job_id}")
async def get_analytics(job_id: str) -> Dict[str, Any]:
    """
    Returns the explicitly formatted JSON analytics summary payloads 
    associated exclusively with jobs that are actively 'completed'.
    """
    if job_id not in JOB_STORE:
        raise HTTPException(status_code=404, detail="Job ID not found.")
        
    job_state = JOB_STORE[job_id]
    
    if job_state["status"] != "completed":
        raise HTTPException(
            status_code=400, 
            detail=f"Job is not completed yet. Current status: {job_state['status']}"
        )
        
    result_path = job_state.get("result_path")
    if not result_path:
        raise HTTPException(status_code=500, detail="Result path missing from completed job state.")
        
    json_path = Path(result_path).with_suffix('.json')
    
    if not json_path.exists():
        raise HTTPException(status_code=404, detail="Analytics JSON report generation failed or file is missing.")
        
    with open(json_path, "r") as f:
        data = json.load(f)
        
    return data


@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Standard heartbeat and status check endpoint to confirm API stability.
    """
    return HealthResponse(
        api_version="1.0.0",
        status="ok",
        timestamp=datetime.now().isoformat()
    )
