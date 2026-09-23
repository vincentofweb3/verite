from __future__ import annotations

import io
import re
from pathlib import Path

from .models import Scene


_SLUGLINE = re.compile(r"^(INT\.?|EXT\.?|INT\.?/EXT\.?|EXT\.?/INT\.?|I/E\.)\s+", re.I)
_CHARACTER = re.compile(r"^[A-Z][A-Z0-9 ._()'-]{1,38}$")
_TRANSITION = re.compile(r"^(CUT TO:|FADE OUT\.?|FADE IN:?|DISSOLVE TO:|SMASH CUT TO:)$", re.I)
_PAREN = re.compile(r"^\(.+\)$")


def extract_text(filename: str, content_type: str, payload: bytes) -> str:
    """Decode supported screenplay formats into text before structuring scenes."""
    suffix = Path(filename).suffix.lower()
    if suffix == ".pdf" or content_type == "application/pdf":
        try:
            from pypdf import PdfReader

            reader = PdfReader(io.BytesIO(payload))
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        except Exception as exc:  # pragma: no cover - depends on malformed PDFs
            raise ValueError(f"Could not read PDF: {exc}") from exc
    try:
        return payload.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError("The screenplay must be UTF-8 text or a readable PDF.") from exc


def parse_screenplay(text: str) -> list[Scene]:
    """Parse common screenplay/Fountain conventions into stable Scene objects.

    This performs structure extraction only. Entity and grounding passes belong to
    later milestones and are intentionally not inferred here.
    """
    lines = [line.rstrip() for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n")]
    scenes: list[Scene] = []
    current: dict[str, object] | None = None
    current_character: str | None = None
    pending_action: list[str] = []

    def finish_scene() -> None:
        nonlocal current, current_character, pending_action
        if current is None:
            return
        action = [item for item in current["action"] if item]  # type: ignore[index]
        dialogue = current["dialogue"]  # type: ignore[index]
        synopsis = next((item for item in action if item), "Scene begins.")
        dialogue_text = " ".join(entry["text"] for entry in dialogue)
        scenes.append(
            Scene(
                id=f"scene-{len(scenes) + 1:03d}",
                scene_number=len(scenes) + 1,
                slugline=str(current["slugline"]),
                synopsis=synopsis[:240],
                action=action,
                dialogue=dialogue,
                characters=sorted({entry["character"] for entry in dialogue}),
                props=_find_props(f"{' '.join(action)} {dialogue_text}"),
                locations=_find_locations(str(current["slugline"])),
            )
        )
        current = None
        current_character = None
        pending_action = []

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            current_character = None
            continue
        if _SLUGLINE.match(line) or line.upper().startswith("[INT."):
            finish_scene()
            current = {"slugline": line.strip("[]"), "action": [], "dialogue": []}
            continue
        if current is None:
            pending_action.append(line)
            continue
        if _TRANSITION.match(line):
            current["action"].append(line)  # type: ignore[index]
            current_character = None
            continue
        if line == line.upper() and _CHARACTER.match(line) and len(line.split()) <= 5 and not line.endswith(":"):
            current_character = line.title() if line.isupper() else line
            continue
        if current_character and _PAREN.match(line):
            current["action"].append(line)  # type: ignore[index]
            continue
        if current_character:
            current["dialogue"].append({"character": current_character, "text": line})  # type: ignore[index]
        else:
            current["action"].append(line)  # type: ignore[index]

    finish_scene()
    if not scenes:
        raise ValueError("No screenplay scenes found. Add INT./EXT. scene headings and try again.")
    return scenes


def _find_locations(slugline: str) -> list[str]:
    parts = re.split(r"\s+[—-]\s+|\s+-\s+", slugline, maxsplit=1)
    if len(parts) < 2:
        return []
    location = parts[0].split(maxsplit=1)[-1].strip(". ")
    return [location.title()] if location else []


def _find_props(action: str) -> list[str]:
    known = ("phone", "car", "lighter", "gun", "letter", "laptop", "keys", "camera", "book")
    lower = action.lower()
    return sorted({item for item in known if re.search(rf"\b{re.escape(item)}\b", lower)})
