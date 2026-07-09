interface Props {
  rowCount: number | null;
  sample: Record<string, unknown>[];
  onClose: () => void;
}

export default function SamplePanel({ rowCount, sample, onClose }: Props) {
  const columns = sample.length > 0 ? Object.keys(sample[0]) : [];
  const title = rowCount !== null ? `${rowCount} ligne(s)` : "Sink";

  return (
    <div
      onClick={(e) => e.stopPropagation()}
      style={{
        position: "absolute",
        top: 10,
        right: 10,
        width: 420,
        maxHeight: "75%",
        background: "#1e293b",
        border: "1px solid #334155",
        borderRadius: 8,
        zIndex: 10,
        display: "flex",
        flexDirection: "column",
        boxShadow: "0 4px 16px rgba(0,0,0,0.4)",
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          padding: "8px 12px",
          borderBottom: "1px solid #334155",
        }}
      >
        <span
          style={{
            fontFamily: "monospace",
            fontSize: 12,
            color: "#94a3b8",
            fontWeight: 600,
          }}
        >
          {title}
        </span>
        <button
          onClick={onClose}
          style={{
            background: "none",
            border: "none",
            color: "#64748b",
            cursor: "pointer",
            fontSize: 16,
            lineHeight: 1,
            padding: 0,
          }}
        >
          ×
        </button>
      </div>
      <div style={{ overflowY: "auto", overflowX: "auto", flex: 1 }}>
        {sample.length === 0 ? (
          <div
            style={{
              padding: "10px 12px",
              color: "#64748b",
              fontFamily: "monospace",
              fontSize: 12,
            }}
          >
            Aucune donnée
          </div>
        ) : (
          <table
            style={{
              borderCollapse: "collapse",
              fontFamily: "monospace",
              fontSize: 11,
              width: "100%",
            }}
          >
            <thead>
              <tr>
                {columns.map((col) => (
                  <th
                    key={col}
                    style={{
                      padding: "6px 10px",
                      textAlign: "left",
                      color: "#94a3b8",
                      fontWeight: 600,
                      borderBottom: "1px solid #334155",
                      whiteSpace: "nowrap",
                    }}
                  >
                    {col}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {sample.map((row, i) => (
                <tr key={i} style={{ background: i % 2 === 0 ? "transparent" : "#0f172a" }}>
                  {columns.map((col) => (
                    <td
                      key={col}
                      style={{
                        padding: "4px 10px",
                        color: "#e2e8f0",
                        maxWidth: 150,
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                        whiteSpace: "nowrap",
                      }}
                    >
                      {String(row[col] ?? "")}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
