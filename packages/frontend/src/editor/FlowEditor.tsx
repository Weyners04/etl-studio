import { useCallback, useEffect, useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import ReactFlow, {
  Background,
  Controls,
  addEdge,
  useEdgesState,
  useNodesState,
  type Connection,
  type Edge as RFEdge,
  type Node as RFNode,
} from "reactflow";
import "reactflow/dist/style.css";
import { toIR, type EtlNodeData } from "@/ir/serialize";
import { validateJob } from "@/api/client";
import EtlNode from "@/editor/nodes/EtlNode";

const nodeTypes = { etlNode: EtlNode };

function useDebounce<T>(value: T, delay: number): T {
  const [debounced, setDebounced] = useState<T>(value);
  useEffect(() => {
    const id = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(id);
  }, [value, delay]);
  return debounced;
}

const JOB_META = { id: "job-1", name: "Exemple" };

const INITIAL_NODES: RFNode<EtlNodeData>[] = [
  {
    id: "n1",
    type: "etlNode",
    position: { x: 100, y: 200 },
    data: { nodeType: "source.csv", params: { path: "data/input.csv" } },
  },
  {
    id: "n2",
    type: "etlNode",
    position: { x: 380, y: 200 },
    data: {
      nodeType: "transform.filter",
      params: { column: "age", operator: ">=", value: 18 },
    },
  },
  {
    id: "n3",
    type: "etlNode",
    position: { x: 660, y: 200 },
    data: { nodeType: "sink.parquet", params: { path: "data/output.parquet" } },
  },
];

const INITIAL_EDGES: RFEdge[] = [
  { id: "e1", source: "n1", target: "n2" },
  { id: "e2", source: "n2", target: "n3" },
];

export default function FlowEditor() {
  const [nodes, , onNodesChange] = useNodesState<EtlNodeData>(INITIAL_NODES);
  const [edges, setEdges, onEdgesChange] = useEdgesState(INITIAL_EDGES);

  const onConnect = useCallback(
    (c: Connection) => setEdges((eds) => addEdge(c, eds)),
    [setEdges],
  );

  const ir = useMemo(() => toIR(JOB_META, nodes, edges), [nodes, edges]);
  const debouncedIr = useDebounce(ir, 300);

  const { data: validationResult, isPending, isError, error } = useQuery({
    queryKey: ["validate", JSON.stringify(debouncedIr)],
    queryFn: () => validateJob(debouncedIr),
  });

  const errorNodeId =
    validationResult?.kind === "validation_error" ? validationResult.nodeId : null;

  const displayNodes: RFNode<EtlNodeData>[] = useMemo(
    () =>
      nodes.map(
        (n): RFNode<EtlNodeData> =>
          n.id === errorNodeId
            ? { ...n, style: { ...n.style, border: "2px solid red", borderRadius: 6 } }
            : n,
      ),
    [nodes, errorNodeId],
  );

  let statusText: string;
  let statusColor: string;
  if (isPending) {
    statusText = "Validation en cours…";
    statusColor = "#f5f5f5";
  } else if (isError) {
    statusText = `Erreur réseau : ${error?.message ?? "Erreur inconnue"}`;
    statusColor = "#fff8e1";
  } else if (validationResult?.kind === "ok") {
    statusText = "Valide";
    statusColor = "#e6f4ea";
  } else if (validationResult?.kind === "validation_error") {
    statusText = validationResult.message;
    statusColor = "#fce8e6";
  } else {
    statusText = "";
    statusColor = "#f5f5f5";
  }

  return (
    <div style={{ width: "100%", height: "100vh", position: "relative" }}>
      <ReactFlow
        nodes={displayNodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        nodeTypes={nodeTypes}
        fitView
      >
        <Background />
        <Controls />
      </ReactFlow>
      <div
        style={{
          position: "absolute",
          bottom: 12,
          left: "50%",
          transform: "translateX(-50%)",
          background: statusColor,
          border: "1px solid #ccc",
          borderRadius: 6,
          padding: "6px 14px",
          fontSize: 13,
          maxWidth: 480,
          whiteSpace: "nowrap",
          overflow: "hidden",
          textOverflow: "ellipsis",
          zIndex: 10,
          pointerEvents: "none",
        }}
      >
        {statusText}
      </div>
    </div>
  );
}
