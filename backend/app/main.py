from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.run_proof import router as run_proof_router

app = FastAPI(
    title="Mandale-OS PPE Engine",
    version="3.0.0",
    description="Pattern Proof Engine — Authority Execution System"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(run_proof_router, prefix="/api")


@app.get("/")
def root():
    return {
        "system": "Mandale-OS PPE",
        "status": "running",
        "engine": "Pattern Proof Engine",
        "mode": "Signed Proof Authority Active"
    }


@app.get("/health")
def health():
    return {"status": "ok"}