# PPE Patch Pack — Install Steps

Copy this patch over your existing `mos-mee-execution-reactor` repo.

## 1. Copy files

Place these files into the same relative paths:

- backend/app/engine/proof_engine.py
- backend/app/engine/evidence_export.py
- backend/app/api/proof.py
- frontend/src/pages/ProofMode.jsx
- docs/proof_reports/.gitkeep
- docs/PPE_UPGRADE_NOTES.md

## 2. Wire backend

In `backend/app/main.py`, add:

```python
from .api.proof import router as proof_router
```

Then after CORS middleware block, add:

```python
app.include_router(proof_router)
```

## 3. Wire frontend

In `frontend/src/App.jsx`, add at top:

```jsx
import ProofMode from "./pages/ProofMode.jsx";
```

Add to `RAIL_ITEMS`:

```jsx
["proof", "Proof Mode"],
```

Inside the focus content render area, add:

```jsx
{activeTab === "proof" && <ProofMode apiBase={API_BASE} />}
```

A safe place is before the existing `{activeTab === "execution" && (` block.

## 4. Add CSS

Append the contents of `frontend/src/ppe-proofmode.css` into `frontend/src/style.css`.

## 5. Test

Backend:
```bash
cd backend
uvicorn app.main:app --reload
```

Frontend:
```bash
cd frontend
npm run dev
```

Open the app and click `Proof Mode`.

## 6. API test

```bash
curl -X POST http://127.0.0.1:8000/proof/run-proof \
  -H "Content-Type: application/json" \
  -d "{\"benchmark\":\"A\",\"export_html\":true}"
```
