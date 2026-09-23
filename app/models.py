from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field, field_validator


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class User(BaseModel):
    id: str
    email: str | None = None
    name: str | None = None


class ProjectCreate(BaseModel):
    title: str = Field(min_length=1, max_length=160)

    @field_validator("title")
    @classmethod
    def title_is_not_whitespace(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Project title is required.")
        return value


class Scene(BaseModel):
    id: str
    scene_number: int
    slugline: str
    synopsis: str
    action: list[str] = Field(default_factory=list)
    dialogue: list[dict[str, str]] = Field(default_factory=list)
    characters: list[str] = Field(default_factory=list)
    props: list[str] = Field(default_factory=list)
    locations: list[str] = Field(default_factory=list)


class ScriptSummary(BaseModel):
    id: str
    filename: str
    content_type: str
    size_bytes: int
    status: Literal["uploaded", "processing", "ready", "error"]
    error: str | None = None
    uploaded_at: datetime
    scenes_count: int = 0


class Project(BaseModel):
    id: str
    title: str
    owner_id: str
    status: Literal["empty", "processing", "ready", "error"]
    created_at: datetime
    updated_at: datetime
    script: ScriptSummary | None = None


class ProjectDetail(Project):
    scenes: list[Scene] = Field(default_factory=list)
    processing_log: list[str] = Field(default_factory=list)
