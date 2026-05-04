from fastapi import APIRouter, UploadFile, File
from fastapi.responses import StreamingResponse

from app.core.execution_builder import build_execution
from app.core.proof_engine import build_proof_zip

router = APIRouter()


@router.post("/upload-react")
async def upload_react(file: UploadFile = File(...)):
    content = await file.read()

    execution = build_execution(content, file.filename)

    return {
        "status": "ok",
        "execution": execution
    }


@router.post("/upload-proof")
async def upload_proof(file: UploadFile = File(...)):
    content = await file.read()

    execution = build_execution(content, file.filename)

    zip_buffer = build_proof_zip(execution)

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename=proof_{file.filename}.zip"},
    )