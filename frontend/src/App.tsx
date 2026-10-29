import { useState } from "react";
import { api, STATUS_META, TERMS, type Condition, type Row } from "./api";

const DISCLAIMER =
  "Приложение помогает зафиксировать условия и показывает, что нужно уточнить. Это не юридическая консультация.";

function Btn(props: React.ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button
      {...props}
      className={
        "min-h-[44px] w-full rounded-xl px-4 py-3 text-base font-semibold active:scale-[0.99] disabled:opacity-40 " +
        (props.className ?? "bg-black text-white")
      }
    />
  );
}

export default function App() {
  const [dealId, setDealId] = useState<string | null>(null);
  const [rows, setRows] = useState<Row[]>([]);
  const [phase, setPhase] = useState<"idle" | "loading" | "error" | "ready">("idle");
  const [error, setError] = useState("");
  const [tab, setTab] = useState<"registry" | "ask" | "reply">("registry");
  const [raw, setRaw] = useState("");
  const [msg, setMsg] = useState("");
  const [confirmed, setConfirmed] = useState(false);
  const [confirmedDone, setConfirmedDone] = useState(false);

  async function load(id: string) {
    setPhase("loading");
    try {
      const reg = await api.registry(id);
      setRows(reg.rows);
      setPhase("ready");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Ошибка загрузки");
      setPhase("error");
    }
  }

  async function newDeal() {
    setPhase("loading");
    setError("");
    try {
      const d = await api.createDeal();
      setDealId(d.id);
      await load(d.id);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Нет связи с сервером. Проверьте, что backend запущен.");
      setPhase("error");
    }
  }

  async function demoDeal() {
    setPhase("loading");
    setError("");
    try {
      const d = await api.createDeal();
      setDealId(d.id);
      await api.addSource(d.id, "Сдаю 1-комн на год. Аренда 30000 сом, залог 30000.", [
        { term: "rent_amount", value: 30000, currency: "KGS", quote: "Аренда 30000 сом", confidence: 0.9 },
        { term: "deposit", value: 30000, currency: "KGS", quote: "залог 30000", confidence: 0.9 },
        { term: "term", value: "на год", quote: "на год", confidence: 0.85 },
      ]);
      await api.addSource(d.id, "Аренда 30000 сом в месяц, залог 35000 сом.", [
        { term: "rent_amount", value: 30000, currency: "KGS", quote: "Аренда 30000 сом", confidence: 0.85 },
        { term: "deposit", value: 35000, currency: "KGS", quote: "залог 35000 сом", confidence: 0.8 },
      ]);
      await load(d.id);
      setTab("registry");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Demo не загрузилось");
      setPhase("error");
    }
  }

  async function addManual() {
    if (!dealId || !raw.trim()) return;
    setPhase("loading");
    try {
      const conds: Condition[] = [
        { term: "rent_amount", value: null, quote: null, confidence: 1 },
      ];
      void conds;
      await api.addSource(dealId, raw, []);
      setRaw("");
      await load(dealId);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Не сохранено");
      setPhase("error");
    }
  }

  async function sendReply() {
    if (!dealId || !raw.trim()) return;
    setPhase("loading");
    try {
      await api.addReply(dealId, raw, []);
      setRaw("");
      await load(dealId);
      setTab("registry");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Ответ не сохранён");
      setPhase("error");
    }
  }

  const needAsk = rows.filter((r) => r.status === "conflict" || r.status === "unknown");

  return (
    <div className="mx-auto flex min-h-dvh w-full max-w-md flex-col bg-white text-gray-900">
      <header className="sticky top-0 z-10 border-b bg-white/95 px-4 py-3 backdrop-blur">
        <h1 className="text-lg font-bold">Kelishim — реестр аренды</h1>
        {dealId && <p className="text-xs text-gray-500">Сделка {dealId}</p>}
      </header>

      <main className="flex-1 overflow-x-hidden px-4 py-4 pb-28">
        {!dealId && phase !== "loading" && (
          <div className="flex flex-col gap-3">
            <p className="text-base">Зафиксируйте обещания хозяина: источники → сравнение → вопросы → ответ → итог.</p>
            <Btn onClick={demoDeal}>Попробовать на примере</Btn>
            <Btn onClick={newDeal} className="bg-gray-200 text-black">Новая сделка</Btn>
            {phase === "error" && <p className="rounded-xl bg-red-50 p-3 text-sm text-red-800">{error}</p>}
          </div>
        )}

        {phase === "loading" && <p className="py-10 text-center text-gray-500">Загрузка…</p>}

        {phase === "error" && dealId && (
          <div className="flex flex-col gap-3">
            <p className="rounded-xl bg-red-50 p-3 text-sm text-red-800">{error}</p>
            <Btn onClick={() => load(dealId)}>Повторить</Btn>
            <p className="text-sm text-gray-600">Не получилось автоматически — введите условия вручную ниже.</p>
          </div>
        )}

        {phase === "ready" && dealId && (
          <div className="flex flex-col gap-4">
            <nav className="grid grid-cols-3 gap-2" aria-label="Разделы">
              {(["registry", "ask", "reply"] as const).map((t) => (
                <button
                  key={t}
                  onClick={() => setTab(t)}
                  aria-pressed={tab === t}
                  className={`min-h-[44px] rounded-xl text-sm font-semibold ${tab === t ? "bg-black text-white" : "bg-gray-100"}`}
                >
                  {t === "registry" ? "Реестр" : t === "ask" ? "Вопросы" : "Ответ"}
                </button>
              ))}
            </nav>

            {tab === "registry" && (
              <section aria-label="Реестр условий" className="flex flex-col gap-2">
                {rows.map((r) => {
                  const m = STATUS_META[r.status];
                  return (
                    <details key={r.term} className="rounded-xl border p-3">
                      <summary className="flex min-h-[44px] cursor-pointer items-center justify-between gap-2">
                        <span className="font-mono text-sm">{r.term}</span>
                        <span className={`rounded-full px-2 py-1 text-xs font-bold ${m.cls}`}>
                          {m.icon} {m.word}
                        </span>
                      </summary>
                      {r.entries.length === 0 && <p className="mt-2 text-sm text-gray-500">Пусто — условие не упомянуто ни в одном источнике.</p>}
                      {r.entries.map((e, i) => (
                        <div key={i} className="mt-2 rounded-lg bg-gray-50 p-2 text-sm">
                          <p><b>Значение:</b> {e.value === null || e.value === undefined ? "—" : String(e.value)} {e.currency ?? ""}</p>
                          {e.quote && <p className="mt-1 border-l-2 pl-2 italic">«{e.quote}»</p>}
                          {(e.hedged || (e.confidence ?? 1) < 0.6) && (
                            <p className="mt-1 font-semibold text-yellow-800">Требует ручной проверки (hedged / низкая уверенность)</p>
                          )}
                        </div>
                      ))}
                      {r.needs_manual_check && <p className="mt-1 text-xs font-semibold">⚠ проверьте вручную</p>}
                    </details>
                  );
                })}
              </section>
            )}

            {tab === "ask" && (
              <section aria-label="Вопросы хозяину" className="flex flex-col gap-3">
                {needAsk.length === 0 && <p className="rounded-xl bg-green-50 p-3 text-sm">Противоречий и пробелов нет — вопросы не нужны.</p>}
                {needAsk.length > 0 && (
                  <>
                    <p className="text-sm text-gray-600">Вопросы только по статусам «Противоречие» и «Не указано»:</p>
                    <ul className="flex flex-col gap-2">
                      {needAsk.map((r) => (
                        <li key={r.term} className="rounded-xl border p-3 text-sm">
                          <b className="font-mono">{r.term}</b> — {STATUS_META[r.status].icon} {STATUS_META[r.status].word}
                        </li>
                      ))}
                    </ul>
                    <label className="text-sm font-semibold" htmlFor="msg">Сообщение хозяину (ничего не отправляется автоматически)</label>
                    <textarea
                      id="msg"
                      value={msg || needAsk.map((r) => `• Уточните: ${r.term}?`).join("\n")}
                      onChange={(e) => setMsg(e.target.value)}
                      rows={5}
                      className="w-full rounded-xl border p-3 text-base"
                    />
                    <label className="flex min-h-[44px] items-center gap-2 text-sm">
                      <input type="checkbox" checked={confirmed} onChange={(e) => setConfirmed(e.target.checked)} className="h-5 w-5" />
                      Я проверил(а) текст, сообщение готово
                    </label>
                    <Btn disabled={!confirmed} onClick={() => setConfirmedDone(true)}>
                      Подтвердить готовность
                    </Btn>
                    {confirmedDone && <p className="rounded-xl bg-green-50 p-3 text-sm">Готово к отправке вручную. Приложение ничего не отправляло.</p>}
                  </>
                )}
              </section>
            )}

            {tab === "reply" && (
              <section aria-label="Ответ хозяина" className="flex flex-col gap-3">
                <label className="text-sm font-semibold" htmlFor="reply">Вставьте ответ хозяина текстом</label>
                <textarea id="reply" value={raw} onChange={(e) => setRaw(e.target.value)} rows={4} className="w-full rounded-xl border p-3 text-base" placeholder="Например: итого залог 30000 сом" />
                <Btn onClick={sendReply}>Добавить ответ и пересчитать</Btn>
                <div className="flex flex-col gap-2">
                  <label className="text-sm font-semibold" htmlFor="src">Или новый источник (текст сохранится как есть)</label>
                  <textarea id="src" value={raw} onChange={(e) => setRaw(e.target.value)} rows={3} className="w-full rounded-xl border p-3 text-base" placeholder="Вставьте текст объявления или переписки" />
                  <Btn onClick={addManual} className="bg-gray-200 text-black">Сохранить источник</Btn>
                </div>
                <p className="text-xs text-gray-500">Термы: {TERMS.join(", ")}</p>
              </section>
            )}
          </div>
        )}
      </main>

      <footer className="fixed inset-x-0 bottom-0 border-t bg-white/95 backdrop-blur">
        <p className="mx-auto max-w-md px-4 py-3 text-xs text-gray-600" style={{ paddingBottom: "env(safe-area-inset-bottom)" }}>
          {DISCLAIMER}
        </p>
      </footer>
    </div>
  );
}
