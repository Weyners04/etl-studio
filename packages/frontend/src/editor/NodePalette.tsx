import type React from "react";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { listNodeTypes, type NodeTypeInfo } from "@/api/client";
import { accentColor } from "@/editor/nodes/nodeColors";
import { filterNodeTypes } from "@/editor/nodeFilter";

function PaletteItem({ info }: { info: NodeTypeInfo }) {
  const color = accentColor(info.type);

  function onDragStart(event: React.DragEvent<HTMLDivElement>) {
    event.dataTransfer.setData("application/etl-node-type", info.type);
    event.dataTransfer.effectAllowed = "move";
  }

  return (
    <div
      draggable
      onDragStart={onDragStart}
      title={info.description}
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
      {info.label}
    </div>
  );
}

export default function NodePalette() {
  const { data: nodeTypes, isPending, isError } = useQuery({
    queryKey: ["nodeTypes"],
    queryFn: listNodeTypes,
    staleTime: Infinity,
  });

  const [query, setQuery] = useState("");
  const filtered = filterNodeTypes(nodeTypes ?? [], query);

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
        display: "flex",
        flexDirection: "column",
        gap: 8,
      }}
    >
      <div
        style={{
          fontWeight: 600,
          fontSize: 11,
          textTransform: "uppercase",
          letterSpacing: "0.05em",
          color: "#64748b",
        }}
      >
        Nœuds
      </div>
      <input
        type="search"
        placeholder="Rechercher…"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        style={{
          width: "100%",
          boxSizing: "border-box",
          padding: "4px 8px",
          border: "1px solid #e2e8f0",
          borderRadius: 4,
          fontSize: 12,
          fontFamily: "inherit",
          color: "#1e293b",
          background: "#fff",
          outline: "none",
        }}
      />
      {isPending && (
        <div style={{ fontSize: 12, color: "#94a3b8" }}>Chargement…</div>
      )}
      {isError && (
        <div style={{ fontSize: 12, color: "#ef4444" }}>Erreur</div>
      )}
      <div>
        {filtered.map((info) => (
          <PaletteItem key={info.type} info={info} />
        ))}
        {!isPending && !isError && filtered.length === 0 && (
          <div style={{ fontSize: 12, color: "#94a3b8" }}>Aucun résultat</div>
        )}
      </div>
    </div>
  );
}
