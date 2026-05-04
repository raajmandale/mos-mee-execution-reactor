import hashlib
import mimetypes
from pathlib import Path


def generate_signature(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def detect_type(filename: str) -> dict:
    ext = Path(filename).suffix.lower()

    type_map = {
        ".jpg": ("image", "Image Flow"),
        ".jpeg": ("image", "Image Flow"),
        ".png": ("image", "Image Flow"),
        ".webp": ("image", "Image Flow"),
        ".zip": ("bundle", "Bundle Workload"),
        ".pdf": ("document", "Document Flow"),
        ".docx": ("document", "Document Flow"),
        ".txt": ("text", "Text Flow"),
        ".json": ("data", "Structured Data Flow"),
        ".csv": ("data", "Structured Data Flow"),
    }

    category, family = type_map.get(ext, ("unknown", "Generic Flow"))

    mime, _ = mimetypes.guess_type(filename)

    return {
        "category": category,
        "family": family,
        "extension": ext,
        "mime": mime or "application/octet-stream",
    }