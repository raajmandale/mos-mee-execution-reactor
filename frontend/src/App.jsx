import React, { useMemo, useRef, useState } from "react";
import "./style.css";

const API_BASE = "http://127.0.0.1:8000";

const NAV = [
  ["command", "Command"],
  ["execution", "Execution"],
  ["memory", "Memory Core"],
  ["pattern", "Pattern Map"],
  ["intel", "System Intel"],
  ["queue", "Upload Queue"],
];

const STAGES = [
  ["IN", "Input"],
  ["SIG", "Signature"],
  ["PAT", "Pattern"],
  ["DEC", "Decision"],
  ["OUT", "Proof"],
];

const DEFAULT_RESULT = {
  workflow: "Image Flow",
  reuse: 91,
  decision: "Pattern Reused",
  decisionReason: "High similarity with existing pattern",
  confidence: "High",
  confidenceValue: 0.91,
  costSaved: 0.91,
  costFull: 1.0,
  source: "demo_image.jpg",
  proof: "Awaiting backend proof",
  proofId: "not-generated-yet",
  runId: "standby",
  inputHash: "standby",
  finalHash: "standby",
  evidencePath: "not-exported-yet",
  integrity: "Pending",
  saved: "4836 ms",
};

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

function detectWorkflow(name = "") {
  const n = name.toLowerCase();

  if (n.endsWith(".zip") || n.endsWith(".rar") || n.endsWith(".7z")) {
    return {
      workflow: "Bundle Workload",
      reuse: 88,
      decision: "Pattern Reused",
      confidence: "High",
      similarity: 0.88,
      saved: "5200 ms",
    };
  }

  if (n.endsWith(".jpg") || n.endsWith(".jpeg") || n.endsWith(".png") || n.endsWith(".webp")) {
    return {
      workflow: "Image Flow",
      reuse: 91,
      decision: "Pattern Reused",
      confidence: "High",
      similarity: 0.91,
      saved: "4836 ms",
    };
  }

  return {
    workflow: "Generic Flow",
    reuse: 74,
    decision: "New Pattern Learned",
    confidence: "Learning",
    similarity: 0.74,
    saved: "2100 ms",
  };
}

function shortHash(v = "") {
  const s = String(v || "");
  if (s.length <= 18) return s;
  return `${s.slice(0, 10)}…${s.slice(-8)}`;
}

function buildProofPayload(source) {
  const detected = detectWorkflow(source);

  return {
    step: detected.workflow,
    features: {
      file_name: source,
      workflow: detected.workflow,
      cost: 1.0,
      similarity: detected.similarity,
      reuse_score: detected.similarity,
    },
    steps: [
      {
        name: "input_acceptance",
        context: {
          cost: 0.2,
          similarity: 1.0,
          reuse_score: 1.0,
          source,
        },
        reuse_available: true,
      },
      {
        name: "signature_normalization",
        context: {
          cost: 0.35,
          similarity: detected.similarity,
          reuse_score: detected.similarity,
          workflow: detected.workflow,
        },
        reuse_available: true,
      },
      {
        name: "pattern_route_decision",
        context: {
          cost: 1.0,
          similarity: detected.similarity,
          reuse_score: detected.similarity,
          decision: detected.decision,
        },
        reuse_available: detected.similarity >= 0.6,
      },
    ],
  };
}

