export default function Insights({ insights }) {
  if (!insights) return null;

  const efficiencyScore = Math.min(
    100,
    Math.round((insights.avg_reuse || 0) * 1.2)
  );

  const intelligenceLevel =
    efficiencyScore > 80
      ? "High Intelligence"
      : efficiencyScore > 50
      ? "Adaptive"
      : "Learning";

  return (
    <div style={{ padding: 24 }}>
      <h1>Insights</h1>
      <p>System-level execution intelligence.</p>

      <div style={{ display: "flex", gap: 20, marginTop: 20 }}>
        <Card title="Total Runs" value={insights.total_runs} />
        <Card title="Average Reuse" value={`${insights.avg_reuse}%`} />
        <Card title="Best Workflow" value={insights.best_workflow} />
      </div>

      <div style={{ marginTop: 20 }}>
        <Card
          title="Accumulated Efficiency"
          value={`${insights.total_time_saved} ms saved`}
        />
      </div>

      {/* 🔥 NEW BLOCK */}
      <div style={{ marginTop: 30 }}>
        <h2>Execution Intelligence</h2>

        <div style={{ display: "flex", gap: 20, marginTop: 15 }}>
          <Card title="Efficiency Score" value={`${efficiencyScore}%`} />
          <Card title="System State" value={intelligenceLevel} />
          <Card
            title="Pattern Strength"
            value={
              insights.avg_reuse > 70
                ? "Stable Patterns"
                : "Evolving Patterns"
            }
          />
        </div>
      </div>
    </div>
  );
}

function Card({ title, value }) {
  return (
    <div
      style={{
        background: "#fff",
        padding: 20,
        borderRadius: 12,
        minWidth: 200,
        boxShadow: "0 2px 8px rgba(0,0,0,0.05)",
      }}
    >
      <div style={{ fontSize: 14, color: "#666" }}>{title}</div>
      <div style={{ fontSize: 24, fontWeight: "bold" }}>{value}</div>
    </div>
  );
}