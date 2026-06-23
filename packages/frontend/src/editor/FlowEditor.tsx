/**
 * Éditeur de flux visuel (React Flow) — squelette Phase 1.
 *
 * Le canvas est un producteur d'IR : les nœuds/arêtes édités ici se sérialisent vers IRGraph
 * (voir src/ir/serialize.ts) avant validation/exécution côté backend.
 */
import { useCallback } from "react";
import ReactFlow, {
  Background,
  Controls,
  addEdge,
  useEdgesState,
  useNodesState,
  type Connection,
} from "reactflow";
import "reactflow/dist/style.css";

export default function FlowEditor() {
  const [nodes, , onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  const onConnect = useCallback(
    (c: Connection) => setEdges((eds) => addEdge(c, eds)),
    [setEdges],
  );

  // TODO (Phase 1) : palette de nœuds (via listNodeTypes), panneau de params,
  // boutons Valider / Run (via src/api/client), sérialisation toIR/fromIR.

  return (
    <div style={{ width: "100%", height: "100vh" }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        fitView
      >
        <Background />
        <Controls />
      </ReactFlow>
    </div>
  );
}