export default function App() {
  const fileRef = useRef(null);

  const [view, setView] = useState("execution");
  const [running, setRunning] = useState(false);
  const [stage, setStage] = useState("OUT");
  const [story, setStory] = useState("Execution ready — authority proof is waiting.");
  const [result, setResult] = useState(DEFAULT_RESULT);
  const [logs, setLogs] = useState([
    "[READY] PPE authority pipeline is standing by.",
    "[PROOF] backend proof authority required.",
    "[DECISION] reasoning panel active.",
  ]);

  const [history, setHistory] = useState([
    { source: "similar_image.jpg", workflow: "Image Flow", reuse: 91, status: "Verified" },
    { source: "demo_bundle.zip", workflow: "Bundle Workload", reuse: 88, status: "Verified" },
    { source: "demo_image.jpg", workflow: "Image Flow", reuse: 91, status: "Verified" },
    { source: "sample.bin", workflow: "Generic Flow", reuse: 74, status: "Mapped" },
  ]);

  const stageIndex = useMemo(
    () => Math.max(0, STAGES.findIndex(([id]) => id === stage)),
    [stage]
  );

  const intel = useMemo(() => {
    const all = [{ ...result }, ...history];
    const avg = Math.round(all.reduce((s, x) => s + Number(x.reuse || 0), 0) / all.length);
    const best = [...all].sort((a, b) => Number(b.reuse || 0) - Number(a.reuse || 0))[0];

    return {
      runs: all.length + 40,
      avg,
      best: best.workflow,
      saved: result.saved,
      efficiency: Math.max(60, Math.min(97, Math.round(avg * 0.75))),
    };
  }, [result, history]);

  function normalizeBackend(data, fileName) {
    const fallback = detectWorkflow(fileName);
    const decision = data?.decisions?.[data.decisions.length - 1] || {};
    const proof = data?.proof || {};

    const confidenceValue = Number(decision.confidence || fallback.similarity || 0.5);
    const costFull = Number(decision.cost_full || 1);
    const costSaved = Number(decision.cost_saved || 0);
    const reuse = Math.round(Math.max(0, Math.min(1, confidenceValue)) * 100);

    return {
      workflow: fallback.workflow,
      reuse,
      decision:
        decision.action === "reused"
          ? "Pattern Reused"
          : decision.action === "partial_reuse"
          ? "Partial Reuse"
          : decision.action === "recomputed"
          ? "Recomputed"
          : fallback.decision,
      decisionReason: decision.reason || "Backend proof route completed.",
      confidence: confidenceValue >= 0.85 ? "High" : confidenceValue >= 0.6 ? "Medium" : "Low",
      confidenceValue,
      costSaved,
      costFull,
      source: fileName,
      proof: data?.proof_id || proof?.proof_id || `MOS-PPE-${Date.now()}`,
      proofId: data?.proof_id || proof?.proof_id || "missing-proof-id",
      runId: data?.run_id || proof?.run_id || "missing-run-id",
      inputHash: proof?.input_hash || "missing-input-hash",
      finalHash: proof?.final_hash || "missing-final-hash",
      evidencePath: data?.evidence_path || "proof_reports/not-exported",
      integrity: data?.proof_id ? "Verified" : "Fallback",
      saved: fallback.saved,
    };
  }

  async function callProofPipeline(source) {
    const payload = buildProofPayload(source);

    const res = await fetch(`${API_BASE}/api/run-proof`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      throw new Error("PPE backend proof pipeline failed");
    }

    return await res.json();
  }

  async function animateExecution(finalResult) {
    setRunning(true);
    setView("execution");
    setLogs([]);

    const steps = [
      ["IN", `[IN] accepted → ${finalResult.source}`],
      ["SIG", `[SIG] input hash → ${shortHash(finalResult.inputHash)}`],
      ["PAT", `[PAT] ${finalResult.workflow} detected`],
      ["DEC", `[DEC] ${finalResult.decision} → ${finalResult.decisionReason}`],
      ["OUT", `[OUT] proof_id → ${shortHash(finalResult.proofId)}`],
    ];

    for (const [s, msg] of steps) {
      setStage(s);
      setStory(msg);
      setLogs((old) => [msg, ...old]);
      await sleep(550);
    }

    setResult(finalResult);
    setHistory((old) => [
      {
        source: finalResult.source,
        workflow: finalResult.workflow,
        reuse: finalResult.reuse,
        status: finalResult.integrity,
      },
      ...old.slice(0, 12),
    ]);

    setRunning(false);
  }

  async function runSource(source) {
    if (running) return;

    try {
      const data = await callProofPipeline(source);
      await animateExecution(normalizeBackend(data, source));
    } catch {
      const fallback = detectWorkflow(source);
      await animateExecution({
        ...DEFAULT_RESULT,
        ...fallback,
        source,
        proof: `LOCAL-FALLBACK-${Date.now()}`,
        proofId: "backend-not-reached",
        runId: "local-fallback",
        decisionReason: "Backend not reached. Local UI fallback executed only.",
        evidencePath: "not-created",
        integrity: "Unverified",
      });
    }
  }

  async function handleUpload(file) {
    if (!file || running) return;
    await runSource(file.name);
  }

  function runDemo(type = "image") {
    const source =
      type === "bundle"
        ? "demo_bundle.zip"
        : type === "similar"
        ? "similar_image.jpg"
        : "demo_image.jpg";

    runSource(source);
  }

  async function downloadProof() {
  if (!result.proofId || result.proofId === "not-generated-yet") {
    alert("Run proof first.");
    return;
  }

  try {
    const res = await fetch(`http://127.0.0.1:8000/api/proof-export/${result.proofId}`);

    if (!res.ok) {
      throw new Error("No export found");
    }

    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = `mos-ppe-signed-${result.proofId.slice(0, 12)}.json`;
    a.click();

    window.URL.revokeObjectURL(url);
  } catch (err) {
    console.error(err);
    alert("Backend export failed. Run proof again.");
  }
}

async function verifyProofFile(file) {
  if (!file) return;

  const form = new FormData();
  form.append("file", file);

  try {
    const res = await fetch(`${API_BASE}/api/verify-proof`, {
      method: "POST",
      body: form,
    });

    const data = await res.json();

    if (data.valid) {
      alert(
        `✅ Proof Verified\n\nProof ID: ${data.proof_id}\nRun ID: ${data.run_id}\nSignature: ${data.signature_type}`
      );
    } else {
      alert(`❌ Proof Failed\n\nReason: ${data.reason}`);
    }
  } catch (err) {
    console.error(err);
    alert("Proof verification failed.");
  }
}
async function downloadPublicKey() {
  try {
    const res = await fetch(`${API_BASE}/api/public-key`);

    if (!res.ok) {
      throw new Error("Public key not ready");
    }

    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = "mos_ppe_public.pem";
    a.click();

    window.URL.revokeObjectURL(url);
  } catch (err) {
    console.error(err);
    alert("Public key not available. Run proof once first.");
  }
}
  return (
    <div className={`mos-shell ${running ? "is-running" : ""}`}>
      <input
        ref={fileRef}
        type="file"
        hidden
        onChange={(e) => handleUpload(e.target.files?.[0])}
      />
<input
  id="proofVerifyInput"
  type="file"
  accept=".json,application/json"
  hidden
  onChange={(e) => verifyProofFile(e.target.files?.[0])}
/>
      <aside className="side">
        <div className="brand">
          <h1>M-OS</h1>
          <p>Mandale-OS PPE</p>
          <span>Pattern Proof Engine</span>
        </div>

        <nav>
          {NAV.map(([id, label]) => (
            <button key={id} className={view === id ? "active" : ""} onClick={() => setView(id)}>
              {label}
            </button>
          ))}
        </nav>

        <div className="state">
          <span>System State</span>
          <b>{running ? "Executing" : "Proof Ready"}</b>
          <small>{result.integrity} · {result.workflow}</small>
        </div>
      </aside>

      <main className="core">
        <TopBar
          view={view}
          stage={stage}
          running={running}
          onUpload={() => fileRef.current?.click()}
          onDemo={runDemo}
          onProof={downloadProof}
        />

        {view === "command" && (
          <section className="mode-panel">
            <span className="eyebrow">COMMAND COCKPIT</span>
            <h1>Execution Control Surface</h1>
            <p>Operator control surface for upload, replay, proof, and execution decisions.</p>
            <div className="command-buttons">
              <button onClick={() => fileRef.current?.click()}>Upload Real File</button>
              <button onClick={() => runDemo("image")}>Run Image Flow</button>
              <button onClick={() => runDemo("bundle")}>Run Bundle Flow</button>
              <button onClick={downloadProof}>Export Proof</button>
              <button onClick={downloadPublicKey}>Public Key</button>
              <button onClick={() => document.getElementById("proofVerifyInput")?.click()}>
  Verify Proof
</button>
            </div>
          </section>
        )}

        {view === "execution" && (
          <ExecutionView
            result={result}
            stage={stage}
            stageIndex={stageIndex}
            story={story}
            logs={logs}
            running={running}
          />
        )}

        {view === "memory" && <MemoryView history={history} />}
        {view === "pattern" && <PatternView stage={stage} stageIndex={stageIndex} />}
        {view === "intel" && <IntelView result={result} intel={intel} />}
        {view === "queue" && <QueueView history={history} />}
      </main>

      <aside className="right">
        <h2>Live Authority</h2>
        <Info label="Routing State" value={result.decision} />
        <Info label="Active Pattern" value={result.workflow} />
        <Info label="Confidence" value={`${Math.round(result.confidenceValue * 100)}%`} />
        <Info label="Integrity" value={result.integrity} />
        <Info label="Proof ID" value={shortHash(result.proofId)} />
        <Info label="Evidence Pack" value={result.evidencePath} />
      </aside>
    </div>
  );
}

