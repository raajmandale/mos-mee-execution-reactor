import json
import hashlib
import sys


def sha256(data):
    return hashlib.sha256(data.encode()).hexdigest()


def load_file(path):
    with open(path, "r") as f:
        return json.load(f)


def verify(proof_file):
    data = load_file(proof_file)

    print("\n🔍 Verifying Proof...\n")

    # Required fields
    required = ["proofId", "inputHash", "finalHash", "decision", "confidenceValue"]

    for key in required:
        if key not in data:
            print(f"❌ Missing field: {key}")
            return

    # Recompute final hash
    recomputed = sha256(data["inputHash"] + data["decision"])

    if recomputed == data["finalHash"]:
        print("✅ Integrity Check: PASSED")
    else:
        print("❌ Integrity Check: FAILED")
        return

    # Confidence sanity check
    confidence = data.get("confidenceValue", 0)

    if confidence >= 80:
        print(f"✅ Confidence: HIGH ({confidence}%)")
    else:
        print(f"⚠️ Confidence: LOW ({confidence}%)")

    print("\n📊 Proof Summary")
    print(f"Proof ID   : {data['proofId']}")
    print(f"Decision   : {data['decision']}")
    print(f"Integrity  : VERIFIED")

    print("\n🚀 RESULT: PROOF VALID\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python verify_proof.py <proof.json>")
    else:
        verify(sys.argv[1])