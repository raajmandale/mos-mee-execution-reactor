import { useMemo, useState } from "react";

const BENCHMARKS = {
  A: {
    title: "Pattern Reuse Routing",
    purpose: "Tests whether similar graph-routing workloads can reuse prior execution paths.",
  },
  B: {
    title: "Structured Transform Workflow",
    purpose: "Tests whether lower-cost execution paths can be selected for repeated transform work.",
  },
  C: {
    title: "Fragment Reconstruction Workflow",
    purpose: "Tests DFG/XPADI-style reconstruction path reuse and continuity.",
  },
};

export default function ProofMode({ apiBase = "http://127.0.0.1:8000" }) {
  const [benchmark, setBenchmark] = useState("A");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const proof = result?.proof;
  const execution = proof?.execution || {};
  const pattern = proof?.pattern || {};

  const evidenceText = useMemo(() => {
    if (!proof) return "";
    return [
      "M-OS Pattern Proof Dossier",
      `Run ID: ${proof.run_id}`,
      `Benchmark: ${proof.benchmark?.title}`,
      `Pattern Signature: ${pattern.signature}`,
      `Similarity Score: ${pattern.similarity_score}`,
      `Route Chosen: ${execution.route_chosen}`,
      `Baseline: ${execution.baseline_ms} ms`,
      `M-OS: ${execution.mos_ms} ms`,
      `Execution Savings: ${execution.savings_pct}%`,
      `Reuse: ${execution.reuse_pct}%`,
      `Proof Hash: ${proof.proof_hash}`,
      "",
      proof.non_claim,
    ].join("\n");
  }, [proof, execution, pattern]);

  async function runProof() {
    setLoading(true);
    try {
      const res = await fetch(`${apiBase}/proof/run-proof`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ benchmark, export_html: true }),
      });
      const json = await res.json();
      setResult(json);
    } catch (err) {
      setResult({
        status: "error",
        proof: null,
        error: String(err),
      });
    } finally {
      setLoading(false);
    }
  }

  function copySummary() {
    if (!evidenceText) return;
    navigator.clipboard?.writeText(evidenceText);
  }

  return (
    <section className="section-panel proof-panel">
      <div className="section-head">
        <div>
          <div className="hero-kicker">PPE v2 • PATTERN PROOF ENGINE</div>
          <div className="section-title">Pattern Proof Dossier</div>
          <div className="section-sub">
            Evidence layer for M-OS MEE: pattern signature, route decision, reuse metrics,
            and proof hash in one operator-readable artifact.
          </div>
        </div>
        <div className="pill reused">Evidence Layer</div>
      </div>

      <div className="proof-selector">
        {Object.entries(BENCHMARKS).map(([key, item]) => (
          <button
            key={key}
            className={`proof-bench ${benchmark === key ? "active" : ""}`}
            onClick={() => setBenchmark(key)}
          >
            <span>Benchmark {key}</span>
            <strong>{item.title}</strong>
            <small>{item.purpose}</small>
          </button>
        ))}
      </div>

      <div className="actions proof-actions">
        <button className="action primary" onClick={runProof} disabled={loading}>
          {loading ? "Generating Proof..." : "Run Pattern Proof"}
        </button>
        <button className="action" onClick={copySummary} disabled={!proof}>
          Copy Proof Summary
        </button>
      </div>

      {!proof && (
        <div className="proof-empty">
          Select a benchmark and run the proof engine. This does not replace the existing
          MEE reactor; it activates evidence on top of it.
        </div>
      )}

      {proof && (
        <>
          <div className="proof-grid">
            <div className="metric-card proof-metric">
              <div className="metric-label">Pattern Similarity</div>
              <div className="metric-value">{pattern.similarity_score}</div>
            </div>
            <div className="metric-card proof-metric">
              <div className="metric-label">Route Chosen</div>
              <div className="metric-value">{execution.route_chosen}</div>
            </div>
            <div className="metric-card proof-metric">
              <div className="metric-label">Reuse</div>
              <div className="metric-value">{execution.reuse_pct}%</div>
            </div>
            <div className="metric-card proof-metric">
              <div className="metric-label">Savings</div>
              <div className="metric-value">{execution.savings_pct}%</div>
            </div>
          </div>

          <div className="proof-dossier">
            <div className="proof-dossier-head">
              <div>
                <div className="section-title small">M-OS Pattern Proof Dossier</div>
                <div className="section-sub">Run ID: {proof.run_id}</div>
              </div>
              <div className="mini-pill processed">Experimental Proof Complete</div>
            </div>

            <div className="proof-table">
              <div><span>Benchmark</span><b>{proof.benchmark?.title}</b></div>
              <div><span>Pattern Signature</span><b>{pattern.signature}</b></div>
              <div><span>Invariant Signature</span><b>{pattern.invariant_signature}</b></div>
              <div><span>Baseline</span><b>{execution.baseline_ms} ms</b></div>
              <div><span>M-OS</span><b>{execution.mos_ms} ms</b></div>
              <div><span>Proof Hash</span><b>{proof.proof_hash}</b></div>
            </div>

            <div className="proof-summary">{proof.summary}</div>
            <div className="proof-nonclaim">{proof.non_claim}</div>

            {result?.export?.filename && (
              <div className="proof-export">
                HTML evidence generated in:
                <code> docs/proof_reports/{result.export.filename}</code>
              </div>
            )}
          </div>
        </>
      )}
    </section>
  );
}
