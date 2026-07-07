/** Client de l'API backend. */
import type { IRGraph } from "@/ir/types";

const BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:8000";

export type ValidationResult =
  | { kind: "ok" }
  | { kind: "validation_error"; message: string; nodeId: string | null; nodeType: string | null };

export async function listNodeTypes(): Promise<string[]> {
  const res = await fetch(`${BASE}/nodes`);
  const data = (await res.json()) as { types: string[] };
  return data.types;
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

export async function runJob(graph: IRGraph): Promise<unknown> {
  const res = await fetch(`${BASE}/jobs/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(graph),
  });
  return res.json();
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
