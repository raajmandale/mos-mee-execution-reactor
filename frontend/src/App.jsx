import { useEffect, useMemo, useRef, useState } from "react";

const API_BASE = "http://127.0.0.1:8000";

const RAIL_ITEMS = [
  ["command", "Command"],
  ["execution", "Execution"],
  ["memory", "Memory Core"],
  ["pattern", "Pattern Map"],
  ["intel", "System Intel"],
  ["queue", "Upload Queue"],
];

const EMPTY_RUNTIME = {
  workflow: "Unknown",
  family: "Unknown",
  reuse: 0,
  confidence: "Low",
  time: 0,
  decision: "Learning",
  mode: "learning",
  systemState: "Learning",
  routeType: "linear",
  nodes: [],
  topNodes: [],
  bottomNodes: [],
  notes: ["No prior route selected.", "Reactor waiting for execution."],
  console: ["[reactor] standby", "[memory] no active recall route"],
  sourceFile: "No file uploaded",
  signature: null,
};

const EMPTY_SYSTEM = {
  totalRuns: 0,
  averageReuse: 0,
  bestWorkflow: "Unknown",
  savedMs: 0,
  efficiencyScore: 0,
  memory: {},
  history: [],
  queue: [],
  lastResult: null,
  prediction: {
    prediction: "Learning",
    confidence: "Low",
    reason: "No execution history yet.",
    memoryClusters: [],
  },
};

const DEMO_PRESETS = {
  image: () =>
    new File(["demo image bytes"], "demo_image.png", {
      type: "image/png",
    }),
  similar: () =>
    new File(["demo similar bytes"], "similar_image.jpg", {
      type: "image/jpeg",
    }),
  bundle: () =>
    new File(["demo bundle bytes"], "demo_bundle.zip", {
      type: "application/zip",
    }),
};

function OrbCanvas({ mode = "learning", mini = false }) {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    let raf = 0;
    let tick = 0;

    const palette = {
      learning: ["#7aa6ff", "#315bff"],
      reused: ["#31efb0", "#0d9d76"],
      partial: ["#ffb769", "#ff8a2c"],
      hybrid: ["#c88cff", "#4ce4c1"],
      idle: ["#7aa6ff", "#315bff"],
    };

    const active = palette[mode] ? mode : "learning";

    const draw = () => {
      const width = canvas.clientWidth || (mini ? 72 : 300);
      const height = canvas.clientHeight || (mini ? 72 : 300);

      canvas.width = width * window.devicePixelRatio;
      canvas.height = height * window.devicePixelRatio;
      ctx.setTransform(window.devicePixelRatio, 0, 0, window.devicePixelRatio, 0, 0);
      ctx.clearRect(0, 0, width, height);

      const [c1, c2] = palette[active];
      const cx = width / 2;
      const cy = height / 2;
      const radius = (mini ? 18 : 68) + Math.sin(tick * 0.035) * (mini ? 1.5 : 4.2);

      const glow = ctx.createRadialGradient(cx, cy, 4, cx, cy, mini ? 44 : 135);
      glow.addColorStop(0, "rgba(255,255,255,0.95)");
      glow.addColorStop(0.16, `${c1}ff`);
      glow.addColorStop(0.42, `${c1}77`);
      glow.addColorStop(0.8, `${c2}22`);
      glow.addColorStop(1, "rgba(0,0,0,0)");
      ctx.fillStyle = glow;
      ctx.beginPath();
      ctx.arc(cx, cy, mini ? 42 : 140, 0, Math.PI * 2);
      ctx.fill();

      const core = ctx.createRadialGradient(cx - radius * 0.15, cy - radius * 0.18, 2, cx, cy, radius);
      core.addColorStop(0, "rgba(255,255,255,0.98)");
      core.addColorStop(0.2, c1);
      core.addColorStop(0.62, c2);
      core.addColorStop(1, "rgba(0,0,0,0)");
      ctx.fillStyle = core;
      ctx.beginPath();
      ctx.arc(cx, cy, radius, 0, Math.PI * 2);
      ctx.fill();

      const ringCount = mini ? 2 : 3;
      for (let i = 0; i < ringCount; i += 1) {
        const ringRadius = radius + (mini ? 7 : 20) + i * (mini ? 8 : 18);
        ctx.beginPath();
        ctx.lineWidth = mini ? 1 : 1.4;
        ctx.strokeStyle = `rgba(255,255,255,${0.16 - i * 0.03})`;
        ctx.arc(
          cx,
          cy,
          ringRadius,
          tick * 0.012 + i * 0.5,
          tick * 0.012 + i * 0.5 + Math.PI * 1.72
        );
        ctx.stroke();
      }

      const dots = mini ? 10 : 18;
      for (let i = 0; i < dots; i += 1) {
        const a = tick * 0.02 + (i / dots) * Math.PI * 2;
        const rr = radius + (mini ? 10 : 17) + Math.sin(tick * 0.04 + i) * (mini ? 2 : 6);
        const px = cx + Math.cos(a) * rr;
        const py = cy + Math.sin(a) * rr;
        ctx.beginPath();
        ctx.fillStyle = i % 2 === 0 ? "rgba(255,255,255,0.88)" : `${c1}dd`;
        ctx.arc(px, py, mini ? 1.6 : 2.3, 0, Math.PI * 2);
        ctx.fill();
      }

      tick += 1;
      raf = requestAnimationFrame(draw);
    };

    draw();
    return () => cancelAnimationFrame(raf);
  }, [mini, mode]);

  return <canvas ref={canvasRef} className={mini ? "mini-orb-canvas" : "orb-canvas"} />;
}

