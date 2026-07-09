import type { DebugNodeResult } from "@/api/client";

/**
 * Construit la correspondance edgeId → rowCount à partir des résultats debug.
 *
 * Le comptage d'une arête est celui de son nœud SOURCE : les données qui
 * transitent sur l'arête sont celles produites par le nœud en amont.
 * Un nœud alimentant plusieurs arêtes (fan-out) donne le même comptage aux deux.
 * Les nœuds dont rowCount est null (sinks) n'apparaissent pas dans la Map.
 */
export function buildEdgeCounts(
  nodes: DebugNodeResult[],
  edges: { id: string; source: string }[],
): Map<string, number> {
  const byNodeId = new Map(
    nodes.filter((n) => n.rowCount !== null).map((n) => [n.nodeId, n.rowCount as number]),
  );
  return new Map(
    edges.filter((e) => byNodeId.has(e.source)).map((e) => [e.id, byNodeId.get(e.source)!]),
  );
}