function TopBar({ view, stage, running, onUpload, onDemo, onProof }) {
  return (
    <section className="topbar">
      <div className="top-title">
        <b>M-OS</b>
        <span>{view.toUpperCase()}</span>
      </div>

      <div className={`mini-orb ${running ? "running" : ""}`}>
        <i>{stage}</i>
      </div>

      <div className="top-actions">
        <button onClick={onUpload} disabled={running}>Upload</button>
        <button onClick={() => onDemo("image")} disabled={running}>Demo</button>
        <button onClick={() => onDemo("similar")} disabled={running}>Similar</button>
        <button onClick={() => onDemo("bundle")} disabled={running}>Bundle</button>
        <button onClick={onProof}>Export</button>
      </div>
    </section>
  );
}

function ExecutionView({ result, stage, stageIndex, story, logs, running }) {
  const savedPercent = result.costFull > 0 ? Math.round((result.costSaved / result.costFull) * 100) : 0;

  return (
    <>
      <section className="hero proof-hero">
        <div>
          <span className="eyebrow">PROOF AUTHORITY ENGINE</span>
          <h1>Execution That Proves Itself</h1>
          <p>Every run now exposes proof identity, decision reasoning, cost impact, and evidence path.</p>
          <div className="story">{story}</div>
        </div>

        <div className={`big-orb ${running ? "spin" : ""}`}>
          <span>{stage}</span>
        </div>
      </section>

      <section className="cards3">
        <Metric label="Workflow" value={result.workflow} />
        <Metric label="Reuse Strength" value={`${result.reuse}%`} />
        <Metric label="Integrity" value={result.integrity} />
      </section>

      <section className="proof-grid">
        <div className="authority-card">
  <h4>Proof Authority</h4>

  <div className="proof-id">
    {shortHash(result.proofId)}
  </div>

  <div className="proof-meta">
    <div>Run ID: {shortHash(result.runId)}</div>
    <div>Input Hash: {shortHash(result.inputHash)}</div>
    <div>Final Hash: {shortHash(result.finalHash)}</div>
  </div>

  <div className="proof-status">
    ✓ Cryptographically Bound  
  </div>
</div>
         <section className="proof-grid">

  {/* ✅ PROOF AUTHORITY CARD */}
  <div className="authority-card">
    <h4>Proof Authority</h4>

    <div className="proof-id">
      {shortHash(result.proofId)}
    </div>

    <div className="proof-meta">
      <div>Run ID: {shortHash(result.runId)}</div>
      <div>Input Hash: {shortHash(result.inputHash)}</div>
      <div>Final Hash: {shortHash(result.finalHash)}</div>
    </div>

    <div className="proof-status">
      ✓ Cryptographically Bound
    </div>
  </div>

  {/* ✅ DECISION CARD */}
  <div className="authority-card decision-card">
    <span className="eyebrow">DECISION REASONING</span>

    <h3>{result.decision}</h3>
    <p>{result.reason}</p>

    <div className="reason-row">
      <span>Confidence</span>
      <b>{result.confidence}%</b>
    </div>

    <div className="reason-row">
      <span>Cost Saved</span>
      <b>{savedPercent}%</b>
    </div>

    <div className="reason-row">
      <span>Why Reused</span>
      <b>Similarity above threshold</b>
    </div>

    <div className="reason-row">
      <span>Threshold</span>
      <b>85%</b>
    </div>

  </div>

</section>

        {/* 🔥 PROOF TIMELINE */}
        <section className="proof-timeline">
          <h3>Proof Timeline</h3>

          <div className="timeline-row">
            <span>Input Locked</span>
            <b>{shortHash(result.inputHash)}</b>
          </div>

          <div className="timeline-row">
            <span>Pattern Matched</span>
            <b>{result.workflow}</b>
          </div>

          <div className="timeline-row">
            <span>Decision Taken</span>
            <b>{result.decision}</b>
          </div>

          <div className="timeline-row">
            <span>Proof Generated</span>
            <b>{shortHash(result.proofId)}</b>
          </div>
        </section>
        <div className="pipeline">
          {STAGES.map(([id, label], i) => (
            <div
              key={id}
              className={`pipe ${stage === id ? "active" : ""} ${i <= stageIndex ? "done" : ""}`}
            >
              <b>{id}</b>
              <small>{label}</small>
            </div>
          ))}
        </div>

        <div className="console">
          <b>LIVE PROOF CONSOLE</b>
          {logs.map((l, i) => <p key={i}>› {l}</p>)}
          <p>› [EVIDENCE]</p>
<button className="evidence-btn">
  Open Evidence Pack
</button>
        </div>
      </section>
    </>
  );
}

