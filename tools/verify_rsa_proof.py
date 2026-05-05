import json
import sys
import hashlib
from pathlib import Path

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding


def canonical_json(data):
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def sha256_text(text):
    return hashlib.sha256(text.encode()).hexdigest()


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_public_key(path):
    with open(path, "rb") as f:
        return serialization.load_pem_public_key(f.read())


def verify_signature(public_key, payload, signature_hex):
    public_key.verify(
        bytes.fromhex(signature_hex),
        canonical_json(payload).encode(),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH,
        ),
        hashes.SHA256(),
    )


def verify_proof(proof_path, public_key_path):
    signed_export = load_json(proof_path)
    public_key = load_public_key(public_key_path)

    signature = signed_export.get("signature")
    if not signature:
        print("❌ Missing RSA signature")
        return False

    clean_payload = dict(signed_export)
    clean_payload.pop("signature", None)
    clean_payload.pop("signature_type", None)
    clean_payload.pop("public_key_file", None)
    clean_payload.pop("verification", None)

    try:
        verify_signature(public_key, clean_payload, signature)
        signature_valid = True
    except Exception as e:
        print("❌ Signature check failed")
        print(str(e))
        return False

    integrity_payload = clean_payload.get("integrity_payload")
    integrity_hash = clean_payload.get("integrity_hash")

    if not integrity_payload or not integrity_hash:
        print("❌ Missing integrity fields")
        return False

    recalculated_integrity = sha256_text(canonical_json(integrity_payload))

    if recalculated_integrity != integrity_hash:
        print("❌ Integrity hash mismatch")
        return False

    proof = clean_payload.get("proof", {})

    print("\n✅ RSA PROOF VERIFIED")
    print("--------------------------------")
    print(f"Proof ID : {proof.get('proof_id')}")
    print(f"Run ID   : {proof.get('run_id')}")
    print(f"Signature: RSA-PSS-SHA256")
    print(f"Integrity: MATCHED")
    print("--------------------------------\n")

    return True


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage:")
        print("python tools/verifier/verify_rsa_proof.py <signed_proof.json> <mos_ppe_public.pem>")
        sys.exit(1)

    proof_file = Path(sys.argv[1])
    public_key_file = Path(sys.argv[2])

    if not proof_file.exists():
        print(f"❌ Proof file not found: {proof_file}")
        sys.exit(1)

    if not public_key_file.exists():
        print(f"❌ Public key file not found: {public_key_file}")
        sys.exit(1)

    ok = verify_proof(proof_file, public_key_file)
    sys.exit(0 if ok else 2)