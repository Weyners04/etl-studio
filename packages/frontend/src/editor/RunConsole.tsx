import { useEffect, useRef } from "react";

interface Props {
  entries: string[];
  onRun: () => void;
  onDebug: () => void;
  canRun: boolean;
  isRunning: boolean;
  isDebugging: boolean;
}

export default function RunConsole({
  entries,
  onRun,
  onDebug,
  canRun,
  isRunning,
  isDebugging,
}: Props) {
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [entries]);

  const isBusy = isRunning || isDebugging;
  const runActive = canRun && !isBusy;
  const debugActive = canRun && !isBusy;

  return (
    <div
      style={{
        borderTop: "1px solid #e2e8f0",
        background: "#0f172a",
        display: "flex",
        flexDirection: "column",
        height: 180,
        flexShrink: 0,
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 10,
          padding: "6px 12px",
          borderBottom: "1px solid #1e293b",
        }}
      >
        <button
          onClick={onRun}
          disabled={!runActive}
          style={{
            background: runActive ? "#22c55e" : "#334155",
            color: runActive ? "#fff" : "#94a3b8",
            border: "none",
            borderRadius: 4,
            padding: "4px 14px",
            fontSize: 12,
            fontWeight: 600,
            cursor: runActive ? "pointer" : "not-allowed",
            transition: "background 0.15s",
          }}
        >
          {isRunning ? "Exécution…" : "Exécuter"}
        </button>
        <button
          onClick={onDebug}
          disabled={!debugActive}
          style={{
            background: debugActive ? "#3b82f6" : "#334155",
            color: debugActive ? "#fff" : "#94a3b8",
            border: "none",
            borderRadius: 4,
            padding: "4px 14px",
            fontSize: 12,
            fontWeight: 600,
            cursor: debugActive ? "pointer" : "not-allowed",
            transition: "background 0.15s",
          }}
        >
          {isDebugging ? "Debug…" : "Debug"}
        </button>
        <span
          style={{
            fontFamily: "monospace",
            fontSize: 11,
            color: "#475569",
            textTransform: "uppercase",
            letterSpacing: "0.05em",
          }}
        >
          Console
        </span>
      </div>
      <div
        style={{
          flex: 1,
          overflowY: "auto",
          padding: "6px 12px",
          fontFamily: "monospace",
          fontSize: 12,
          color: "#e2e8f0",
          lineHeight: 1.6,
        }}
      >
        {entries.length === 0 ? (
          <span style={{ color: "#475569" }}>Aucune exécution</span>
        ) : (
          entries.map((entry, i) => <div key={i}>{entry}</div>)
        )}
        <div ref={endRef} />
      </div>
    </div>
  );
}
