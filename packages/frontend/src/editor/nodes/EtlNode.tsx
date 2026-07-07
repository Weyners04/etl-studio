import { Handle, Position, type NodeProps } from "reactflow";
import type { EtlNodeData } from "@/ir/serialize";
import { accentColor } from "./nodeColors";

export default function EtlNode({ data }: NodeProps<EtlNodeData>) {
  const color = accentColor(data.nodeType);
  return (
    <>
      <Handle type="target" position={Position.Left} />
      <div
        style={{
          background: "#fff",
          borderRadius: 4,
          boxShadow: "0 1px 4px rgba(0,0,0,0.12)",
          borderLeft: `4px solid ${color}`,
          padding: "8px 14px",
          minWidth: 140,
          fontFamily: "monospace",
          fontSize: 12,
          color: "#1e293b",
          userSelect: "none",
        }}
      >
        {data.nodeType}
      </div>
      <Handle type="source" position={Position.Right} />
    </>
  );
}
