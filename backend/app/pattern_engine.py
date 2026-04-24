from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any


IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".svg"}
DOC_EXTS = {".pdf", ".doc", ".docx", ".txt", ".md", ".rtf"}
CODE_EXTS = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".c", ".cpp", ".cs",
    ".go", ".rs", ".php", ".rb", ".swift", ".kt", ".sql", ".json", ".xml",
    ".yaml", ".yml", ".html", ".css", ".sh"
}
ARCHIVE_EXTS = {".zip", ".rar", ".7z", ".tar", ".gz"}

FAMILY_LABELS = {
    "image": "Image Flow",
    "document": "Document Flow",
    "code": "Code Flow",
    "bundle": "Bundle Workload",
    "generic": "Generic Flow",
}


def normalize_ext(filename: str) -> str:
    return Path(filename).suffix.lower().strip()


def tokenize_name(filename: str) -> list[str]:
    stem = Path(filename).stem.lower()
    raw = stem.replace("-", " ").replace("_", " ").replace(".", " ").split()
    tokens = [t for t in raw if t and len(t) > 1]
    return tokens[:10]


def family_from_ext(ext: str) -> str:
    if ext in IMAGE_EXTS:
        return "image"
    if ext in DOC_EXTS:
        return "document"
    if ext in CODE_EXTS:
        return "code"
    if ext in ARCHIVE_EXTS:
        return "bundle"
    return "generic"


def size_bucket(size_bytes: int) -> str:
    if size_bytes <= 128 * 1024:
        return "tiny"
    if size_bytes <= 2 * 1024 * 1024:
        return "small"
    if size_bytes <= 10 * 1024 * 1024:
        return "medium"
    return "large"


def summarize_zip_entries(filenames: list[str]) -> dict[str, Any]:
    if not filenames:
        return {"inner_count": 0, "inner_families": [], "hybrid": False}

    families = [family_from_ext(normalize_ext(name)) for name in filenames]
    counted = Counter(families)
    inner_families = sorted(counted.keys())
    return {
        "inner_count": len(filenames),
        "inner_families": inner_families,
        "hybrid": len(inner_families) > 1,
    }


def build_signature(
    *,
    filename: str,
    size_bytes: int,
    zip_info: dict[str, Any] | None = None,
) -> dict[str, Any]:
    ext = normalize_ext(filename)
    family = family_from_ext(ext)
    tokens = tokenize_name(filename)
    zip_info = zip_info or {"inner_count": 0, "inner_families": [], "hybrid": False}

    label = FAMILY_LABELS.get(family, "Generic Flow")
    if family == "bundle" and zip_info.get("hybrid"):
        label = "Hybrid Pipeline"

    return {
        "label": label,
        "family": family,
        "ext": ext,
        "size_bucket": size_bucket(size_bytes),
        "name_tokens": tokens,
        "zip_info": {
            "inner_count": int(zip_info.get("inner_count", 0)),
            "inner_families": list(zip_info.get("inner_families", [])),
            "hybrid": bool(zip_info.get("hybrid", False)),
        },
    }


def signature_key(signature: dict[str, Any]) -> str:
    return f"{signature['family']}:{signature['ext']}:{signature['size_bucket']}"


def cluster_key(signature: dict[str, Any]) -> str:
    return f"{signature['family']}:{signature['size_bucket']}"


def token_overlap_score(a: list[str], b: list[str]) -> float:
    if not a or not b:
        return 0.0
    sa = set(a)
    sb = set(b)
    return len(sa & sb) / max(len(sa | sb), 1)


def signature_similarity(sig: dict[str, Any], mem: dict[str, Any]) -> float:
    score = 0.0

    if sig["family"] == mem.get("family"):
        score += 0.40
    if sig["ext"] == mem.get("ext"):
        score += 0.22
    if sig["size_bucket"] == mem.get("size_bucket"):
        score += 0.16

    score += 0.16 * token_overlap_score(sig.get("name_tokens", []), mem.get("name_tokens", []))

    sig_zip = sig.get("zip_info", {})
    mem_zip = mem.get("zip_info", {})
    if sig_zip.get("hybrid") and mem_zip.get("hybrid"):
        score += 0.06

    return min(score, 1.0)


def match_signature(signature: dict[str, Any], memory: dict[str, Any]) -> dict[str, Any]:
    if not memory:
        return {
            "kind": "none",
            "confidence": "Low",
            "matched_key": None,
            "matched_entry": None,
            "score": 0.0,
        }

    key = signature_key(signature)
    if key in memory:
        return {
            "kind": "exact",
            "confidence": "High",
            "matched_key": key,
            "matched_entry": memory[key],
            "score": 1.0,
        }

    best_key = None
    best_entry = None
    best_score = 0.0

    for mem_key, entry in memory.items():
        score = signature_similarity(signature, entry)
        if score > best_score:
            best_key = mem_key
            best_entry = entry
            best_score = score

    if best_score >= 0.74:
        return {
            "kind": "partial",
            "confidence": "High" if best_score >= 0.88 else "Medium",
            "matched_key": best_key,
            "matched_entry": best_entry,
            "score": best_score,
        }

    return {
        "kind": "none",
        "confidence": "Low",
        "matched_key": None,
        "matched_entry": None,
        "score": best_score,
    }