function LinearRoute({ nodes = [], mode = "learning" }) {
  if (!nodes.length) return null;

  return (
    <div className="route-linear">
      {nodes.map((node, idx) => (
        <div className="route-cell" key={`${node.short}-${idx}`}>
          <div className={`route-node ${mode} ${node.state || "cold"}`}>
            <span>{node.short}</span>
          </div>
          <div className="route-label">{node.label}</div>
          {idx < nodes.length - 1 && (
            <div className={`route-line ${mode}`}>
              <div className="route-pulse" />
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

function HybridRoute({ topNodes = [], bottomNodes = [] }) {
  return (
    <div className="route-hybrid">
      <div className="hy-row">
        {topNodes.map((node, idx) => (
          <div className="route-cell" key={`top-${node.short}-${idx}`}>
            <div className={`route-node hybrid ${node.state || "cold"}`}>
              <span>{node.short}</span>
            </div>
            <div className="route-label">{node.label}</div>
            {idx < topNodes.length - 1 && (
              <div className="route-line hybrid">
                <div className="route-pulse" />
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="hy-branches">
        <div className="branch-left" />
        <div className="branch-right" />
      </div>

      <div className="hy-row">
        {bottomNodes.map((node, idx) => (
          <div className="route-cell" key={`bottom-${node.short}-${idx}`}>
            <div className={`route-node hybrid ${node.state || "cold"}`}>
              <span>{node.short}</span>
            </div>
            <div className="route-label">{node.label}</div>
            {idx < bottomNodes.length - 1 && (
              <div className="route-line hybrid">
                <div className="route-pulse" />
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

function ConsolePanel({ lines = [] }) {
  return (
    <div className="console-shell">
      <div className="console-top">
        <div className="console-dots">
          <span />
          <span />
          <span />
        </div>
        <div className="console-title">LIVE EXECUTION CONSOLE</div>
      </div>
      <div className="console-body">
        {lines.map((line, idx) => (
          <div className="console-line" key={`${line}-${idx}`}>
            <span className="console-prefix">›</span>
            <span>{line}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function FocusHeader({
  activeTab,
  runtimeState,
  isRunning,
  onUpload,
  onDemo,
  onSimilar,
  onBundle,
}) {
  const titleMap = {
    execution: "Execution Engine",
    memory: "Memory Core",
    pattern: "Pattern Map",
    intel: "System Intelligence",
    queue: "Upload Queue",
  };

  return (
    <div className="focus-header">
      <div className="focus-left">
        <div className="focus-mini-logo">M-OS</div>
        <div className="focus-title">{titleMap[activeTab] || "Focus View"}</div>
      </div>

      <div className="focus-center">
        <OrbCanvas mode={runtimeState.mode} mini />
      </div>

      <div className="focus-actions">
        <button className="focus-btn primary" onClick={onUpload} disabled={isRunning}>
          Upload
        </button>
        <button className="focus-btn" onClick={onDemo} disabled={isRunning}>
          Demo
        </button>
        <button className="focus-btn" onClick={onSimilar} disabled={isRunning}>
          Similar
        </button>
        <button className="focus-btn" onClick={onBundle} disabled={isRunning}>
          Bundle
        </button>
      </div>
    </div>
  );
}

export default function App() {
  const [activeTab, setActiveTab] = useState("command");
  const [isRunning, setIsRunning] = useState(false);
  const [runtimeState, setRuntimeState] = useState(EMPTY_RUNTIME);
  const [systemState, setSystemState] = useState(EMPTY_SYSTEM);

  const fileRef = useRef(null);
  const centerRef = useRef(null);

  const isFocusMode = activeTab !== "command";

  function scrollCenterToTop() {
    if (centerRef.current) {
      centerRef.current.scrollTo({ top: 0, behavior: "smooth" });
    }
  }

  function mapBackendResultToRuntime(result) {
    if (!result) return EMPTY_RUNTIME;

    return {
      workflow: result.workflow ?? "Unknown",
      family: result.family ?? "Unknown",
      reuse: result.reuse ?? 0,
      confidence: result.confidence ?? "Low",
      time: result.time ?? 0,
      decision: result.decision ?? "Learning",
      mode: result.mode ?? "learning",
      systemState: result.systemState ?? "Learning",
      routeType: result.routeType ?? "linear",
      nodes: result.nodes ?? [],
      topNodes: result.topNodes ?? [],
      bottomNodes: result.bottomNodes ?? [],
      notes: result.notes ?? ["No execution notes."],
      console: result.console ?? ["[reactor] no console output"],
      sourceFile: result.sourceFile ?? "No file uploaded",
      signature: result.signature ?? null,
    };
  }

  async function hydrateState() {
    try {
      const res = await fetch(`${API_BASE}/state`);
      const json = await res.json();

      setSystemState({
        totalRuns: json.totalRuns ?? 0,
        averageReuse: json.averageReuse ?? 0,
        bestWorkflow: json.bestWorkflow ?? "Unknown",
        savedMs: json.savedMs ?? 0,
        efficiencyScore: json.efficiencyScore ?? 0,
        memory: json.memory ?? {},
        history: json.history ?? [],
        queue: json.queue ?? [],
        lastResult: json.lastResult ?? null,
        prediction: json.prediction ?? EMPTY_SYSTEM.prediction,
      });

      if (json.lastResult) {
        setRuntimeState(mapBackendResultToRuntime(json.lastResult));
      } else {
        setRuntimeState(EMPTY_RUNTIME);
      }
    } catch (err) {
      console.error("state load failed", err);
    }
  }

  useEffect(() => {
    hydrateState();
  }, []);

  async function handleUpload(file, targetTab = "execution") {
    if (!file) return;

    const form = new FormData();
    form.append("file", file);

    try {
      setIsRunning(true);

      const res = await fetch(`${API_BASE}/upload-react`, {
        method: "POST",
        body: form,
      });

      if (!res.ok) {
        throw new Error(`Upload failed with status ${res.status}`);
      }

      const json = await res.json();
      setRuntimeState(mapBackendResultToRuntime(json));
      await hydrateState();
      setActiveTab(targetTab);
      scrollCenterToTop();
    } catch (err) {
      console.error("execution failed", err);
    } finally {
      setIsRunning(false);
    }
  }

  async function runPreset(kind) {
    const presetFactory = DEMO_PRESETS[kind];
    if (!presetFactory) return;
    const presetFile = presetFactory();
    await handleUpload(presetFile, activeTab === "command" ? "execution" : activeTab);
  }

  const memoryCards = useMemo(() => {
    return Object.entries(systemState.memory || {}).map(([key, value]) => ({
      key,
      title: value.label || key,
      meta: `Seen: ${value.seen} • Best Reuse: ${value.best_reuse}% • ${value.last_confidence || "Low"}`,
    }));
  }, [systemState.memory]);

  const historyCards = useMemo(() => systemState.history || [], [systemState.history]);
  const queueCards = useMemo(() => systemState.queue || [], [systemState.queue]);
  const prediction = systemState.prediction || EMPTY_SYSTEM.prediction;
  const memoryClusters = prediction.memoryClusters || [];

  return (
    <div className={`os-root mode-${runtimeState.mode}`}>
      <div className="bg-grid" />
      <div className="bg-glow bg-glow-a" />
      <div className="bg-glow bg-glow-b" />

      <aside className="os-left">
        <div className="logo-box">
          <div className="logo-main">M-OS</div>
          <div className="logo-sub">MANDALE-OS (MOS-MEE)</div>
        </div>

        {RAIL_ITEMS.map(([key, label]) => (
          <button
            key={key}
            className={`nav-item ${activeTab === key ? "active" : ""}`}
            onClick={() => {
              setActiveTab(key);
              scrollCenterToTop();
            }}
          >
            {label}
          </button>
        ))}

        <div className="state-box">
          <div className="state-kicker">SYSTEM STATE</div>
          <div className="state-value">{runtimeState.systemState}</div>
        </div>
      </aside>

      <main ref={centerRef} className="os-center">
        {!isFocusMode ? (
          <>
            <section className="hero-panel">
              <div className="hero-copy">
                <div className="hero-kicker">UPLOAD-AWARE REACTOR</div>
                <h1 className="hero-title">Mandale-OS Execution Reactor</h1>
                <p className="hero-sub">
                  Real upload-aware reactor with backend-driven route intelligence, neural reuse,
                  and file-family execution routing.
                </p>

                <div className="actions">
                  <button
                    className="action primary"
                    onClick={() => fileRef.current?.click()}
                    disabled={isRunning}
                  >
                    {isRunning ? "Processing..." : "Upload Real File / ZIP"}
                  </button>

                  <button className="action" onClick={() => runPreset("image")} disabled={isRunning}>
                    Run Demo
                  </button>

                  <button className="action" onClick={() => runPreset("similar")} disabled={isRunning}>
                    Run Similar Task
                  </button>

                  <button className="action" onClick={() => runPreset("bundle")} disabled={isRunning}>
                    Run Bundle Task
                  </button>
                </div>

                <input
                  ref={fileRef}
                  type="file"
                  hidden
                  onChange={(e) => {
                    const file = e.target.files?.[0];
                    if (file) handleUpload(file);
                    e.target.value = "";
                  }}
                />
              </div>

              <div className="hero-orb-panel">
                <OrbCanvas mode={runtimeState.mode} />
              </div>
            </section>

            <section className="top-result">
              <div className="metric-card">
                <div className="metric-label">Workflow</div>
                <div className="metric-value">{runtimeState.workflow}</div>
              </div>
              <div className="metric-card">
                <div className="metric-label">Reuse</div>
                <div className="metric-value">{runtimeState.reuse}%</div>
              </div>
              <div className="metric-card">
                <div className="metric-label">Source</div>
                <div className="metric-value">{runtimeState.sourceFile}</div>
              </div>
            </section>

            <section className="section-panel">
              <div className="section-head">
                <div>
                  <div className="section-title">Command Surface</div>
                  <div className="section-sub">
                    Live backend result stays in the top viewport for direct operator control.
                  </div>
                </div>
                <div className={`pill ${runtimeState.mode}`}>{runtimeState.decision}</div>
              </div>

              <div className="command-grid">
                <div className="info-card">
                  <div className="metric-label">Pattern Family</div>
                  <div className="metric-value">{runtimeState.family}</div>
                </div>
                <div className="info-card">
                  <div className="metric-label">Confidence</div>
                  <div className="metric-value">{runtimeState.confidence}</div>
                </div>
                <div className="info-card">
                  <div className="metric-label">Execution Time</div>
                  <div className="metric-value">{runtimeState.time} ms</div>
                </div>
              </div>

              <div className="console-wrap">
                <ConsolePanel lines={runtimeState.console} />
              </div>

              <div className="prediction-card">
                <div className="prediction-head">
                  <div className="section-title small">Prediction Layer</div>
                  <div className={`mini-pill ${prediction.confidence?.toLowerCase()}`}>{prediction.confidence}</div>
                </div>
                <div className="prediction-main">{prediction.prediction}</div>
                <div className="prediction-reason">{prediction.reason}</div>
              </div>
            </section>
          </>
        ) : (
          <>
            <FocusHeader
              activeTab={activeTab}
              runtimeState={runtimeState}
              isRunning={isRunning}
              onUpload={() => fileRef.current?.click()}
              onDemo={() => runPreset("image")}
              onSimilar={() => runPreset("similar")}
              onBundle={() => runPreset("bundle")}
            />

            <input
              ref={fileRef}
              type="file"
              hidden
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (file) handleUpload(file, activeTab);
                e.target.value = "";
              }}
            />

            <div className="focus-content">
              <section className="top-result compact">
                <div className="metric-card">
                  <div className="metric-label">Workflow</div>
                  <div className="metric-value">{runtimeState.workflow}</div>
                </div>
                <div className="metric-card">
                  <div className="metric-label">Reuse</div>
                  <div className="metric-value">{runtimeState.reuse}%</div>
                </div>
                <div className="metric-card">
                  <div className="metric-label">Source</div>
                  <div className="metric-value">{runtimeState.sourceFile}</div>
                </div>
              </section>

              {activeTab === "execution" && (
                <section className="section-panel">
                  <div className="section-head">
                    <div>
                      <div className="section-title">Backend-Driven Route Engine</div>
                      <div className="section-sub">
                        Route changes depend on uploaded file type and backend classification.
                      </div>
                    </div>
                    <div className={`pill ${runtimeState.mode}`}>{runtimeState.decision}</div>
                  </div>

                  {runtimeState.routeType === "hybrid" ? (
                    <HybridRoute
                      topNodes={runtimeState.topNodes}
                      bottomNodes={runtimeState.bottomNodes}
                    />
                  ) : (
                    <LinearRoute nodes={runtimeState.nodes} mode={runtimeState.mode} />
                  )}

                  <div className="console-wrap">
                    <ConsolePanel lines={runtimeState.console} />
                  </div>

                  <div className="prediction-card">
                    <div className="prediction-head">
                      <div className="section-title small">Prediction Layer</div>
                      <div className={`mini-pill ${prediction.confidence?.toLowerCase()}`}>{prediction.confidence}</div>
                    </div>
                    <div className="prediction-main">{prediction.prediction}</div>
                    <div className="prediction-reason">{prediction.reason}</div>
                  </div>
                </section>
              )}

              {activeTab === "memory" && (
                <section className="section-panel">
                  <div className="section-head">
                    <div>
                      <div className="section-title">Persistent Memory Core</div>
                      <div className="section-sub">
                        Stored structural families updated from real upload execution.
                      </div>
                    </div>
                    <div className="pill neutral">Memory Active</div>
                  </div>

                  <div className="stack-list">
                    {memoryCards.length === 0 ? (
                      <div className="stack-card">
                        <div>
                          <div className="stack-title">No memory written yet</div>
                          <div className="stack-meta">Run uploads or demos to build memory.</div>
                        </div>
                        <div className="mini-pill">Idle</div>
                      </div>
                    ) : (
                      memoryCards.map((item) => (
                        <div className="stack-card" key={item.key}>
                          <div>
                            <div className="stack-title">{item.title}</div>
                            <div className="stack-meta">{item.meta}</div>
                          </div>
                          <div className="mini-pill">Live</div>
                        </div>
                      ))
                    )}
                  </div>

                  {!!memoryClusters.length && (
                    <div className="cluster-grid">
                      {memoryClusters.map((cluster) => (
                        <div className="cluster-card" key={cluster.cluster}>
                          <div className="cluster-family">{cluster.label}</div>
                          <div className="cluster-meta">
                            {cluster.items} signatures • Seen {cluster.seen}
                          </div>
                          <div className="cluster-reuse">Best {cluster.best_reuse}%</div>
                        </div>
                      ))}
                    </div>
                  )}
                </section>
              )}

              {activeTab === "pattern" && (
                <section className="section-panel">
                  <div className="section-head">
                    <div>
                      <div className="section-title">Orbit Memory Map</div>
                      <div className="section-sub">
                        Family-level relationship surface for upload-aware execution intelligence.
                      </div>
                    </div>
                    <div className="pill neutral">Pattern Active</div>
                  </div>

                  <div className="pattern-map">
                    <div
                      className={`map-orbit map-center ${
                        runtimeState.workflow === "Bundle Workload" || runtimeState.workflow === "Hybrid Pipeline"
                          ? "active"
                          : ""
                      }`}
                    >
                      MOS
                    </div>
                    <div className={`map-orbit map-a ${runtimeState.workflow === "Image Flow" ? "active" : ""}`}>
                      IMG
                    </div>
                    <div className={`map-orbit map-b ${runtimeState.workflow === "Document Flow" ? "active" : ""}`}>
                      DOC
                    </div>
                    <div className={`map-orbit map-c ${runtimeState.workflow === "Code Flow" ? "active" : ""}`}>
                      CODE
                    </div>
                    <div
                      className={`map-orbit map-d ${
                        runtimeState.workflow === "Bundle Workload" || runtimeState.workflow === "Hybrid Pipeline"
                          ? "active"
                          : ""
                      }`}
                    >
                      BND
                    </div>
                  </div>
                </section>
              )}

              {activeTab === "intel" && (
                <section className="section-panel">
                  <div className="section-head">
                    <div>
                      <div className="section-title">System Intelligence</div>
                      <div className="section-sub">
                        High-level operational metrics from the upload-aware reactor.
                      </div>
                    </div>
                    <div className="pill neutral">Intel Live</div>
                  </div>

                  <div className="intel-grid">
                    <div className="metric-card">
                      <div className="metric-label">Total Runs</div>
                      <div className="metric-value">{systemState.totalRuns}</div>
                    </div>
                    <div className="metric-card">
                      <div className="metric-label">Average Reuse</div>
                      <div className="metric-value">{systemState.averageReuse}%</div>
                    </div>
                    <div className="metric-card">
                      <div className="metric-label">Best Workflow</div>
                      <div className="metric-value">{systemState.bestWorkflow}</div>
                    </div>
                    <div className="metric-card">
                      <div className="metric-label">Saved Time</div>
                      <div className="metric-value">{systemState.savedMs} ms</div>
                    </div>
                    <div className="metric-card">
                      <div className="metric-label">Efficiency Score</div>
                      <div className="metric-value">{systemState.efficiencyScore}%</div>
                    </div>
                  </div>

                  <div className="stack-list history-top">
                    {historyCards.slice(0, 8).map((item, idx) => (
                      <div className="stack-card" key={`${item.timestamp}-${idx}`}>
                        <div>
                          <div className="stack-title">{item.workflow}</div>
                          <div className="stack-meta">
                            {item.timestamp} • Reuse: {item.reuse}% • Mode: {item.mode}
                          </div>
                        </div>
                        <div className={`mini-pill ${item.mode}`}>{item.decision}</div>
                      </div>
                    ))}
                  </div>
                </section>
              )}

              {activeTab === "queue" && (
                <section className="section-panel">
                  <div className="section-head">
                    <div>
                      <div className="section-title">Upload Queue</div>
                      <div className="section-sub">
                        Recent upload jobs processed by the reactor.
                      </div>
                    </div>
                    <div className="pill neutral">Queue Active</div>
                  </div>

                  <div className="stack-list">
                    {queueCards.length === 0 ? (
                      <div className="stack-card">
                        <div>
                          <div className="stack-title">No queued files</div>
                          <div className="stack-meta">Upload a file to start processing.</div>
                        </div>
                      </div>
                    ) : (
                      queueCards.map((item) => (
                        <div className="stack-card" key={item.id}>
                          <div>
                            <div className="stack-title">{item.file}</div>
                            <div className="stack-meta">
                              {item.status} • {item.timestamp}
                            </div>
                          </div>
                          <div className="mini-pill processed">{item.status}</div>
                        </div>
                      ))
                    )}
                  </div>
                </section>
              )}
            </div>
          </>
        )}

        <div className="bottom-spacer" />
      </main>

      <aside className="os-right">
        <div className="right-panel">
          <div className="right-title">Live Intelligence</div>

          <div className="right-card">
            <div className="metric-label">Routing State</div>
            <div className="metric-value">{runtimeState.decision}</div>
          </div>

          <div className="right-card">
            <div className="metric-label">Active Pattern</div>
            <div className="metric-value">{runtimeState.workflow}</div>
          </div>

          <div className="right-card">
            <div className="metric-label">Confidence</div>
            <div className="metric-value">{runtimeState.confidence}</div>
          </div>

          <div className="right-card">
            <div className="metric-label">Live Insights</div>
            <div className="intel-mini">Total Runs: {systemState.totalRuns}</div>
            <div className="intel-mini">Average Reuse: {systemState.averageReuse}%</div>
            <div className="intel-mini">Best Workflow: {systemState.bestWorkflow}</div>
            <div className="intel-mini">Saved Time: {systemState.savedMs} ms</div>
            <div className="intel-mini">Efficiency Score: {systemState.efficiencyScore}%</div>
          </div>

          <div className="right-card">
            <div className="metric-label">Prediction</div>
            <div className="intel-mini">Next: {prediction.prediction}</div>
            <div className="intel-mini">Confidence: {prediction.confidence}</div>
            <div className="intel-mini">{prediction.reason}</div>
          </div>

          <div className="right-card">
            <div className="metric-label">Engine Notes</div>
            <ul className="notes">
              {runtimeState.notes.map((note, idx) => (
                <li key={idx}>{note}</li>
              ))}
            </ul>
          </div>
        </div>
      </aside>
    </div>
  );
}