import { useEffect, useState } from "react";
import { api, STATUS_META, TERMS, TERM_RU, type Condition, type Row } from "./api";

const DISCLAIMER =
  "Приложение помогает зафиксировать условия и показывает, что нужно уточнить. Это не юридическая консультация.";
const LS_KEY = "kelishim:dealId";

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

function parseValue(text: string): unknown {
  const t = text.trim();
  if (t === "" || t === "—" || t.toLowerCase() === "null") return null;
  const n = Number(t.replace(/\s/g, "").replace(",", "."));
  return Number.isFinite(n) && t.match(/^[\d\s.,]+$/) ? n : t;
}

function ConditionBuilder(props: {
  raw: string;
  setRaw: (v: string) => void;
  conds: Condition[];
  setConds: (v: Condition[]) => void;
  rawLabel: string;
  rawPlaceholder: string;
}) {
  const { raw, setRaw, conds, setConds, rawLabel, rawPlaceholder } = props;
  const [term, setTerm] = useState(TERMS[0]);
  const [val, setVal] = useState("");
  const [cur, setCur] = useState("");
  const [hedged, setHedged] = useState(false);
  const [busy, setBusy] = useState<"" | "extract" | "media">("");
  const [autoError, setAutoError] = useState("");

  async function autoExtract() {
    if (!raw.trim() || busy) return;
    setBusy("extract");
    setAutoError("");
    try {
      const got = await api.extract(raw);
      setConds([...conds, ...got]);
    } catch (e) {
      setAutoError(e instanceof Error ? e.message : "Не извлеклось");
    } finally {
      setBusy("");
    }
  }

  async function fromFile(f: File | undefined, kind: "photo" | "audio") {
    if (!f || busy) return;
    setBusy("media");
    setAutoError("");
    try {
      const text = kind === "photo" ? await api.ocr(f) : await api.transcribe(f);
      setRaw(text);
    } catch (e) {
      setAutoError(e instanceof Error ? e.message : "Не распозналось");
    } finally {
      setBusy("");
    }
  }

  function add() {
    if (!raw.trim()) return;
    const value = parseValue(val);
    setConds([
      ...conds,
      {
        term,
        value,
        currency: cur === "" ? null : cur,
        quote: raw.trim(),
        confidence: 1,
        hedged,
      },
    ]);
    setVal("");
    setCur("");
    setHedged(false);
  }

  return (
    <div className="flex flex-col gap-2 rounded-xl border p-3">
      <label className="text-sm font-semibold">{rawLabel}</label>
      <textarea
        value={raw}
        onChange={(e) => setRaw(e.target.value)}
        rows={3}
        className="w-full rounded-xl border p-3 text-base"
        placeholder={rawPlaceholder}
      />
      <div className="grid grid-cols-2 gap-2">
        <label className="flex min-h-[44px] cursor-pointer items-center justify-center gap-2 rounded-xl bg-gray-100 text-sm font-semibold">
          📷 Фото
          <input
            type="file"
            accept="image/*"
            className="hidden"
            aria-label="Загрузить фото текста"
            disabled={busy !== ""}
            onChange={(e) => { fromFile(e.target.files?.[0], "photo"); e.target.value = ""; }}
          />
        </label>
        <label className="flex min-h-[44px] cursor-pointer items-center justify-center gap-2 rounded-xl bg-gray-100 text-sm font-semibold">
          🎤 Аудио
          <input
            type="file"
            accept="audio/*"
            className="hidden"
            aria-label="Загрузить аудио"
            disabled={busy !== ""}
            onChange={(e) => { fromFile(e.target.files?.[0], "audio"); e.target.value = ""; }}
          />
        </label>
      </div>
      {busy === "media" && <p className="text-sm text-gray-500">Распознаю… текст подставится ниже, проверьте его.</p>}
      <Btn onClick={autoExtract} disabled={!raw.trim() || busy !== ""} className="bg-gray-800 text-white">
        {busy === "extract" ? "Извлекаю…" : "✨ Извлечь условия автоматически"}
      </Btn>
      {autoError !== "" && (
        <p className="rounded-xl bg-red-50 p-3 text-sm text-red-800">
          Автоматически не получилось ({autoError}). Введите условия вручную ниже — текст сохранён.
        </p>
      )}
      <div className="grid grid-cols-2 gap-2">
        <label className="flex flex-col gap-1 text-sm">
          Условие
          <select value={term} onChange={(e) => setTerm(e.target.value)} className="min-h-[44px] rounded-xl border p-2 text-base">
            {TERMS.map((t) => (
              <option key={t} value={t}>{TERM_RU[t] ?? t}</option>
            ))}
          </select>
        </label>
        <label className="flex flex-col gap-1 text-sm">
          Значение
          <input value={val} onChange={(e) => setVal(e.target.value)} placeholder="30000 / да / год" className="min-h-[44px] rounded-xl border p-2 text-base" />
        </label>
      </div>
      <div className="grid grid-cols-2 gap-2">
        <label className="flex flex-col gap-1 text-sm">
          Валюта
          <select value={cur} onChange={(e) => setCur(e.target.value)} className="min-h-[44px] rounded-xl border p-2 text-base">
            <option value="">—</option>
            <option value="KGS">KGS (сом)</option>
            <option value="USD">USD</option>
          </select>
        </label>
        <label className="flex min-h-[44px] items-center gap-2 text-sm">
          <input type="checkbox" checked={hedged} onChange={(e) => setHedged(e.target.checked)} className="h-5 w-5" />
          Неуверенно (hedged)
        </label>
      </div>
      <Btn onClick={add} className="bg-gray-200 text-black">+ Добавить условие ({conds.length})</Btn>
      {conds.length > 0 && (
        <ul className="flex flex-col gap-1 text-sm">
          {conds.map((c, i) => (
            <li key={i} className="flex items-center justify-between gap-2 rounded-lg bg-gray-50 p-2">
              <span><b>{TERM_RU[c.term] ?? c.term}:</b> {String(c.value ?? "—")} {c.currency ?? ""}{c.hedged ? " (неуверенно)" : ""}</span>
              <button
                aria-label={`Убрать условие ${i + 1}`}
                onClick={() => setConds(conds.filter((_, j) => j !== i))}
                className="min-h-[44px] min-w-[44px] rounded-xl bg-gray-200 font-bold"
              >×</button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default function App() {
  const [dealId, setDealId] = useState<string | null>(null);
  const [rows, setRows] = useState<Row[]>([]);
  const [phase, setPhase] = useState<"idle" | "loading" | "error" | "ready">("idle");
  const [error, setError] = useState("");
  const [tab, setTab] = useState<"registry" | "ask" | "reply" | "result">("registry");
  const [rawSrc, setRawSrc] = useState("");
  const [condsSrc, setCondsSrc] = useState<Condition[]>([]);
  const [rawReply, setRawReply] = useState("");
  const [condsReply, setCondsReply] = useState<Condition[]>([]);
  const [msg, setMsg] = useState("");
  const [confirmed, setConfirmed] = useState(false);
  const [confirmedDone, setConfirmedDone] = useState(false);
  const [isDemo, setIsDemo] = useState(false);

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

  useEffect(() => {
    const saved = localStorage.getItem(LS_KEY);
    if (saved) {
      setDealId(saved);
      load(saved).catch(() => {
        localStorage.removeItem(LS_KEY);
        setDealId(null);
      });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function remember(id: string, demo: boolean) {
    setDealId(id);
    setIsDemo(demo);
    localStorage.setItem(LS_KEY, id);
  }

  function forget() {
    setDealId(null);
    setRows([]);
    setMsg("");
    setConfirmed(false);
    setConfirmedDone(false);
    setRawSrc("");
    setRawReply("");
    setCondsSrc([]);
    setCondsReply([]);
    setIsDemo(false);
    setPhase("idle");
    localStorage.removeItem(LS_KEY);
  }

  async function newDeal() {
    setPhase("loading");
    setError("");
    try {
      const d = await api.createDeal();
      remember(d.id, false);
      await load(d.id);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Нет связи с сервером.");
      setPhase("error");
    }
  }

  async function demoDeal() {
    setPhase("loading");
    setError("");
    try {
      const d = await api.createDeal();
      remember(d.id, true);
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
    if (!dealId || !rawSrc.trim()) return;
    setPhase("loading");
    try {
      await api.addSource(dealId, rawSrc, condsSrc);
      setRawSrc("");
      setCondsSrc([]);
      await load(dealId);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Не сохранено");
      setPhase("error");
    }
  }

  async function sendReply() {
    if (!dealId || !rawReply.trim()) return;
    setPhase("loading");
    try {
      await api.addReply(dealId, rawReply, condsReply);
      setRawReply("");
      setCondsReply([]);
      setConfirmed(false);
      setConfirmedDone(false);
      await load(dealId);
      setTab("registry");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Ответ не сохранён");
      setPhase("error");
    }
  }

  async function deleteDeal() {
    if (!dealId) return;
    if (!window.confirm("Удалить сделку и все её данные?")) return;
    try {
      await api.deleteDeal(dealId);
    } catch {
      /* backend мог уже потерять её — чистим локально в любом случае */
    }
    forget();
  }

  function fillTemplate() {
    setMsg(needAsk.map((r) => `• Уточните: ${TERM_RU[r.term] ?? r.term} (${STATUS_META[r.status].word.toLowerCase()})?`).join("\n"));
    setConfirmed(false);
    setConfirmedDone(false);
  }

  const needAsk = rows.filter((r) => r.status === "conflict" || r.status === "unknown");
  const counts = {
    match: rows.filter((r) => r.status === "match").length,
    conflict: rows.filter((r) => r.status === "conflict").length,
    single: rows.filter((r) => r.status === "single").length,
    unknown: rows.filter((r) => r.status === "unknown").length,
  };

  return (
    <div className="mx-auto flex min-h-dvh w-full max-w-md flex-col bg-white text-gray-900">
      <header className="sticky top-0 z-10 border-b bg-white/95 px-4 py-3 backdrop-blur">
        <div className="flex items-center justify-between gap-2">
          <h1 className="text-lg font-bold">Kelishim — реестр аренды</h1>
          {dealId && (
            <button onClick={deleteDeal} aria-label="Удалить сделку" className="min-h-[44px] min-w-[44px] rounded-xl bg-gray-100 text-xl">🗑</button>
          )}
        </div>
        {dealId && <p className="text-xs text-gray-500">Сделка {dealId}{isDemo ? " · сохранённый результат" : ""}</p>}
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
            <p className="text-sm text-gray-600">Не получилось автоматически — введите условия вручную на вкладке «Ответ».</p>
          </div>
        )}

        {phase === "ready" && dealId && (
          <div className="flex flex-col gap-4">
            <nav className="grid grid-cols-4 gap-1" aria-label="Разделы">
              {([["registry", "Реестр"], ["ask", "Вопросы"], ["reply", "Ответ"], ["result", "Итог"]] as const).map(([t, label]) => (
                <button
                  key={t}
                  onClick={() => setTab(t)}
                  aria-pressed={tab === t}
                  className={`min-h-[44px] rounded-xl text-sm font-semibold ${tab === t ? "bg-black text-white" : "bg-gray-100"}`}
                >
                  {label}
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
                        <span className="text-sm font-semibold">{TERM_RU[r.term] ?? r.term}</span>
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
                          <b>{TERM_RU[r.term] ?? r.term}</b> — {STATUS_META[r.status].icon} {STATUS_META[r.status].word}
                        </li>
                      ))}
                    </ul>
                    <label className="text-sm font-semibold" htmlFor="msg">Сообщение хозяину (ничего не отправляется автоматически)</label>
                    <textarea
                      id="msg"
                      value={msg}
                      onChange={(e) => { setMsg(e.target.value); setConfirmed(false); setConfirmedDone(false); }}
                      rows={5}
                      className="w-full rounded-xl border p-3 text-base"
                      placeholder="Нажмите «Вставить шаблон» или напишите свой текст"
                    />
                    <Btn onClick={fillTemplate} className="bg-gray-200 text-black">Вставить шаблон</Btn>
                    <label className="flex min-h-[44px] items-center gap-2 text-sm">
                      <input type="checkbox" checked={confirmed} onChange={(e) => { setConfirmed(e.target.checked); setConfirmedDone(false); }} className="h-5 w-5" />
                      Я проверил(а) текст, сообщение готово
                    </label>
                    <Btn disabled={!confirmed || !msg.trim()} onClick={() => setConfirmedDone(true)}>
                      Подтвердить готовность
                    </Btn>
                    {confirmedDone && <p className="rounded-xl bg-green-50 p-3 text-sm">Готово к отправке вручную. Приложение ничего не отправляло.</p>}
                  </>
                )}
              </section>
            )}

            {tab === "reply" && (
              <section aria-label="Ответ хозяина и источники" className="flex flex-col gap-3">
                <ConditionBuilder
                  raw={rawReply} setRaw={setRawReply} conds={condsReply} setConds={setCondsReply}
                  rawLabel="Ответ хозяина (текст + условия из него)"
                  rawPlaceholder="Например: итого залог 30000 сом"
                />
                <Btn onClick={sendReply} disabled={!rawReply.trim()}>Добавить ответ и пересчитать</Btn>
                <ConditionBuilder
                  raw={rawSrc} setRaw={setRawSrc} conds={condsSrc} setConds={setCondsSrc}
                  rawLabel="Новый источник (текст + условия из него)"
                  rawPlaceholder="Вставьте текст объявления или переписки"
                />
                <Btn onClick={addManual} disabled={!rawSrc.trim()} className="bg-gray-200 text-black">Сохранить источник</Btn>
              </section>
            )}

            {tab === "result" && (
              <section aria-label="Итог сделки" className="flex flex-col gap-3">
                {isDemo && <p className="rounded-xl bg-yellow-50 p-3 text-sm">Сохранённый результат (demo-пример).</p>}
                <div className="grid grid-cols-2 gap-2 text-center text-sm">
                  <p className="rounded-xl bg-green-100 p-3">✅ Совпадает: <b>{counts.match}</b></p>
                  <p className="rounded-xl bg-red-100 p-3">⚠️ Противоречие: <b>{counts.conflict}</b></p>
                  <p className="rounded-xl bg-yellow-100 p-3">🟡 Один источник: <b>{counts.single}</b></p>
                  <p className="rounded-xl bg-gray-100 p-3">❓ Не указано: <b>{counts.unknown}</b></p>
                </div>
                {needAsk.length === 0
                  ? <p className="rounded-xl bg-green-50 p-3 text-sm">Все условия зафиксированы одинаково. Осталось подтвердить сообщение хозяину на вкладке «Вопросы».</p>
                  : <div className="rounded-xl border p-3 text-sm">
                      <p className="font-semibold">Нужно уточнить ({needAsk.length}):</p>
                      <ul className="mt-1 list-disc pl-5">
                        {needAsk.map((r) => (
                          <li key={r.term}>{TERM_RU[r.term] ?? r.term} — {STATUS_META[r.status].word.toLowerCase()}</li>
                        ))}
                      </ul>
                    </div>}
              </section>
            )}
          </div>
        )}
      </main>

      <footer className="fixed inset-x-0 bottom-0 border-b bg-white/95 backdrop-blur">
        <p className="mx-auto max-w-md px-4 py-3 text-xs text-gray-600" style={{ paddingBottom: "env(safe-area-inset-bottom)" }}>
          {DISCLAIMER}
        </p>
      </footer>
    </div>
  );
}