def build_linear_nodes(label: str, match_kind: str) -> list[dict[str, str]]:
    state_map = {
        "exact": ["hot", "hot", "hot", "hot", "hot"],
        "partial": ["hot", "hot", "warm", "warm", "warm"],
        "none": ["hot", "warm", "cold", "cold", "cold"],
    }
    states = state_map.get(match_kind, state_map["none"])

    return [
        {"short": "IN", "label": "Input", "state": states[0]},
        {"short": "N", "label": "Normalize", "state": states[1]},
        {"short": "M", "label": "Match", "state": states[2]},
        {"short": "R", "label": "Reuse", "state": states[3]},
        {"short": "OUT", "label": label, "state": states[4]},
    ]


def decide_route(signature: dict[str, Any], match: dict[str, Any]) -> dict[str, Any]:
    family = signature["family"]
    label = signature["label"]

    if family == "bundle" and signature["zip_info"].get("hybrid"):
        route_type = "hybrid"
        mode = "hybrid"
        decision = "Hybrid Routing"
        reuse = 84 if match["kind"] != "none" else 40
        confidence = "High" if match["kind"] != "none" else "Medium"
        top_nodes = [
            {"short": "IN", "label": "Bundle Input", "state": "hot"},
            {"short": "A", "label": "Image Route", "state": "hot"},
            {"short": "B", "label": "Data Route", "state": "warm"},
        ]
        bottom_nodes = [
            {"short": "M", "label": "Merge", "state": "warm"},
            {"short": "OUT", "label": label, "state": "hot"},
        ]
        nodes = []
        notes = [
            "Mixed workload bundle detected.",
            "Hybrid route selected from inner family spread.",
            "Memory-aware merge path prepared.",
        ]
        console = [
            "[reactor] hybrid bundle detected",
            "[signature] multiple family traces found",
            "[router] split route → merge route armed",
        ]
    else:
        route_type = "linear"
        top_nodes = None
        bottom_nodes = None
        nodes = build_linear_nodes(label, match["kind"])

        if match["kind"] == "exact":
            mode = "reused"
            decision = "Pattern Reused"
            reuse = 91 if family == "image" else 88
            confidence = "High"
            notes = [
                "Exact structural signature match found.",
                "Known execution family recalled.",
                "Reuse path promoted as active route.",
            ]
            console = [
                "[signature] exact match found",
                "[memory] promoting known execution family",
                "[router] reused path locked",
            ]
        elif match["kind"] == "partial":
            mode = "partial"
            decision = "Partial Match"
            reuse = 75 if family == "image" else 68
            confidence = match["confidence"]
            notes = [
                "Invariant signature match found.",
                "Family-level memory overlap detected.",
                "Partial reuse selected for current route.",
            ]
            console = [
                "[signature] partial family overlap",
                "[memory] structural recall available",
                "[router] partial reuse path selected",
            ]
        else:
            mode = "learning"
            decision = "Learning"
            reuse = 0
            confidence = "Low"
            notes = [
                "No prior route selected.",
                "New structural family entering reactor.",
                "Memory will be updated after execution.",
            ]
            console = [
                "[reactor] standby",
                "[memory] no active recall route",
                "[graph] awaiting file upload",
            ]

    est_time = estimate_time(signature, mode)

    return {
        "workflow": label,
        "family": signature["family"],
        "reuse": reuse,
        "confidence": confidence,
        "time": est_time,
        "decision": decision,
        "mode": mode,
        "systemState": system_state_from_mode(mode),
        "routeType": route_type,
        "nodes": nodes,
        "topNodes": top_nodes,
        "bottomNodes": bottom_nodes,
        "notes": notes,
        "console": console,
    }


def estimate_time(signature: dict[str, Any], mode: str) -> int:
    base = {
        "tiny": 114,
        "small": 238,
        "medium": 548,
        "large": 980,
    }.get(signature["size_bucket"], 320)

    if mode == "reused":
        return int(base * 0.28)
    if mode == "partial":
        return int(base * 0.55)
    if mode == "hybrid":
        return int(base * 0.78)
    return base


def system_state_from_mode(mode: str) -> str:
    if mode == "reused":
        return "High Intelligence"
    if mode == "partial":
        return "Adaptive"
    if mode == "hybrid":
        return "Multi Routing"
    return "Learning"


def update_memory(memory: dict[str, Any], signature: dict[str, Any], route: dict[str, Any]) -> dict[str, Any]:
    memory = dict(memory or {})
    key = signature_key(signature)

    existing = memory.get(key, {})
    seen = int(existing.get("seen", 0)) + 1
    best_reuse = max(int(existing.get("best_reuse", 0)), int(route["reuse"]))

    memory[key] = {
        "label": signature["label"],
        "family": signature["family"],
        "ext": signature["ext"],
        "size_bucket": signature["size_bucket"],
        "name_tokens": signature["name_tokens"],
        "zip_info": signature["zip_info"],
        "seen": seen,
        "best_reuse": best_reuse,
        "last_confidence": route["confidence"],
        "last_decision": route["decision"],
        "cluster_key": cluster_key(signature),
    }
    return memory