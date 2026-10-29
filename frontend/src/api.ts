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

async function req(path: string, init?: RequestInit, timeoutMs = 30000) {
  const ctrl = new AbortController();
  const t = setTimeout(() => ctrl.abort(), timeoutMs);
  try {
    const r = await fetch(BASE + path, {
      ...init,
      signal: ctrl.signal,
      headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
    });
    if (!r.ok) {
      const text = await r.text();
      throw new Error(`API ${r.status}: ${text}`);
    }
    return r.json();
  } catch (e) {
    if (e instanceof DOMException && e.name === "AbortError") {
      throw new Error("Сервер не отвечает (таймаут). Проверьте backend и введите условия вручную.");
    }
    throw e;
  } finally {
    clearTimeout(t);
  }
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
  deleteDeal: (id: string): Promise<{ ok: boolean }> =>
    req(`/deals/${id}`, { method: "DELETE" }),
};

export const TERMS = [
  "rent_amount", "deposit", "term", "utilities", "pets",
  "prepayment", "repairs", "owner_access", "termination", "deposit_return",
];

export const TERM_RU: Record<string, string> = {
  rent_amount: "Аренда",
  deposit: "Залог",
  term: "Срок",
  utilities: "Коммуналка",
  pets: "Животные",
  prepayment: "Предоплата",
  repairs: "Ремонт",
  owner_access: "Доступ хозяина",
  termination: "Расторжение",
  deposit_return: "Возврат залога",
};

export const STATUS_META: Record<Row["status"], { icon: string; word: string; cls: string }> = {
  unknown: { icon: "❓", word: "Не указано", cls: "bg-gray-100 text-gray-800" },
  single: { icon: "🟡", word: "Один источник", cls: "bg-yellow-100 text-yellow-800" },
  match: { icon: "✅", word: "Совпадает", cls: "bg-green-100 text-green-800" },
  conflict: { icon: "⚠️", word: "Противоречие", cls: "bg-red-100 text-red-800" },
};
