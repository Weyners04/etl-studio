import type { RunResult } from "@/api/client";

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
