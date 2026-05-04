import os
import json
import hashlib
from typing import Any

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa


# =========================
# KEY CONFIG
# =========================

KEY_DIR = "keys"
PRIVATE_KEY_PATH = os.path.join(KEY_DIR, "mos_ppe_private.pem")
PUBLIC_KEY_PATH = os.path.join(KEY_DIR, "mos_ppe_public.pem")


# =========================
# UTIL
# =========================

def _canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def _hash(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()


# =========================
# KEY MANAGEMENT
# =========================

def ensure_keys():
    os.makedirs(KEY_DIR, exist_ok=True)

    if not os.path.exists(PRIVATE_KEY_PATH) or not os.path.exists(PUBLIC_KEY_PATH):
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )

        public_key = private_key.public_key()

        # Save private key
        with open(PRIVATE_KEY_PATH, "wb") as f:
            f.write(
                private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                )
            )

        # Save public key
        with open(PUBLIC_KEY_PATH, "wb") as f:
            f.write(
                public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                )
            )


def load_private_key():
    with open(PRIVATE_KEY_PATH, "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None)


def load_public_key():
    with open(PUBLIC_KEY_PATH, "rb") as f:
        return serialization.load_pem_public_key(f.read())


# =========================
# EXPORTER CLASS
# =========================

class EvidenceExporter:

    def __init__(self):
        ensure_keys()
        self.private_key = load_private_key()

    def sign(self, payload: dict) -> dict:
        canonical = _canonical_json(payload)
        payload_hash = _hash(canonical)

        signature = self.private_key.sign(
            canonical.encode(),
            padding.PKCS1v15(),
            hashes.SHA256()
        )

        return {
            "payload": payload,
            "hash": payload_hash,
            "signature": signature.hex(),
            "algorithm": "RSA-2048-SHA256"
        }