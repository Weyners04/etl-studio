export type FieldKind =
  | "text"
  | "text-union"
  | "number"
  | "checkbox"
  | "select"
  | "array-text"
  | "fallback";

export interface FieldDescriptor {
  key: string;
  label: string;
  kind: FieldKind;
  options?: string[];
  required: boolean;
}

/**
 * Convertit un JSON Schema Pydantic (object de properties) en liste de descripteurs
 * de champs, dans l'ordre des propriétés déclarées.
 * Repli honnête : tout type non reconnu produit un "fallback" (input texte).
 */
export function schemaToFields(schema: Record<string, unknown>): FieldDescriptor[] {
  const rawProperties = schema["properties"];
  if (typeof rawProperties !== "object" || rawProperties === null) return [];
  const properties = rawProperties as Record<string, Record<string, unknown>>;
  const required = (schema["required"] as string[] | undefined) ?? [];

  return Object.entries(properties).map(([key, prop]) => {
    const label = typeof prop["title"] === "string" ? prop["title"] : key;
    const isRequired = required.includes(key);

    if (Array.isArray(prop["enum"])) {
      return {
        key,
        label,
        kind: "select" as const,
        options: prop["enum"] as string[],
        required: isRequired,
      };
    }
    if (Array.isArray(prop["anyOf"])) {
      return { key, label, kind: "text-union" as const, required: isRequired };
    }
    const type = prop["type"];
    if (type === "boolean") return { key, label, kind: "checkbox" as const, required: isRequired };
    if (type === "integer" || type === "number") {
      return { key, label, kind: "number" as const, required: isRequired };
    }
    if (type === "array") {
      return { key, label, kind: "array-text" as const, required: isRequired };
    }
    if (type === "string") return { key, label, kind: "text" as const, required: isRequired };
    return { key, label, kind: "fallback" as const, required: isRequired };
  });
}

/**
 * Convertit une saisie texte en la valeur typée la plus spécifique.
 * Utilisé pour les champs anyOf (text-union) afin de ne pas toujours stocker une string
 * quand l'IR attend un number ou un boolean.
 *
 * Règle :
 *   "true" / "false"  → boolean
 *   chaîne numérique  → integer si entier, number sinon
 *   autre             → string
 */
export function smartParse(raw: string): unknown {
  if (raw === "true") return true;
  if (raw === "false") return false;
  if (raw !== "" && !isNaN(Number(raw))) {
    const n = Number(raw);
    return Number.isInteger(n) ? n : n;
  }
  return raw;
}

/** Convertit une valeur IR en string affichable dans un input texte. */
export function valueToString(value: unknown): string {
  if (value === null || value === undefined) return "";
  if (typeof value === "boolean") return value ? "true" : "false";
  return String(value);
}
