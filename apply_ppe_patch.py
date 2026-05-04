from pathlib import Path
import shutil

ROOT = Path.cwd()

PATCH_FILES = [
    "backend/app/engine/proof_engine.py",
    "backend/app/engine/evidence_export.py",
    "backend/app/api/proof.py",
    "frontend/src/pages/ProofMode.jsx",
    "docs/proof_reports/.gitkeep",
    "docs/PPE_UPGRADE_NOTES.md",
]

def copy_file(rel):
    src = Path(__file__).resolve().parent / rel
    dst = ROOT / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    print(f"copied {rel}")

def patch_main():
    path = ROOT / "backend/app/main.py"
    txt = path.read_text(encoding="utf-8")

    if "proof_router" not in txt:
        marker = "from fastapi.middleware.cors import CORSMiddleware\n"
        txt = txt.replace(marker, marker + "\nfrom .api.proof import router as proof_router\n")

    if "app.include_router(proof_router)" not in txt:
        marker = "    allow_headers=[\"*\"],\n)\n"
        txt = txt.replace(marker, marker + "\n\napp.include_router(proof_router)\n")

    path.write_text(txt, encoding="utf-8")
    print("patched backend/app/main.py")

def patch_appjsx():
    path = ROOT / "frontend/src/App.jsx"
    txt = path.read_text(encoding="utf-8")

    if 'import ProofMode from "./pages/ProofMode.jsx";' not in txt:
        txt = txt.replace(
            'import { useEffect, useMemo, useRef, useState } from "react";\n',
            'import { useEffect, useMemo, useRef, useState } from "react";\nimport ProofMode from "./pages/ProofMode.jsx";\n'
        )

    if '["proof", "Proof Mode"],' not in txt:
        txt = txt.replace(
            '  ["execution", "Execution"],\n',
            '  ["execution", "Execution"],\n  ["proof", "Proof Mode"],\n'
        )

    insert = '              {activeTab === "proof" && <ProofMode apiBase={API_BASE} />}\n\n'
    if '<ProofMode apiBase={API_BASE}' not in txt:
        txt = txt.replace(
            '              {activeTab === "execution" && (\n',
            insert + '              {activeTab === "execution" && (\n'
        )

    path.write_text(txt, encoding="utf-8")
    print("patched frontend/src/App.jsx")

def patch_css():
    css_path = ROOT / "frontend/src/style.css"
    add_path = Path(__file__).resolve().parent / "frontend/src/ppe-proofmode.css"
    txt = css_path.read_text(encoding="utf-8")
    add = add_path.read_text(encoding="utf-8")
    if "PPE v2 — Proof Mode" not in txt:
        css_path.write_text(txt + "\n\n" + add, encoding="utf-8")
        print("patched frontend/src/style.css")
    else:
        print("frontend/src/style.css already patched")

def main():
    for rel in PATCH_FILES:
        copy_file(rel)
    patch_main()
    patch_appjsx()
    patch_css()
    print("\nPPE patch applied. Start backend + frontend and open Proof Mode.")

if __name__ == "__main__":
    main()
