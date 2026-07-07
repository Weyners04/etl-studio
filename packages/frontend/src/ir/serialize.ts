/**
 * Pont entre l'état React Flow et l'IR (le contrat dans les deux sens).
 *
 * toIR    : état du canvas (nodes/edges React Flow) -> IRGraph
 * fromIR  : IRGraph -> état du canvas
 */
import type { Edge as RFEdge, Node as RFNode } from "reactflow";
import type { IREdge, IRGraph, IRNode, NodeType } from "./types";

export interface EtlNodeData {
  nodeType: string;
  params: Record<string, unknown>;
}

export function toIR(
  meta: { id: string; name: string },
  nodes: RFNode<EtlNodeData>[],
  edges: RFEdge[],
): IRGraph {
  return {
    version: "0.1.0",
    id: meta.id,
    name: meta.name,
    nodes: nodes.map(
      (n): IRNode => ({
        id: n.id,
        type: n.data.nodeType as NodeType,
        params: n.data.params,
        position: n.position,
      }),
    ),
    edges: edges.map(
      (e): IREdge => ({
        id: e.id,
        source: e.source,
        target: e.target,
      }),
    ),
  };
}

export function fromIR(graph: IRGraph): { nodes: RFNode<EtlNodeData>[]; edges: RFEdge[] } {
  return {
    nodes: graph.nodes.map(
      (n): RFNode<EtlNodeData> => ({
        id: n.id,
        type: "default",
        position: n.position ?? { x: 0, y: 0 },
        data: { nodeType: n.type, params: n.params },
      }),
    ),
    edges: graph.edges.map(
      (e): RFEdge => ({
        id: e.id,
        source: e.source,
        target: e.target,
      }),
    ),
  };
}
