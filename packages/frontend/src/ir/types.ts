/**
 * Types de la représentation intermédiaire (IR), côté frontend.
 *
 * Traduction TypeScript du contrat défini dans
 * packages/ir-schema/schema/ir.schema.json — source de vérité partagée avec le backend.
 * L'éditeur visuel est un *producteur* d'IR : le canvas sérialise vers ces types.
 */

export interface Position {
  x: number;
  y: number;
}

export type NodeType = `source.${string}` | `transform.${string}` | `sink.${string}`;

export interface IRNode {
  id: string;
  type: NodeType;
  params: Record<string, unknown>;
  position?: Position;
}

export interface IREdge {
  id: string;
  source: string;
  target: string;
  sourcePort?: string;
  targetPort?: string;
}

export interface IRGraph {
  version: string;
  id: string;
  name: string;
  nodes: IRNode[];
  edges: IREdge[];
}
