import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import App from "./App";
import { TERMS } from "./api";

const DISCLAIMER =
  "Приложение помогает зафиксировать условия и показывает, что нужно уточнить. Это не юридическая консультация.";

function registryPayload() {
  return {
    id: "d1",
    rows: TERMS.map((term) => ({
      term,
      status: "unknown",
      entries: [],
      needs_manual_check: false,
    })),
  };
}

function mockApi() {
  return vi.fn(async (url: string, init?: RequestInit) => {
    const method = init?.method ?? "GET";
    let body: unknown = {};
    if (url.endsWith("/deals") && method === "POST") body = { id: "d1" };
    else if (url.endsWith("/registry")) body = registryPayload();
    else if (url.includes("/extract")) body = { conditions: [] };
    else if (url.includes("/transcribe") || url.includes("/ocr")) body = { text: "аренда 30000 сом" };
    return { ok: true, status: 200, json: async () => body, text: async () => "" } as Response;
  });
}

beforeEach(() => {
  localStorage.clear();
  vi.stubGlobal("fetch", mockApi());
});

describe("App shell", () => {
  it("shows disclaimer and start actions without a deal", () => {
    render(<App />);
    expect(screen.getByText(DISCLAIMER)).toBeInTheDocument();
    expect(screen.getByText("Новая сделка")).toBeInTheDocument();
    expect(screen.getByText("Попробовать на примере")).toBeInTheDocument();
  });

  it("demo deal opens four tabs incl. result, reply tab has auto-extract and media inputs", async () => {
    const user = userEvent.setup();
    render(<App />);
    await user.click(screen.getByText("Попробовать на примере"));
    await waitFor(() => expect(screen.getByText("Итог")).toBeInTheDocument());
    expect(screen.getByText("Реестр")).toBeInTheDocument();
    expect(screen.getByText("Вопросы")).toBeInTheDocument();
    expect(screen.getByText("Ответ")).toBeInTheDocument();

    await user.click(screen.getByText("Ответ"));
    expect(screen.getAllByText("✨ Извлечь условия автоматически")).toHaveLength(2);
    expect(screen.getAllByLabelText("Загрузить фото текста")).toHaveLength(2);
    expect(screen.getAllByLabelText("Загрузить аудио")).toHaveLength(2);

    await user.click(screen.getByText("Итог"));
    expect(screen.getByText(/Нужно уточнить/)).toBeInTheDocument();
    expect(screen.getByText(DISCLAIMER)).toBeInTheDocument();
  });

  it("extract failure keeps text and tells to enter manually", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async (url: string) => {
        if (url.includes("/extract")) {
          return { ok: false, status: 503, text: async () => "нет ключа" } as Response;
        }
        if (url.endsWith("/deals")) return { ok: true, status: 200, json: async () => ({ id: "d1" }) } as Response;
        return { ok: true, status: 200, json: async () => registryPayload() } as Response;
      })
    );
    const user = userEvent.setup();
    render(<App />);
    await user.click(screen.getByText("Попробовать на примере"));
    await waitFor(() => expect(screen.getByText("Ответ")).toBeInTheDocument());
    await user.click(screen.getByText("Ответ"));
    await user.type(screen.getAllByRole("textbox")[0], "аренда 30000 сом");
    await user.click(screen.getAllByText("✨ Извлечь условия автоматически")[0]);
    await waitFor(() =>
      expect(screen.getByText(/Автоматически не получилось/)).toBeInTheDocument()
    );
  });
});
