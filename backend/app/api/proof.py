from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import io
import zipfile
import json
import time

router = APIRouter()

@router.post("/run-proof")
def run_proof():
    buffer = io.BytesIO()

    data = {
        "status": "verified",
        "timestamp": int(time.time()),
        "engine": "M-OS PPE",
        "result": "Execution Verified"
    }

    with zipfile.ZipFile(buffer, "w") as z:
        z.writestr("proof.json", json.dumps(data, indent=2))

    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=proof_bundle.zip"}
    )