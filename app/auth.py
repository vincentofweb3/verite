from __future__ import annotations

import json
import os
from functools import lru_cache

from fastapi import Header, HTTPException, status

from .models import User


@lru_cache(maxsize=1)
def firebase_web_config() -> dict[str, str]:
    try:
        value = json.loads(os.getenv("FIREBASE_WEB_CONFIG", "{}"))
        return value if isinstance(value, dict) else {}
    except json.JSONDecodeError:
        return {}


async def current_user(authorization: str | None = Header(default=None)) -> User:
    mode = os.getenv("AUTH_MODE", "local").lower()
    if mode in {"local", "off"}:
        return User(id="local-demo", email="demo@verite.local", name="Demo workspace")
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sign in is required.")
    token = authorization.split(" ", 1)[1].strip()
    try:
        import firebase_admin
        from firebase_admin import auth

        if not firebase_admin._apps:  # type: ignore[attr-defined]
            firebase_admin.initialize_app()
        decoded = auth.verify_id_token(token)
        return User(id=decoded["uid"], email=decoded.get("email"), name=decoded.get("name"))
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication token.") from exc