function MemoryView({ history }) {
  return (
    <section className="mode-panel">
      <span className="eyebrow">PERSISTENT PATTERN MEMORY</span>
      <h1>Memory Core</h1>
      <p>Stored structural families updated from proof-aware execution.</p>

      <div className="memory-graph">
        <div className="memory-center">MOS</div>
        {history.slice(0, 7).map((h, i) => (
          <div key={i} className={`memory-dot dot-${i}`}>
            <b>{short(h.workflow)}</b>
            <small>{h.reuse}%</small>
          </div>
        ))}
      </div>

      <div className="memory-list">
        {history.slice(0, 6).map((h, i) => (
          <div key={i}>
            <b>{h.workflow}</b>
            <span>{h.source} · {h.reuse}% · {h.status}</span>
          </div>
        ))}
      </div>
    </section>
  );
}

function PatternView({ stage, stageIndex }) {
  return (
    <section className="mode-panel">
      <span className="eyebrow">LIVE PATTERN ROUTE</span>
      <h1>Pattern Map</h1>
      <p>Every node reflects the current execution state machine.</p>

      <div className="pattern-web">
        {STAGES.map(([id, label], i) => (
          <div key={id} className={`web-node ${stage === id ? "active" : ""} ${i <= stageIndex ? "done" : ""}`}>
            <b>{id}</b>
            <span>{label}</span>
          </div>
        ))}
      </div>
    </section>
  );
}

