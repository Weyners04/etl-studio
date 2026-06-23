/**
 * Pont entre l'état React Flow et l'IR (le contrat dans les deux sens).
 *
 * toIR    : état du canvas (nodes/edges React Flow) -> IRGraph
 * fromIR  : IRGraph -> état du canvas
 *
 * TODO (Phase 1) : implémenter la correspondance complète des champs / params.
 */
import type { Edge as RFEdge, Node as RFNode } from "reactflow";
import type { IRGraph } from "./types";

export function toIR(_meta: { id: string; name: string }, _nodes: RFNode[], _edges: RFEdge[]): IRGraph {
  throw new Error("toIR : à implémenter en Phase 1.");
}

export function fromIR(_graph: IRGraph): { nodes: RFNode[]; edges: RFEdge[] } {
  throw new Error("fromIR : à implémenter en Phase 1.");
}
