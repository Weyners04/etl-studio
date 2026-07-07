import type React from "react";
import { useQuery } from "@tanstack/react-query";
import { listNodeTypes } from "@/api/client";
import { accentColor } from "@/editor/nodes/nodeColors";

function PaletteItem({ nodeType }: { nodeType: string }) {
  const color = accentColor(nodeType);

  function onDragStart(event: React.DragEvent<HTMLDivElement>) {
    event.dataTransfer.setData("application/etl-node-type", nodeType);
    event.dataTransfer.effectAllowed = "move";
  }

  return (
    <div
      draggable
      onDragStart={onDragStart}
      style={{
        display: "flex",
        alignItems: "center",
        padding: "6px 10px",
        margin: "2px 0",
        borderLeft: `4px solid ${color}`,
        background: "#fff",
        borderRadius: 3,
        cursor: "grab",
        fontFamily: "monospace",
        fontSize: 12,
        color: "#1e293b",
        userSelect: "none",
      }}
    >
      {nodeType}
    </div>
  );
}

export default function NodePalette() {
  const { data: nodeTypes, isPending, isError } = useQuery({
    queryKey: ["nodeTypes"],
    queryFn: listNodeTypes,
    staleTime: Infinity,
  });

  return (
    <div
      style={{
        width: 180,
        height: "100%",
        background: "#f8fafc",
        borderRight: "1px solid #e2e8f0",
        padding: 12,
        overflowY: "auto",
        boxSizing: "border-box",
        flexShrink: 0,
      }}
    >
      <div
        style={{
          fontWeight: 600,
          fontSize: 11,
          textTransform: "uppercase",
          letterSpacing: "0.05em",
          color: "#64748b",
          marginBottom: 8,
        }}
      >
        Nœuds
      </div>
      {isPending && (
        <div style={{ fontSize: 12, color: "#94a3b8" }}>Chargement…</div>
      )}
      {isError && (
        <div style={{ fontSize: 12, color: "#ef4444" }}>Erreur</div>
      )}
      {nodeTypes?.map((info) => (
        <PaletteItem key={info.type} nodeType={info.type} />
      ))}
    </div>
  );
}
