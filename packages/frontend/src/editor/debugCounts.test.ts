import { describe, expect, it } from "vitest";
import { buildEdgeCounts } from "./debugCounts";
import type { DebugNodeResult } from "@/api/client";

function node(nodeId: string, rowCount: number | null): DebugNodeResult {
  return { nodeId, rowCount, sample: [] };
}

describe("buildEdgeCounts", () => {
  it("maps each edge to the row count of its source node", () => {
    const nodes = [node("n1", 3), node("n2", 2), node("n3", null)];
    const edges = [
      { id: "e1", source: "n1" },
      { id: "e2", source: "n2" },
    ];
    const counts = buildEdgeCounts(nodes, edges);
    expect(counts.get("e1")).toBe(3);
    expect(counts.get("e2")).toBe(2);
  });

  it("fan-out: one source feeding two edges gets the same count on both", () => {
    const nodes = [node("n1", 5)];
    const edges = [
      { id: "e1", source: "n1" },
      { id: "e2", source: "n1" },
    ];
    const counts = buildEdgeCounts(nodes, edges);
    expect(counts.get("e1")).toBe(5);
    expect(counts.get("e2")).toBe(5);
  });

  it("sink with rowCount null produces no entry in the map", () => {
    const nodes = [node("n1", 3), node("n2", null)];
    const edges = [
      { id: "e1", source: "n1" },
      { id: "e2", source: "n2" },
    ];
    const counts = buildEdgeCounts(nodes, edges);
    expect(counts.has("e2")).toBe(false);
  });

  it("edge whose source has no debug result is absent from the map", () => {
    const nodes = [node("n1", 3)];
    const edges = [
      { id: "e1", source: "n1" },
      { id: "e2", source: "n_unknown" },
    ];
    const counts = buildEdgeCounts(nodes, edges);
    expect(counts.get("e1")).toBe(3);
    expect(counts.has("e2")).toBe(false);
  });

  it("returns an empty map for empty inputs", () => {
    expect(buildEdgeCounts([], []).size).toBe(0);
  });
});
