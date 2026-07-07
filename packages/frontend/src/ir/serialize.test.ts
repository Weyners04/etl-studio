import { describe, expect, it } from "vitest";
import type { Edge as RFEdge, Node as RFNode } from "reactflow";
import { toIR, type EtlNodeData } from "./serialize";

const META = { id: "job-1", name: "Test Job" };

const NODES: RFNode<EtlNodeData>[] = [
  {
    id: "n1",
    type: "default",
    position: { x: 100, y: 200 },
    data: { nodeType: "source.csv", params: { path: "data.csv" } },
  },
  {
    id: "n2",
    type: "default",
    position: { x: 400, y: 200 },
    data: { nodeType: "sink.parquet", params: { path: "out.parquet" } },
  },
];

const EDGES: RFEdge[] = [{ id: "e1", source: "n1", target: "n2" }];

describe("toIR", () => {
  it("sets version, id and name from meta", () => {
    const ir = toIR(META, NODES, EDGES);
    expect(ir.version).toBe("0.1.0");
    expect(ir.id).toBe("job-1");
    expect(ir.name).toBe("Test Job");
  });

  it("uses data.nodeType as IR node type, not React Flow visual type", () => {
    const ir = toIR(META, NODES, EDGES);
    // NODES[*].type is "default" — toIR must use data.nodeType instead
    expect(ir.nodes[0].type).toBe("source.csv");
    expect(ir.nodes[1].type).toBe("sink.parquet");
  });

  it("maps params correctly", () => {
    const ir = toIR(META, NODES, EDGES);
    expect(ir.nodes[0].params).toEqual({ path: "data.csv" });
    expect(ir.nodes[1].params).toEqual({ path: "out.parquet" });
  });

  it("reduces edges to {id, source, target} only", () => {
    const ir = toIR(META, NODES, EDGES);
    expect(ir.edges[0]).toEqual({ id: "e1", source: "n1", target: "n2" });
    expect(Object.keys(ir.edges[0])).toHaveLength(3);
  });

  it("preserves node position", () => {
    const ir = toIR(META, NODES, EDGES);
    expect(ir.nodes[0].position).toEqual({ x: 100, y: 200 });
    expect(ir.nodes[1].position).toEqual({ x: 400, y: 200 });
  });
});
