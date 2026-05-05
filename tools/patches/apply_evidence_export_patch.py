from pathlib import Path
import shutil

ROOT = Path.cwd()

FILES = [
    "backend/app/evidence_export.py",
    "frontend/src/pages/EvidencePack.jsx",
]

def copy_file(rel):
    src = Path(__file__).resolve().parent / rel
    dst = ROOT / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    print(f"copied {rel}")

def patch_main_py():
    path = ROOT / "backend/app/main.py"
    txt = path.read_text(encoding="utf-8")

    if "HTMLResponse" not in txt:
        txt = txt.replace(
            "from fastapi.middleware.cors import CORSMiddleware\n",
            "from fastapi.middleware.cors import CORSMiddleware\nfrom fastapi.responses import HTMLResponse\n"
        )

    if "from .evidence_export import REPORT_DIR, export_evidence_pack" not in txt:
        marker = "from .runtime_manager import (\n"
        txt = txt.replace(
            marker,
            "from .evidence_export import REPORT_DIR, export_evidence_pack\n" + marker
        )

    endpoint = """
@app.post("/evidence/export-last")
def export_last_evidence():
    state = load_state()
    return export_evidence_pack(state)


@app.get("/evidence/report/{filename}", response_class=HTMLResponse)
def read_evidence_report(filename: str):
    safe_name = Path(filename).name
    path = REPORT_DIR / safe_name
    if not path.exists() or path.suffix.lower() != ".html":
        return HTMLResponse("<h1>Evidence report not found</h1>", status_code=404)
    return HTMLResponse(path.read_text(encoding="utf-8"))
"""

    if '@app.post("/evidence/export-last")' not in txt:
        txt = txt.rstrip() + "\n\n" + endpoint + "\n"

    path.write_text(txt, encoding="utf-8")
    print("patched backend/app/main.py")

def patch_app_jsx():
    path = ROOT / "frontend/src/App.jsx"
    txt = path.read_text(encoding="utf-8")

    if 'import EvidencePack from "./pages/EvidencePack.jsx";' not in txt:
        txt = txt.replace(
            'import { useEffect, useMemo, useRef, useState } from "react";\n',
            'import { useEffect, useMemo, useRef, useState } from "react";\nimport EvidencePack from "./pages/EvidencePack.jsx";\n'
        )

    if '["evidence", "Proof Report"],' not in txt:
        txt = txt.replace(
            '  ["intel", "System Intel"],\n',
            '  ["intel", "System Intel"],\n  ["evidence", "Proof Report"],\n'
        )

    if 'evidence: "Proof Report",' not in txt:
        txt = txt.replace(
            '    intel: "System Intelligence",\n',
            '    intel: "System Intelligence",\n    evidence: "Proof Report",\n'
        )

    evidence_block = """
              {activeTab === "evidence" && (
                <EvidencePack apiBase={API_BASE} />
              )}

"""

    if '<EvidencePack apiBase={API_BASE}' not in txt:
        txt = txt.replace(
            '              {activeTab === "queue" && (\n',
            evidence_block + '              {activeTab === "queue" && (\n'
        )

    path.write_text(txt, encoding="utf-8")
    print("patched frontend/src/App.jsx")

def patch_css():
    path = ROOT / "frontend/src/style.css"
    add = (Path(__file__).resolve().parent / "frontend/src/evidence-pack.css").read_text(encoding="utf-8")
    txt = path.read_text(encoding="utf-8")

    if "PPE v2 — Evidence Pack Export" not in txt:
        path.write_text(txt + "\n\n" + add, encoding="utf-8")
        print("patched frontend/src/style.css")
    else:
        print("frontend/src/style.css already patched")

def main():
    for rel in FILES:
        copy_file(rel)
    patch_main_py()
    patch_app_jsx()
    patch_css()
    print("\nEvidence Export patch applied.")
    print("Restart backend and refresh frontend.")
    print("New menu item: Proof Report")

if __name__ == "__main__":
    main()
