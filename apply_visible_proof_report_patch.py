from pathlib import Path
import shutil

ROOT = Path.cwd()

def copy_file(rel):
    src = Path(__file__).resolve().parent / rel
    dst = ROOT / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    print(f"copied {rel}")

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

    if '<EvidencePack apiBase={API_BASE}' not in txt:
        block = """
              {activeTab === "evidence" && (
                <EvidencePack apiBase={API_BASE} />
              )}

"""
        txt = txt.replace(
            '              {activeTab === "queue" && (\n',
            block + '              {activeTab === "queue" && (\n'
        )

    if 'View Proof Report' not in txt:
        old = """                  <button className="action" onClick={() => runPreset("bundle")} disabled={isRunning}>
                    Run Bundle Task
                  </button>"""
        new = """                  <button className="action" onClick={() => runPreset("bundle")} disabled={isRunning}>
                    Run Bundle Task
                  </button>

                  <button
                    className="action proof-action"
                    onClick={() => {
                      setActiveTab("evidence");
                      scrollCenterToTop();
                    }}
                  >
                    View Proof Report
                  </button>"""
        txt = txt.replace(old, new)

    path.write_text(txt, encoding="utf-8")
    print("patched frontend/src/App.jsx")

def patch_css():
    path = ROOT / "frontend/src/style.css"
    add_path = Path(__file__).resolve().parent / "frontend/src/evidence-pack.css"
    add = add_path.read_text(encoding="utf-8")
    txt = path.read_text(encoding="utf-8")

    if "PPE v2 — Visible Proof Report" not in txt:
        txt += "\\n\\n" + add

    path.write_text(txt, encoding="utf-8")
    print("patched frontend/src/style.css")

def main():
    copy_file("frontend/src/pages/EvidencePack.jsx")
    patch_app_jsx()
    patch_css()
    print("\\nVisible Proof Report patch applied.")
    print("Refresh frontend. New left menu item: Proof Report")
    print("Home button added: View Proof Report")

if __name__ == "__main__":
    main()
