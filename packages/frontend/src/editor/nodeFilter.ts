import type { NodeTypeInfo } from "@/api/client";

export function filterNodeTypes(types: NodeTypeInfo[], query: string): NodeTypeInfo[] {
  const q = query.trim().toLowerCase();
  if (!q) return types;
  return types.filter(
    (t) =>
      t.label.toLowerCase().includes(q) || t.description.toLowerCase().includes(q),
  );
}
