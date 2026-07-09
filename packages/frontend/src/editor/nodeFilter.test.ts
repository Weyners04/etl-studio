import { describe, expect, it } from "vitest";
import { filterNodeTypes } from "./nodeFilter";
import type { NodeTypeInfo } from "@/api/client";

function info(type: string, label: string, description: string): NodeTypeInfo {
  return { type, category: type.split(".")[0], label, description, paramsSchema: {} };
}

const TYPES: NodeTypeInfo[] = [
  info("source.csv", "CSVReader", "Lit un fichier CSV et charge ses lignes dans le pipeline."),
  info("transform.filter", "FilterRow", "Filtre les lignes selon une condition sur une colonne."),
  info("transform.select", "ColumnFilter", "Ne conserve que les colonnes sélectionnées."),
  info("sink.parquet", "ParquetWriter", "Écrit les données dans un fichier Parquet."),
];

describe("filterNodeTypes", () => {
  it("returns all types for an empty query", () => {
    expect(filterNodeTypes(TYPES, "")).toHaveLength(4);
    expect(filterNodeTypes(TYPES, "   ")).toHaveLength(4);
  });

  it("matches on label (case-insensitive)", () => {
    const result = filterNodeTypes(TYPES, "csv");
    expect(result).toHaveLength(1);
    expect(result[0].type).toBe("source.csv");

    const upper = filterNodeTypes(TYPES, "CSV");
    expect(upper).toHaveLength(1);
    expect(upper[0].type).toBe("source.csv");
  });

  it("matches on description (case-insensitive)", () => {
    const result = filterNodeTypes(TYPES, "colonne");
    expect(result.map((t) => t.type)).toContain("transform.filter");
    expect(result.map((t) => t.type)).toContain("transform.select");
  });

  it("returns an empty list when nothing matches", () => {
    expect(filterNodeTypes(TYPES, "zzz_no_match")).toHaveLength(0);
  });
});
