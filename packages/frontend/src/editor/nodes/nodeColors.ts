export const ACCENT: Record<string, string> = {
  source: "#3b82f6",
  transform: "#f97316",
  sink: "#22c55e",
};
export const ACCENT_DEFAULT = "#94a3b8";

export function accentColor(nodeType: string): string {
  const prefix = nodeType.split(".")[0];
  return ACCENT[prefix] ?? ACCENT_DEFAULT;
}
