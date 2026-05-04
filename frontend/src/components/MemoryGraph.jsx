import { useEffect, useRef } from "react";

export default function MemoryGraph({ data }) {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");

    let nodes = data?.nodes || [];
    let links = data?.links || [];

    const resize = () => {
      canvas.width = canvas.offsetWidth;
      canvas.height = canvas.offsetHeight;
    };
    resize();
    window.addEventListener("resize", resize);

    // init random positions
    nodes.forEach((n) => {
      n.x = Math.random() * canvas.width;
      n.y = Math.random() * canvas.height;
      n.vx = (Math.random() - 0.5) * 0.5;
      n.vy = (Math.random() - 0.5) * 0.5;
    });

    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // draw links
      links.forEach((l) => {
        const a = nodes[l.source];
        const b = nodes[l.target];

        ctx.strokeStyle = "rgba(59,130,246,0.3)";
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(a.x, a.y);
        ctx.lineTo(b.x, b.y);
        ctx.stroke();
      });

      // draw nodes
      nodes.forEach((n) => {
  const glow = Math.min(n.weight || 1, 5);

  const gradient = ctx.createRadialGradient(
    n.x,
    n.y,
    2,
    n.x,
    n.y,
    18 + glow * 6
  );

  gradient.addColorStop(0, "#2563eb");
  gradient.addColorStop(0.5, "rgba(59,130,246,0.5)");
  gradient.addColorStop(1, "rgba(59,130,246,0)");

  ctx.fillStyle = gradient;
  ctx.beginPath();
  ctx.arc(n.x, n.y, 6 + glow * 2, 0, Math.PI * 2);
  ctx.fill();
});