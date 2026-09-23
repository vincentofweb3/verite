from __future__ import annotations

import json
import os
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .models import Project, ProjectCreate, ProjectDetail, Scene, ScriptSummary, utc_now


class Repository:
    """Persistence boundary: local JSON for development, Firestore when configured."""

    def __init__(self, data_dir: str | None = None):
        self.data_dir = Path(data_dir or os.getenv("DATA_DIR", "./data"))
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.upload_dir = self.data_dir / "uploads"
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._firestore = self._build_firestore()

    def _build_firestore(self):
        if not os.getenv("GCP_PROJECT_ID") and not os.getenv("GOOGLE_CLOUD_PROJECT"):
            return None
        from google.cloud import firestore

        return firestore.Client(
            project=os.getenv("GCP_PROJECT_ID") or os.getenv("GOOGLE_CLOUD_PROJECT"),
            database=os.getenv("FIRESTORE_DATABASE", "(default)"),
        )

    def create_project(self, payload: ProjectCreate, owner_id: str) -> Project:
        now = utc_now()
        project = Project(id=uuid.uuid4().hex, title=payload.title.strip(), owner_id=owner_id, status="empty", created_at=now, updated_at=now)
        self._write_project(project, [])
        return project

    def list_projects(self, owner_id: str) -> list[Project]:
        if self._firestore:
            documents = self._firestore.collection("projects").where("owner_id", "==", owner_id).stream()
            projects = [Project.model_validate(document.to_dict()) for document in documents]
            return sorted(projects, key=lambda item: item.updated_at, reverse=True)
        projects = [Project.model_validate(item) for item in self._read_all().values() if item["owner_id"] == owner_id]
        return sorted(projects, key=lambda item: item.updated_at, reverse=True)

    def get_project(self, project_id: str, owner_id: str) -> ProjectDetail | None:
        if self._firestore:
            reference = self._firestore.collection("projects").document(project_id)
            snapshot = reference.get()
            if not snapshot.exists:
                return None
            project = snapshot.to_dict()
            if not project or project.get("owner_id") != owner_id:
                return None
            scenes = [document.to_dict() for document in reference.collection("scripts").document("latest").collection("scenes").stream()]
            scenes.sort(key=lambda item: item["scene_number"])
            return ProjectDetail.model_validate({**project, "scenes": scenes, "processing_log": project.get("processing_log", [])})
        record = self._read_one(project_id)
        if not record or record["project"]["owner_id"] != owner_id:
            return None
        return ProjectDetail.model_validate({**record["project"], "scenes": record.get("scenes", []), "processing_log": record.get("processing_log", [])})

    def save_upload(self, project_id: str, filename: str, content_type: str, payload: bytes, owner_id: str) -> ScriptSummary:
        with self._lock:
            detail = self.get_project(project_id, owner_id)
            if not detail:
                raise KeyError(project_id)
            script_id = uuid.uuid4().hex
            safe_name = Path(filename).name or "screenplay.txt"
            destination = self.upload_dir / f"{project_id}-{script_id}-{safe_name}"
            destination.write_bytes(payload)
            summary = ScriptSummary(id=script_id, filename=safe_name, content_type=content_type or "application/octet-stream", size_bytes=len(payload), status="processing", uploaded_at=utc_now())
            self._upload_to_gcs(project_id, script_id, safe_name, payload, content_type)
            detail.script = summary
            detail.status = "processing"
            detail.scenes = []
            detail.updated_at = utc_now()
            detail.processing_log = [f"{_stamp()}  Upload received          -> {safe_name} ({len(payload):,} bytes)", "Processing screenplay structure..."]
            self._write_project(detail, detail.scenes)
            return summary

    def save_parsed(self, project_id: str, owner_id: str, scenes: list[Scene], log: list[str], script_id: str | None = None) -> ProjectDetail | None:
        with self._lock:
            detail = self.get_project(project_id, owner_id)
            if not detail or not detail.script:
                raise KeyError(project_id)
            if script_id and detail.script.id != script_id:
                return None
            detail.script.scenes_count = len(scenes)
            detail.script.status = "ready"
            detail.status = "ready"
            detail.updated_at = utc_now()
            detail.scenes = scenes
            detail.processing_log = log
            self._write_project(detail, scenes)
            return detail

    def save_error(self, project_id: str, owner_id: str, message: str, log: list[str], script_id: str | None = None) -> ProjectDetail | None:
        with self._lock:
            detail = self.get_project(project_id, owner_id)
            if not detail:
                raise KeyError(project_id)
            if script_id and detail.script and detail.script.id != script_id:
                return None
            detail.status = "error"
            if detail.script:
                detail.script.status = "error"
                detail.script.error = message
            detail.updated_at = utc_now()
            detail.processing_log = [*log, f"{_stamp()}  Script Parser            -> ERROR: {message}"]
            self._write_project(detail, detail.scenes)
            return detail

    def _write_project(self, project: Project | ProjectDetail, scenes: list[Scene]) -> None:
        processing_log = project.processing_log if isinstance(project, ProjectDetail) else []
        project_payload = project.model_dump(mode="json")
        project_payload.pop("scenes", None)
        project_payload.pop("processing_log", None)
        record = {"project": project_payload, "scenes": [item.model_dump(mode="json") for item in scenes], "processing_log": processing_log}
        with self._lock:
            destination = self.data_dir / f"{project.id}.json"
            temporary = self.data_dir / f".{project.id}.{uuid.uuid4().hex}.tmp"
            temporary.write_text(json.dumps(record, indent=2), encoding="utf-8")
            temporary.replace(destination)
        if self._firestore:
            parent = self._firestore.collection("projects").document(project.id)
            scene_collection = parent.collection("scripts").document("latest").collection("scenes")
            existing_scene_documents = list(scene_collection.stream())
            operations: list[tuple[str, object, dict[str, Any] | None]] = [
                ("delete", document.reference, None) for document in existing_scene_documents
            ]
            operations.extend(
                ("set", scene_collection.document(scene.id), scene.model_dump(mode="json"))
                for scene in scenes
            )
            for start in range(0, len(operations), 400):
                batch = self._firestore.batch()
                for operation, reference, payload in operations[start : start + 400]:
                    if operation == "delete":
                        batch.delete(reference)
                    else:
                        batch.set(reference, payload or {})
                batch.commit()
            parent.set({**record["project"], "processing_log": processing_log})

    def _read_all(self) -> dict[str, Any]:
        with self._lock:
            records: dict[str, Any] = {}
            for path in self.data_dir.glob("*.json"):
                try:
                    records[path.stem] = json.loads(path.read_text(encoding="utf-8"))["project"]
                except (OSError, json.JSONDecodeError, KeyError):
                    continue
            return records

    def _read_one(self, project_id: str) -> dict[str, Any] | None:
        with self._lock:
            path = self.data_dir / f"{project_id}.json"
            if not path.exists():
                return None
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                return None

    def _upload_to_gcs(self, project_id: str, script_id: str, filename: str, payload: bytes, content_type: str) -> None:
        bucket_name = os.getenv("GCS_BUCKET")
        if not bucket_name:
            return
        from google.cloud import storage

        blob = storage.Client().bucket(bucket_name).blob(f"projects/{project_id}/scripts/{script_id}/{filename}")
        blob.upload_from_string(payload, content_type=content_type or "application/octet-stream")


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%H:%M:%S")
