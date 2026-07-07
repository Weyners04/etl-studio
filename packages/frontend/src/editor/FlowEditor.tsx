import type React from "react";
import { useCallback, useEffect, useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import ReactFlow, {
  Background,
  Controls,
  addEdge,
  useEdgesState,
  useNodesState,
  useReactFlow,
  type Connection,
  type Edge as RFEdge,
  type Node as RFNode,
} from "reactflow";
import "reactflow/dist/style.css";
import { toIR, type EtlNodeData } from "@/ir/serialize";
import { validateJob, listNodeTypes } from "@/api/client";
import EtlNode from "@/editor/nodes/EtlNode";
import NodePalette from "@/editor/NodePalette";
import NodeParamsPanel from "@/editor/NodeParamsPanel";

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
  const [nodes, setNodes, onNodesChange] = useNodesState<EtlNodeData>(INITIAL_NODES);
  const [edges, setEdges, onEdgesChange] = useEdgesState(INITIAL_EDGES);
  const { screenToFlowPosition } = useReactFlow();

  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);

  // Même clé que NodePalette → TanStack retourne le cache immédiatement.
  const { data: nodeTypeInfos } = useQuery({
    queryKey: ["nodeTypes"],
    queryFn: listNodeTypes,
    staleTime: Infinity,
  });

  const onConnect = useCallback(
    (c: Connection) => setEdges((eds) => addEdge(c, eds)),
    [setEdges],
  );

  const onDragOver = useCallback((event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = "move";
  }, []);

  const onDrop = useCallback(
    (event: React.DragEvent<HTMLDivElement>) => {
      event.preventDefault();
      const nodeType = event.dataTransfer.getData("application/etl-node-type");
      if (!nodeType) return;
      const position = screenToFlowPosition({ x: event.clientX, y: event.clientY });
      const newNode: RFNode<EtlNodeData> = {
        id: crypto.randomUUID(),
        type: "etlNode",
        position,
        data: { nodeType, params: {} },
      };
      setNodes((nds) => [...nds, newNode]);
    },
    [screenToFlowPosition, setNodes],
  );

  const onNodeClick = useCallback(
    (_event: React.MouseEvent, node: RFNode<EtlNodeData>) => {
      setSelectedNodeId(node.id);
    },
    [],
  );

  const onPaneClick = useCallback((_event: React.MouseEvent) => {
    setSelectedNodeId(null);
  }, []);

  const onParamChange = useCallback(
    (key: string, value: unknown) => {
      if (!selectedNodeId) return;
      setNodes((nds) =>
        nds.map((n) =>
          n.id === selectedNodeId
            ? { ...n, data: { ...n.data, params: { ...n.data.params, [key]: value } } }
            : n,
        ),
      );
    },
    [selectedNodeId, setNodes],
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

  const selectedNode = selectedNodeId
    ? (nodes.find((n) => n.id === selectedNodeId) ?? null)
    : null;

  const selectedNodeTypeInfo = selectedNode
    ? (nodeTypeInfos?.find((info) => info.type === selectedNode.data.nodeType) ?? null)
    : null;

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
    <div style={{ width: "100%", height: "100vh", display: "flex" }}>
      <NodePalette />
      <div
        style={{ flex: 1, position: "relative" }}
        onDragOver={onDragOver}
        onDrop={onDrop}
      >
        <ReactFlow
          nodes={displayNodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onNodeClick={onNodeClick}
          onPaneClick={onPaneClick}
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
      {selectedNode && (
        <NodeParamsPanel
          nodeId={selectedNode.id}
          nodeType={selectedNode.data.nodeType}
          params={selectedNode.data.params}
          schema={selectedNodeTypeInfo?.paramsSchema ?? {}}
          onParamChange={onParamChange}
        />
      )}
    </div>
  );
}
