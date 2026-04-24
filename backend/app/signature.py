import hashlib


def hash_dict(d: dict) -> str:
    raw = str(sorted(d.items())).encode()
    return hashlib.sha256(raw).hexdigest()[:16]


def build_step_signature(step_name: str, input_kind: str, extra: dict = None):
    extra = extra or {}

    signature = {
        "step_type": step_name.lower().replace(" ", "_"),
        "input_kind": input_kind,
        "features": extra,
    }

    signature["feature_hash"] = hash_dict(signature)

    return signature