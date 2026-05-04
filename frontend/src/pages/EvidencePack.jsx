import { useState } from "react";

export default function EvidencePack({ apiBase = "http://127.0.0.1:8000" }) {
  const [loading, setLoading] = useState(false);
  const [pack, setPack] = useState(null);
  const [error, setError] = useState("");

  async function generatePack() {
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`${apiBase}/evidence/export-last`, { method: "POST" });
      if (!res.ok) throw new Error(`Evidence export failed: ${res.status}`);
      const json = await res.json();
      setPack(json);
    } catch (err) {
      setError(String(err));
    } finally {
      setLoading(false);
    }
  }

  const proof = pack?.proof;

  return (
    <section className="section-panel evidence-panel">
      <div className="section-head">
        <div>
          <div className="hero-kicker">PPE v2 • SIMPLE PROOF VIEW</div>
          <div className="section-title">Proof Report</div>
          <div className="section-sub">
            Simple explanation for everyone: what was tested, what M-OS recognized,
            what it reused, and what evidence was generated.
          </div>
        </div>
        <div className="pill reused">Human-Readable Evidence</div>
      </div>

      <div className="simple-proof-steps">
        <div className="simple-step"><b>1</b><span>Run or upload a file</span></div>
        <div className="simple-step"><b>2</b><span>M-OS detects the pattern</span></div>
        <div className="simple-step"><b>3</b><span>It reuses a known path</span></div>
        <div className="simple-step"><b>4</b><span>Proof report is created</span></div>
      </div>

      <div className="actions evidence-actions">
        <button className="action primary" onClick={generatePack} disabled={loading}>
          {loading ? "Generating Proof Report..." : "Generate Proof Report"}
        </button>
      </div>

      {error && <div className="proof-error">{error}</div>}

      {!proof && (
        <div className="proof-empty">
          First click <b>Run Demo</b> or <b>Run Bundle Task</b> from Command. Then return here and click
          <b> Generate Proof Report</b>. This screen converts technical runtime data into a simple
          report that a non-technical person can understand.
        </div>
      )}

      {proof && (
        <div className="human-report">
          <div className="human-hero">
            <div>
              <div className="hero-kicker">WHAT HAPPENED?</div>
              <h2>M-OS recognized known work.</h2>
              <p>{proof.simpleExplanation}</p>
            </div>
            <div className="human-badge">{proof.reusePercent}% Reuse</div>
          </div>

          <div className="proof-grid">
            <div className="metric-card proof-metric">
              <div className="metric-label">Tested File</div>
              <div className="metric-value small-value">{proof.sourceFile}</div>
            </div>
            <div className="metric-card proof-metric">
              <div className="metric-label">Detected Work</div>
              <div className="metric-value small-value">{proof.workflow}</div>
            </div>
            <div className="metric-card proof-metric">
              <div className="metric-label">Decision</div>
              <div className="metric-value small-value">{proof.decision}</div>
            </div>
            <div className="metric-card proof-metric">
              <div className="metric-label">Saved Time</div>
              <div className="metric-value">{proof.savedMs} ms</div>
            </div>
          </div>

          <div className="plain-card">
            <h3>Meaning in simple words</h3>
            <p>{proof.commonMeaning}</p>
          </div>

          <div className="plain-card">
            <h3>Route path</h3>
            <div className="human-route">
              {(proof.nodes || []).map((node, idx) => (
                <span key={`${node.short || node.label}-${idx}`}>
                  {node.label || node.short}
                  {idx < proof.nodes.length - 1 ? " → " : ""}
                </span>
              ))}
            </div>
          </div>

          <div className="plain-card">
            <h3>Generated evidence files</h3>
            <div className="file-list">
              <div><b>JSON:</b> <code>{pack.files?.json}</code></div>
              <div><b>Markdown:</b> <code>{pack.files?.markdown}</code></div>
              <div><b>HTML:</b> <code>{pack.files?.html}</code></div>
            </div>
          </div>

          <div className="plain-card warning">
            <h3>Boundary</h3>
            <p>{proof.nonClaim}</p>
          </div>
        </div>
      )}
    </section>
  );
}
