import type React from "react";
import { useCallback, useEffect, useMemo, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
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
import { debugJob, runJob, validateJob, listNodeTypes, type DebugNodeResult } from "@/api/client";
import EtlNode from "@/editor/nodes/EtlNode";
import NodePalette from "@/editor/NodePalette";
import NodeParamsPanel from "@/editor/NodeParamsPanel";
import RunConsole from "@/editor/RunConsole";
import SamplePanel from "@/editor/SamplePanel";
import { buildEdgeCounts } from "@/editor/debugCounts";
import {
  formatDebugResult,
  formatDebugStart,
  formatRunResult,
  formatRunStart,
  timestamp,
} from "@/editor/runLog";

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
  const [logEntries, setLogEntries] = useState<string[]>([]);
  const [execErrorNodeId, setExecErrorNodeId] = useState<string | null>(null);
  const [debugResults, setDebugResults] = useState<DebugNodeResult[]>([]);
  const [selectedEdgeId, setSelectedEdgeId] = useState<string | null>(null);

  // Même clé que NodePalette → TanStack retourne le cache immédiatement.
  const { data: nodeTypeInfos } = useQuery({
    queryKey: ["nodeTypes"],
    queryFn: listNodeTypes,
    staleTime: Infinity,
  });

  const ir = useMemo(() => toIR(JOB_META, nodes, edges), [nodes, edges]);
  const debouncedIr = useDebounce(ir, 300);

  // Efface les résultats debug dès que le graphe change.
  useEffect(() => {
    setDebugResults([]);
    setSelectedEdgeId(null);
  }, [ir]);

  const { data: validationResult, isPending, isError, error } = useQuery({
    queryKey: ["validate", JSON.stringify(debouncedIr)],
    queryFn: () => validateJob(debouncedIr),
  });

  const mutation = useMutation({
    mutationFn: runJob,
    onMutate: () => {
      setLogEntries([formatRunStart(JOB_META.name, timestamp())]);
      setExecErrorNodeId(null);
    },
    onSuccess: (result) => {
      setLogEntries((prev) => [...prev, formatRunResult(result, timestamp())]);
      if (result.kind === "execution_error") setExecErrorNodeId(result.nodeId);
    },
    onError: (err: Error) => {
      setLogEntries((prev) => [
        ...prev,
        `[${timestamp()}] ERREUR réseau : ${err.message}`,
      ]);
    },
  });

  const debugMutation = useMutation({
    mutationFn: debugJob,
    onMutate: () => {
      setLogEntries([formatDebugStart(JOB_META.name, timestamp())]);
      setExecErrorNodeId(null);
      setDebugResults([]);
      setSelectedEdgeId(null);
    },
    onSuccess: (result) => {
      setLogEntries((prev) => [...prev, formatDebugResult(result, timestamp())]);
      if (result.kind === "ok") {
        setDebugResults(result.nodes);
      } else if (result.kind === "execution_error") {
        setExecErrorNodeId(result.nodeId);
        setDebugResults(result.partialNodes);
      }
    },
    onError: (err: Error) => {
      setLogEntries((prev) => [
        ...prev,
        `[${timestamp()}] ERREUR réseau : ${err.message}`,
      ]);
    },
  });

  const edgeCounts = useMemo(
    () => buildEdgeCounts(debugResults, edges),
    [debugResults, edges],
  );

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
    setSelectedEdgeId(null);
  }, []);

  const onEdgeClick = useCallback((_event: React.MouseEvent, edge: RFEdge) => {
    setSelectedEdgeId(edge.id);
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

  const validationErrorNodeId =
    validationResult?.kind === "validation_error" ? validationResult.nodeId : null;

  const displayNodes: RFNode<EtlNodeData>[] = useMemo(
    () =>
      nodes.map((n): RFNode<EtlNodeData> => {
        const isError =
          (validationErrorNodeId !== null && n.id === validationErrorNodeId) ||
          (execErrorNodeId !== null && n.id === execErrorNodeId);
        return isError
          ? { ...n, style: { ...n.style, border: "2px solid red", borderRadius: 6 } }
          : n;
      }),
    [nodes, validationErrorNodeId, execErrorNodeId],
  );

  const displayEdges: RFEdge[] = useMemo(
    () =>
      edges.map((e) => {
        const count = edgeCounts.get(e.id);
        return count !== undefined ? { ...e, label: `${count} lignes` } : e;
      }),
    [edges, edgeCounts],
  );

  const selectedNode = selectedNodeId
    ? (nodes.find((n) => n.id === selectedNodeId) ?? null)
    : null;

  const selectedNodeTypeInfo = selectedNode
    ? (nodeTypeInfos?.find((info) => info.type === selectedNode.data.nodeType) ?? null)
    : null;

  // Données de l'échantillon pour l'arête sélectionnée (nœud source).
  const selectedEdge = selectedEdgeId ? (edges.find((e) => e.id === selectedEdgeId) ?? null) : null;
  const sampleNode = selectedEdge
    ? (debugResults.find((r) => r.nodeId === selectedEdge.source) ?? null)
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
    <div style={{ width: "100%", height: "100vh", display: "flex", flexDirection: "column" }}>
      {/* Zone principale : palette | canvas | params */}
      <div style={{ display: "flex", flex: 1, minHeight: 0 }}>
        <NodePalette />
        <div
          style={{ flex: 1, position: "relative" }}
          onDragOver={onDragOver}
          onDrop={onDrop}
        >
          <ReactFlow
            nodes={displayNodes}
            edges={displayEdges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onNodeClick={onNodeClick}
            onEdgeClick={onEdgeClick}
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
          {sampleNode && (
            <SamplePanel
              rowCount={sampleNode.rowCount}
              sample={sampleNode.sample}
              onClose={() => setSelectedEdgeId(null)}
            />
          )}
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
      {/* Console d'exécution pleine largeur */}
      <RunConsole
        entries={logEntries}
        onRun={() => mutation.mutate(ir)}
        onDebug={() => debugMutation.mutate(ir)}
        canRun={validationResult?.kind === "ok"}
        isRunning={mutation.isPending}
        isDebugging={debugMutation.isPending}
      />
    </div>
  );
}
