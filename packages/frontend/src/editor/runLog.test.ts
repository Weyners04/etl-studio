import { describe, expect, it } from "vitest";
import { formatRunStart, formatRunResult } from "./runLog";
import type { RunResult } from "@/api/client";

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
