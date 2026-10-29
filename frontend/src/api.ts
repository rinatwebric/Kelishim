const BASE: string =
  (import.meta as unknown as { env?: Record<string, string> }).env?.VITE_API_URL ??
  "http://localhost:8000";

export type Condition = {
  term: string;
  value: unknown;
  currency?: string | null;
  quote?: string | null;
  confidence?: number;
  hedged?: boolean;
};

export type Row = {
  term: string;
  status: "unknown" | "single" | "match" | "conflict";
  entries: Condition[];
  needs_manual_check: boolean;
};

async function req(path: string, init?: RequestInit) {
  const r = await fetch(BASE + path, {
    ...init,
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
  });
  if (!r.ok) {
    const t = await r.text();
    throw new Error(`API ${r.status}: ${t}`);
  }
  return r.json();
}

export const api = {
  createDeal: (): Promise<{ id: string }> => req("/deals", { method: "POST" }),
  addSource: (id: string, raw_text: string, conditions: Condition[]) =>
    req(`/deals/${id}/sources`, {
      method: "POST",
      body: JSON.stringify({ kind: "text", raw_text, conditions }),
    }),
  addReply: (id: string, raw_text: string, conditions: Condition[]) =>
    req(`/deals/${id}/owner_reply`, {
      method: "POST",
      body: JSON.stringify({ kind: "owner_reply", raw_text, conditions }),
    }),
  registry: (id: string): Promise<{ id: string; rows: Row[] }> =>
    req(`/deals/${id}/registry`),
};

export const TERMS = [
  "rent_amount", "deposit", "term", "utilities", "pets",
  "prepayment", "repairs", "owner_access", "termination", "deposit_return",
];

export const STATUS_META: Record<Row["status"], { icon: string; word: string; cls: string }> = {
  unknown: { icon: "❓", word: "Не указано", cls: "bg-gray-100 text-gray-800" },
  single: { icon: "🟡", word: "Один источник", cls: "bg-yellow-100 text-yellow-900" },
  match: { icon: "✅", word: "Совпадает", cls: "bg-green-100 text-green-900" },
  conflict: { icon: "⚠️", word: "Противоречие", cls: "bg-red-100 text-red-900" },
};
