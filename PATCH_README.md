# M-OS PPE — Evidence Pack Export Patch

This patch adds a simple human-readable proof export layer.

## What it adds

Backend:
- `backend/app/evidence_export.py`
- `POST /evidence/export-last`
- `GET /evidence/report/{filename}`

Frontend:
- `frontend/src/pages/EvidencePack.jsx`
- New left menu item: `Proof Report`

Reports generated into:
- `docs/proof_reports/*.json`
- `docs/proof_reports/*.md`
- `docs/proof_reports/*.html`

## Install

Extract this ZIP into your existing `mos-mee-execution-reactor` repo root.

Run:

```powershell
python apply_evidence_export_patch.py
```

Restart backend:

```powershell
cd backend
python -m uvicorn app.main:app --reload
```

Frontend should hot-reload. If not:

```powershell
cd frontend
npm run dev
```

## Test

1. Run any demo/upload first.
2. Open left menu: `Proof Report`
3. Click: `Generate Evidence Pack`

Expected:
- Human-readable proof report appears in UI.
- Report files appear in `docs/proof_reports/`.
