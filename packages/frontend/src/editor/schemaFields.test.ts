import { describe, expect, it } from "vitest";
import { schemaToFields, smartParse } from "./schemaFields";

// ---------------------------------------------------------------------------
// schemaToFields
// ---------------------------------------------------------------------------

describe("schemaToFields", () => {
  it("maps string property to text field", () => {
    const schema = {
      properties: { path: { title: "Path", type: "string" } },
      required: ["path"],
    };
    const fields = schemaToFields(schema);
    expect(fields).toHaveLength(1);
    expect(fields[0]).toEqual({ key: "path", label: "Path", kind: "text", required: true });
  });

  it("maps enum property to select field with options", () => {
    const schema = {
      properties: {
        operator: { title: "Operator", enum: ["==", "!=", ">", ">=", "<", "<="] },
      },
      required: ["operator"],
    };
    const fields = schemaToFields(schema);
    expect(fields[0].kind).toBe("select");
    expect(fields[0].options).toEqual(["==", "!=", ">", ">=", "<", "<="]);
    expect(fields[0].required).toBe(true);
  });

  it("maps anyOf to text-union field (repli pour les unions)", () => {
    const schema = {
      properties: {
        value: { title: "Value", anyOf: [{ type: "integer" }, { type: "string" }] },
      },
      required: ["value"],
    };
    const fields = schemaToFields(schema);
    expect(fields[0].kind).toBe("text-union");
  });

  it("maps boolean property to checkbox", () => {
    const schema = {
      properties: { has_header: { title: "Has Header", type: "boolean" } },
      required: [],
    };
    const fields = schemaToFields(schema);
    expect(fields[0].kind).toBe("checkbox");
    expect(fields[0].required).toBe(false);
  });

  it("maps array property to array-text", () => {
    const schema = {
      properties: { columns: { title: "Columns", type: "array", items: { type: "string" } } },
      required: ["columns"],
    };
    const fields = schemaToFields(schema);
    expect(fields[0].kind).toBe("array-text");
  });

  it("uses key as label when title is absent", () => {
    const schema = {
      properties: { my_field: { type: "string" } },
      required: [],
    };
    const fields = schemaToFields(schema);
    expect(fields[0].label).toBe("my_field");
  });

  it("returns empty array for schema without properties", () => {
    expect(schemaToFields({})).toEqual([]);
  });
});

// ---------------------------------------------------------------------------
// smartParse — règle de conversion documentée et intentionnelle
// ---------------------------------------------------------------------------

describe("smartParse", () => {
  it("converts integer strings to numbers", () => {
    expect(smartParse("42")).toBe(42);
    expect(typeof smartParse("42")).toBe("number");
    expect(smartParse("0")).toBe(0);
    expect(smartParse("-7")).toBe(-7);
  });

  it("converts float strings to numbers", () => {
    expect(smartParse("3.14")).toBeCloseTo(3.14);
    expect(typeof smartParse("3.14")).toBe("number");
  });

  it("converts 'true' and 'false' to booleans", () => {
    expect(smartParse("true")).toBe(true);
    expect(smartParse("false")).toBe(false);
    expect(typeof smartParse("true")).toBe("boolean");
  });

  it("keeps non-numeric, non-boolean strings as strings", () => {
    expect(smartParse("age")).toBe("age");
    expect(smartParse("data/in.csv")).toBe("data/in.csv");
    expect(typeof smartParse("age")).toBe("string");
  });

  it("keeps empty string as string (champ vide → validation échoue → rouge)", () => {
    expect(smartParse("")).toBe("");
    expect(typeof smartParse("")).toBe("string");
  });
});