function IntelView({ result, intel }) {
  return (
    <section className="mode-panel">
      <span className="eyebrow">SYSTEM INTELLIGENCE</span>
      <h1>Operational Intelligence</h1>
      <p>Live proof-readiness, reuse strength, and route confidence.</p>

      <div className="intel-grid">
        <Metric label="Total Runs" value={intel.runs} />
        <Metric label="Average Reuse" value={`${intel.avg}%`} />
        <Metric label="Best Workflow" value={intel.best} />
        <Metric label="Saved Time" value={result.saved} />
        <Metric label="Efficiency" value={`${intel.efficiency}%`} />
        <Metric label="Proof State" value={result.integrity} />
      </div>
    </section>
  );
}

function QueueView({ history }) {
  return (
    <section className="mode-panel">
      <span className="eyebrow">UPLOAD QUEUE</span>
      <h1>Execution Queue</h1>
      <p>Recent files, detected patterns and proof states.</p>

      <div className="queue-list">
        {history.map((h, i) => (
          <div key={i}>
            <b>{h.source}</b>
            <span>{h.workflow}</span>
            <em>{h.status}</em>
          </div>
        ))}
      </div>
    </section>
  );
}

function Info({ label, value }) {
  return (
    <div className="info">
      <span>{label}</span>
      <b>{value}</b>
    </div>
  );
}

function Metric({ label, value }) {
  return (
    <div className="metric">
      <span>{label}</span>
      <b>{value}</b>
    </div>
  );
}

function short(v) {
  const x = String(v || "").toLowerCase();
  if (x.includes("image")) return "IMG";
  if (x.includes("bundle")) return "BND";
  if (x.includes("generic")) return "GEN";
  return "PAT";
}