from __future__ import annotations

import logging
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .auth import current_user, firebase_web_config
from .models import Project, ProjectCreate, ProjectDetail, User
from .parser import extract_text, parse_screenplay
from .storage import Repository

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger("verite")
app = FastAPI(title="Vérité", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=[origin.strip() for origin in os.getenv("CORS_ORIGINS", "*").split(",")], allow_credentials=True, allow_methods=["GET", "POST"], allow_headers=["*"])
repo = Repository()
processing_executor = ThreadPoolExecutor(max_workers=int(os.getenv("PROCESSING_WORKERS", "2")), thread_name_prefix="verite-parser")
frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
app.mount("/assets", StaticFiles(directory=frontend_dir / "assets"), name="assets")


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok", "service": "verite"}


@app.get("/api/auth/config")
async def auth_config() -> dict[str, object]:
    return {"mode": os.getenv("AUTH_MODE", "local"), "firebase": firebase_web_config()}


@app.get("/api/projects", response_model=list[Project])
async def list_projects(user: User = Depends(current_user)) -> list[Project]:
    return repo.list_projects(user.id)


@app.post("/api/projects", response_model=Project, status_code=status.HTTP_201_CREATED)
async def create_project(payload: ProjectCreate, user: User = Depends(current_user)) -> Project:
    return repo.create_project(payload, user.id)


@app.get("/api/projects/{project_id}", response_model=ProjectDetail)
async def get_project(project_id: str, user: User = Depends(current_user)) -> ProjectDetail:
    project = repo.get_project(project_id, user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")
    return project


@app.post("/api/projects/{project_id}/scripts", response_model=ProjectDetail, status_code=status.HTTP_201_CREATED)
async def upload_script(project_id: str, file: UploadFile = File(...), user: User = Depends(current_user)) -> ProjectDetail:
    filename = Path(file.filename or "screenplay.txt").name
    suffix = Path(filename).suffix.lower()
    if suffix not in {".txt", ".fountain", ".pdf"}:
        raise HTTPException(status_code=415, detail="Unsupported file type. Upload a PDF, Fountain, or .txt screenplay.")
    payload = await file.read()
    if not payload:
        raise HTTPException(status_code=400, detail="The screenplay file is empty.")
    max_upload_bytes = int(os.getenv("MAX_UPLOAD_BYTES", str(25 * 1024 * 1024)))
    if len(payload) > max_upload_bytes:
        raise HTTPException(status_code=413, detail=f"The screenplay exceeds the {max_upload_bytes // (1024 * 1024)} MB upload limit.")
    try:
        summary = repo.save_upload(project_id, filename, file.content_type or "text/plain", payload, user.id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Project not found.") from exc
    processing_executor.submit(
        _process_uploaded_script,
        project_id,
        user.id,
        summary.id,
        filename,
        file.content_type or "text/plain",
        payload,
    )
    detail = repo.get_project(project_id, user.id)
    assert detail is not None
    return detail


def _process_uploaded_script(project_id: str, owner_id: str, script_id: str, filename: str, content_type: str, payload: bytes) -> None:
    detail = repo.get_project(project_id, owner_id)
    if not detail or not detail.script or detail.script.id != script_id:
        return
    try:
        scenes = parse_screenplay(extract_text(filename, content_type, payload))
        log = [
            *detail.processing_log[:1],
            f"{_time()}  Script Parser            -> {len(scenes)} scene{'s' if len(scenes) != 1 else ''} extracted",
            f"{_time()}  Script Parser            -> Parsed structure ready for review",
        ]
        repo.save_parsed(project_id, owner_id, scenes, log, script_id=script_id)
    except ValueError as exc:
        logger.info("Parsing failed for %s: %s", project_id, exc)
        repo.save_error(project_id, owner_id, str(exc), detail.processing_log, script_id=script_id)
    except Exception as exc:  # pragma: no cover - defensive production boundary
        logger.exception("Unexpected processing failure for %s", project_id)
        repo.save_error(project_id, owner_id, f"Unexpected processing failure: {exc}", detail.processing_log, script_id=script_id)


@app.get("/{path:path}", include_in_schema=False)
async def frontend(path: str = "") -> FileResponse:
    return FileResponse(frontend_dir / "index.html")


def _time() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).strftime("%H:%M:%S")
