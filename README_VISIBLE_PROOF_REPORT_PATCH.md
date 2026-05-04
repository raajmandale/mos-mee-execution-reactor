# Visible Proof Report Patch

This patch fixes the main usability problem:

A non-technical person must clearly see where the proof is.

## Adds

- Left menu item: **Proof Report**
- Home button: **View Proof Report**
- Simple Proof Report screen
- 4-step explanation:
  1. Run/upload file
  2. M-OS detects pattern
  3. M-OS reuses known path
  4. Evidence report is generated

## Install

Extract inside repo root:

```powershell
python apply_visible_proof_report_patch.py
```

Refresh frontend:

```text
http://localhost:5173
```

## Test

1. Click `Run Bundle Task`
2. Click `View Proof Report`
3. Click `Generate Proof Report`
