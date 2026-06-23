/** Client de l'API backend. */
import type { IRGraph } from "@/ir/types";

const BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:8000";

export async function listNodeTypes(): Promise<string[]> {
  const res = await fetch(`${BASE}/nodes`);
  const data = (await res.json()) as { types: string[] };
  return data.types;
}

export async function validateJob(graph: IRGraph): Promise<void> {
  const res = await fetch(`${BASE}/jobs/validate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(graph),
  });
  if (!res.ok) throw new Error((await res.json()).detail ?? "Validation échouée");
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
