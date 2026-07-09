import { describe, expect, it } from "vitest";
import { formatDebugResult, formatDebugStart, formatRunResult, formatRunStart } from "./runLog";
import type { DebugResult, RunResult } from "@/api/client";

describe("formatRunStart", () => {
  it("formats the start log line with job name and time", () => {
    expect(formatRunStart("Mon job", "14:30:00")).toBe('[14:30:00] Job "Mon job" — démarrage');
  });
});

describe("formatRunResult", () => {
  it("formats ok result listing written files", () => {
    const result: RunResult = {
      kind: "ok",
      outputs: [{ nodeId: "n2", written: "out/result.parquet" }],
    };
    expect(formatRunResult(result, "14:30:01")).toBe(
      "[14:30:01] Exécution terminée — fichier(s) écrit(s) : out/result.parquet",
    );
  });

  it("shows dash when ok result has no outputs", () => {
    const result: RunResult = { kind: "ok", outputs: [] };
    expect(formatRunResult(result, "14:30:01")).toBe(
      "[14:30:01] Exécution terminée — fichier(s) écrit(s) : —",
    );
  });

  it("formats execution_error with uppercased category and node info", () => {
    const result: RunResult = {
      kind: "execution_error",
      message: "fichier introuvable",
      nodeId: "n1",
      nodeType: "source.csv",
      category: "resource",
    };
    expect(formatRunResult(result, "14:30:02")).toBe(
      '[14:30:02] ERREUR nœud "n1" (source.csv) — RESOURCE : fichier introuvable',
    );
  });

  it("formats validation_error with message only", () => {
    const result: RunResult = {
      kind: "validation_error",
      message: "path manquant",
      nodeId: "n1",
      nodeType: "source.csv",
    };
    expect(formatRunResult(result, "14:30:03")).toBe(
      "[14:30:03] ERREUR de validation : path manquant",
    );
  });
});

describe("formatDebugStart", () => {
  it("formats the debug start log line with job name and time", () => {
    expect(formatDebugStart("Mon job", "09:00:00")).toBe(
      '[09:00:00] Job "Mon job" — debug (pas-à-pas)',
    );
  });
});

describe("formatDebugResult", () => {
  it("formats ok result with node count and written files", () => {
    const result: DebugResult = {
      kind: "ok",
      nodes: [
        { nodeId: "n1", rowCount: 3, sample: [] },
        { nodeId: "n2", rowCount: null, sample: [] },
      ],
      outputs: [{ nodeId: "n2", written: "out/result.csv" }],
    };
    expect(formatDebugResult(result, "09:00:01")).toBe(
      "[09:00:01] Debug terminé — 2 nœud(s) analysé(s), fichier(s) : out/result.csv",
    );
  });

  it("formats execution_error with partial node count", () => {
    const result: DebugResult = {
      kind: "execution_error",
      message: "fichier introuvable",
      nodeId: "n1",
      nodeType: "source.csv",
      category: "resource",
      partialNodes: [{ nodeId: "n0", rowCount: 5, sample: [] }],
    };
    expect(formatDebugResult(result, "09:00:02")).toBe(
      '[09:00:02] ERREUR nœud "n1" (source.csv) — RESOURCE : fichier introuvable (1 nœud(s) avant l\'erreur)',
    );
  });

  it("formats validation_error with message only", () => {
    const result: DebugResult = {
      kind: "validation_error",
      message: "cycle détecté",
      nodeId: null,
      nodeType: null,
    };
    expect(formatDebugResult(result, "09:00:03")).toBe(
      "[09:00:03] ERREUR de validation : cycle détecté",
    );
  });
});
