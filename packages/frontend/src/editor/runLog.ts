import type { DebugResult, RunResult } from "@/api/client";

export function timestamp(): string {
  const now = new Date();
  return [now.getHours(), now.getMinutes(), now.getSeconds()]
    .map((n) => String(n).padStart(2, "0"))
    .join(":");
}

export function formatRunStart(jobName: string, time: string): string {
  return `[${time}] Job "${jobName}" — démarrage`;
}

export function formatRunResult(result: RunResult, time: string): string {
  if (result.kind === "ok") {
    const files = result.outputs.map((o) => o.written).join(", ") || "—";
    return `[${time}] Exécution terminée — fichier(s) écrit(s) : ${files}`;
  }
  if (result.kind === "execution_error") {
    const cat = result.category.toUpperCase();
    return `[${time}] ERREUR nœud "${result.nodeId}" (${result.nodeType}) — ${cat} : ${result.message}`;
  }
  return `[${time}] ERREUR de validation : ${result.message}`;
}

export function formatDebugStart(jobName: string, time: string): string {
  return `[${time}] Job "${jobName}" — debug (pas-à-pas)`;
}

export function formatDebugResult(result: DebugResult, time: string): string {
  if (result.kind === "ok") {
    const n = result.nodes.length;
    const files = result.outputs.map((o) => o.written).join(", ") || "—";
    return `[${time}] Debug terminé — ${n} nœud(s) analysé(s), fichier(s) : ${files}`;
  }
  if (result.kind === "execution_error") {
    const cat = result.category.toUpperCase();
    const partial = result.partialNodes.length;
    return `[${time}] ERREUR nœud "${result.nodeId}" (${result.nodeType}) — ${cat} : ${result.message} (${partial} nœud(s) avant l'erreur)`;
  }
  return `[${time}] ERREUR de validation : ${result.message}`;
}
