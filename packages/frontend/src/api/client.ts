/** Client de l'API backend. */
import type { IRGraph } from "@/ir/types";

const BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:8000";

export type ValidationResult =
  | { kind: "ok" }
  | { kind: "validation_error"; message: string; nodeId: string | null; nodeType: string | null };

export interface NodeTypeInfo {
  type: string;
  category: string;
  label: string;
  description: string;
  paramsSchema: Record<string, unknown>;
}

export async function listNodeTypes(): Promise<NodeTypeInfo[]> {
  const res = await fetch(`${BASE}/nodes`);
  const raw = (await res.json()) as {
    type: string;
    category: string;
    label: string;
    description: string;
    params_schema: Record<string, unknown>;
  }[];
  return raw.map((n) => ({
    type: n.type,
    category: n.category,
    label: n.label,
    description: n.description,
    paramsSchema: n.params_schema,
  }));
}

export async function validateJob(graph: IRGraph): Promise<ValidationResult> {
  const res = await fetch(`${BASE}/jobs/validate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(graph),
  });
  if (res.ok) return { kind: "ok" };
  if (res.status === 422) {
    const body = (await res.json()) as {
      detail: { message: string; node_id: string | null; node_type: string | null };
    };
    return {
      kind: "validation_error",
      message: body.detail.message,
      nodeId: body.detail.node_id,
      nodeType: body.detail.node_type,
    };
  }
  throw new Error(`Erreur serveur : ${res.status}`);
}

export type RunResult =
  | { kind: "ok"; outputs: { nodeId: string; written: string }[] }
  | { kind: "validation_error"; message: string; nodeId: string | null; nodeType: string | null }
  | { kind: "execution_error"; message: string; nodeId: string | null; nodeType: string | null; category: string };

export async function runJob(graph: IRGraph): Promise<RunResult> {
  const res = await fetch(`${BASE}/jobs/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(graph),
  });
  if (res.ok) {
    const body = (await res.json()) as {
      status: string;
      outputs: { node_id: string; written: string }[];
    };
    return {
      kind: "ok",
      outputs: body.outputs.map((o) => ({ nodeId: o.node_id, written: o.written })),
    };
  }
  if (res.status === 422) {
    const body = (await res.json()) as {
      detail: {
        error_type: string;
        message: string;
        node_id: string | null;
        node_type: string | null;
        category?: string;
      };
    };
    const d = body.detail;
    if (d.error_type === "execution_error") {
      return {
        kind: "execution_error",
        message: d.message,
        nodeId: d.node_id,
        nodeType: d.node_type,
        category: d.category ?? "unknown",
      };
    }
    return {
      kind: "validation_error",
      message: d.message,
      nodeId: d.node_id,
      nodeType: d.node_type,
    };
  }
  throw new Error(`Erreur serveur : ${res.status}`);
}

export interface DebugNodeResult {
  nodeId: string;
  rowCount: number | null;
  sample: Record<string, unknown>[];
}

export type DebugResult =
  | { kind: "ok"; nodes: DebugNodeResult[]; outputs: { nodeId: string; written: string }[] }
  | {
      kind: "execution_error";
      message: string;
      nodeId: string | null;
      nodeType: string | null;
      category: string;
      partialNodes: DebugNodeResult[];
    }
  | { kind: "validation_error"; message: string; nodeId: string | null; nodeType: string | null };

export async function debugJob(graph: IRGraph): Promise<DebugResult> {
  const res = await fetch(`${BASE}/jobs/debug`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(graph),
  });
  if (res.ok) {
    const body = (await res.json()) as {
      status: string;
      nodes: { node_id: string; row_count: number | null; sample: Record<string, unknown>[] }[];
      outputs: { node_id: string; written: string }[];
    };
    return {
      kind: "ok",
      nodes: body.nodes.map((n) => ({ nodeId: n.node_id, rowCount: n.row_count, sample: n.sample })),
      outputs: body.outputs.map((o) => ({ nodeId: o.node_id, written: o.written })),
    };
  }
  if (res.status === 422) {
    const body = (await res.json()) as {
      detail: {
        error_type: string;
        message: string;
        node_id: string | null;
        node_type: string | null;
        category?: string;
        partial_nodes?: { node_id: string; row_count: number | null; sample: Record<string, unknown>[] }[];
      };
    };
    const d = body.detail;
    if (d.error_type === "execution_error") {
      return {
        kind: "execution_error",
        message: d.message,
        nodeId: d.node_id,
        nodeType: d.node_type,
        category: d.category ?? "unknown",
        partialNodes: (d.partial_nodes ?? []).map((n) => ({
          nodeId: n.node_id,
          rowCount: n.row_count,
          sample: n.sample,
        })),
      };
    }
    return {
      kind: "validation_error",
      message: d.message,
      nodeId: d.node_id,
      nodeType: d.node_type,
    };
  }
  throw new Error(`Erreur serveur : ${res.status}`);
}

/** Génération IA — Phase 2. */
export async function generateFromPrompt(prompt: string): Promise<IRGraph> {
  const res = await fetch(`${BASE}/ai/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt }),
  });
  return res.json() as Promise<IRGraph>;
}
