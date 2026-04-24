export default function FocusHeader({ activeTab }) {

  const tabTitle = {
    execution: "Execution Engine",
    memory: "Memory Core",
    pattern: "Pattern Map",
    intel: "System Intelligence",
    queue: "Upload Queue"
  };

  return (
    <div className="focus-header">

      <div className="focus-left">
        <div className="focus-logo">M-OS</div>
        <div className="focus-title">{tabTitle[activeTab]}</div>
      </div>

      <div className="focus-center">
        <div className="mini-orb"></div>
      </div>

      <div className="focus-actions">
        <button>Upload</button>
        <button>Run Demo</button>
        <button>Run Similar</button>
        <button>Run Bundle</button>
      </div>

    </div>
  );
}