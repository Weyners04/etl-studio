import { accentColor } from "@/editor/nodes/nodeColors";
import {
  schemaToFields,
  smartParse,
  valueToString,
  type FieldDescriptor,
} from "@/editor/schemaFields";

interface Props {
  nodeId: string;
  nodeType: string;
  params: Record<string, unknown>;
  schema: Record<string, unknown>;
  onParamChange: (key: string, value: unknown) => void;
}

function FieldInput({
  field,
  value,
  onChange,
}: {
  field: FieldDescriptor;
  value: unknown;
  onChange: (val: unknown) => void;
}) {
  const inputStyle = {
    width: "100%",
    padding: "4px 6px",
    fontSize: 12,
    border: "1px solid #cbd5e1",
    borderRadius: 3,
    boxSizing: "border-box" as const,
    fontFamily: "monospace",
  };

  switch (field.kind) {
    case "select":
      return (
        <select
          value={String(value ?? "")}
          onChange={(e) => onChange(e.target.value)}
          style={inputStyle}
        >
          {!value && <option value="">—</option>}
          {field.options?.map((opt) => (
            <option key={opt} value={opt}>
              {opt}
            </option>
          ))}
        </select>
      );

    case "checkbox":
      return (
        <input
          type="checkbox"
          checked={Boolean(value)}
          onChange={(e) => onChange(e.target.checked)}
          style={{ cursor: "pointer" }}
        />
      );

    case "number":
      return (
        <input
          type="number"
          value={value === undefined || value === "" ? "" : String(value)}
          onChange={(e) => {
            const n = e.target.valueAsNumber;
            onChange(isNaN(n) ? undefined : n);
          }}
          style={inputStyle}
        />
      );

    case "array-text":
      return (
        <input
          type="text"
          value={Array.isArray(value) ? value.join(", ") : String(value ?? "")}
          onChange={(e) => {
            const arr = e.target.value
              .split(",")
              .map((s) => s.trim())
              .filter((s) => s.length > 0);
            onChange(arr);
          }}
          placeholder="col1, col2, col3"
          style={inputStyle}
        />
      );

    case "text-union":
      return (
        <input
          type="text"
          value={valueToString(value)}
          onChange={(e) => onChange(smartParse(e.target.value))}
          style={inputStyle}
        />
      );

    case "text":
    case "fallback":
    default:
      return (
        <input
          type="text"
          value={String(value ?? "")}
          onChange={(e) => onChange(e.target.value)}
          style={inputStyle}
        />
      );
  }
}

export default function NodeParamsPanel({
  nodeType,
  params,
  schema,
  onParamChange,
}: Props) {
  const color = accentColor(nodeType);
  const fields = schemaToFields(schema);

  return (
    <div
      style={{
        width: 240,
        height: "100%",
        borderLeft: "1px solid #e2e8f0",
        background: "#f8fafc",
        display: "flex",
        flexDirection: "column",
        flexShrink: 0,
        overflowY: "auto",
      }}
    >
      <div
        style={{
          borderLeft: `4px solid ${color}`,
          padding: "10px 12px",
          background: "#fff",
          borderBottom: "1px solid #e2e8f0",
        }}
      >
        <div style={{ fontFamily: "monospace", fontSize: 12, color: "#1e293b" }}>
          {nodeType}
        </div>
      </div>

      <div style={{ padding: 12, display: "flex", flexDirection: "column", gap: 12 }}>
        {fields.length === 0 && (
          <div style={{ fontSize: 12, color: "#94a3b8" }}>Aucun paramètre</div>
        )}
        {fields.map((field) => (
          <div key={field.key}>
            <label
              style={{
                display: "block",
                fontSize: 11,
                fontWeight: 600,
                color: "#475569",
                marginBottom: 4,
                textTransform: "uppercase",
                letterSpacing: "0.04em",
              }}
            >
              {field.label}
              {field.required && (
                <span style={{ color: "#ef4444", marginLeft: 2 }}>*</span>
              )}
            </label>
            <FieldInput
              field={field}
              value={params[field.key]}
              onChange={(val) => onParamChange(field.key, val)}
            />
          </div>
        ))}
      </div>
    </div>
  );
}
