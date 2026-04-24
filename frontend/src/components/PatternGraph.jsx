import React from "react";

export default function PatternGraph({ patterns }) {
  if (!patterns || patterns.length === 0) return null;

  return (
  <div style={{ marginTop: 30, overflow: "hidden" }}>
      <h2>Pattern Graph</h2>
      <p>Visual relationship between execution families</p>

      <div style={styles.graph}>
        {patterns.map((p, i) => (
          <div key={i} style={styles.node}>
            <div style={styles.nodeCircle}>{p.seen}</div>
            <div style={styles.nodeLabel}>{p.family}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

const styles = {
  graph: {
  display: "flex",
  gap: 20,
  alignItems: "center",
  marginTop: 20,
  flexWrap: "wrap",
  maxWidth: "100%",
  overflowX: "auto",
},
  node: {
    textAlign: "center",
  },
  nodeCircle: {
    width: 60,
    height: 60,
    borderRadius: "50%",
    background: "linear-gradient(135deg,#4f46e5,#f97316)",
    color: "#fff",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontSize: 22,
    fontWeight: "bold",
    marginBottom: 8,
  },
  nodeLabel: {
    fontSize: 14,
    fontWeight: "500",
  },
};