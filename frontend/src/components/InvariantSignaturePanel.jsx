export default function InvariantSignaturePanel() {
  return (
    <div className="mt-6 bg-white/70 backdrop-blur-xl border border-slate-200 rounded-2xl p-6 shadow-sm">

      {/* Header */}
      <div className="mb-4">
        <div className="text-xs font-semibold tracking-wide text-indigo-500 uppercase">
          Invariant Signature
        </div>
        <div className="text-sm text-slate-500">
          Structural identity that allows safe execution reuse
        </div>
      </div>

      {/* Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">

        {/* Structural Class */}
        <div className="p-4 rounded-xl bg-slate-50 border">
          <div className="text-xs text-slate-400">Structural Class</div>
          <div className="text-lg font-semibold text-slate-800">
            Creative Pipeline
          </div>
        </div>

        {/* Input Shape */}
        <div className="p-4 rounded-xl bg-slate-50 border">
          <div className="text-xs text-slate-400">Input Shape</div>
          <div className="text-lg font-semibold text-slate-800">
            Image → Transform → Export
          </div>
        </div>

        {/* Stable Invariants */}
        <div className="p-4 rounded-xl bg-slate-50 border col-span-1 md:col-span-2">
          <div className="text-xs text-slate-400">Stable Invariants</div>
          <ul className="mt-2 text-sm text-slate-700 list-disc pl-5 space-y-1">
            <li>Decode → Resize → Optimize → Export</li>
            <li>Output format consistency (PNG)</li>
            <li>Resolution normalization preserved</li>
          </ul>
        </div>

        {/* Reuse Safety */}
        <div className="p-4 rounded-xl bg-green-50 border border-green-200">
          <div className="text-xs text-green-500">Reuse Safety</div>
          <div className="text-lg font-semibold text-green-700">
            SAFE
          </div>
        </div>

        {/* Decision Reason */}
        <div className="p-4 rounded-xl bg-blue-50 border border-blue-200">
          <div className="text-xs text-blue-500">Decision Reason</div>
          <div className="text-sm font-medium text-blue-700">
            Execution consequence remains identical across runs
          </div>
        </div>

      </div>
    </div>
  );
}