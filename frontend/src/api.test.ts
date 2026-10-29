import { describe, expect, it } from "vitest";
import { STATUS_META, TERM_RU, TERMS } from "./api";

describe("contract: 10 frozen terms", () => {
  it("terms list matches spec schema", () => {
    expect(TERMS).toEqual([
      "rent_amount", "deposit", "term", "utilities", "pets",
      "prepayment", "repairs", "owner_access", "termination", "deposit_return",
    ]);
  });

  it("every term has a Russian label", () => {
    for (const t of TERMS) {
      expect(TERM_RU[t], t).toMatch(/[^a-z_]/);
    }
  });
});

describe("contract: four statuses", () => {
  it("covers unknown/single/match/conflict with distinct words", () => {
    const keys = Object.keys(STATUS_META).sort();
    expect(keys).toEqual(["conflict", "match", "single", "unknown"]);
    const words = new Set(Object.values(STATUS_META).map((m) => m.word));
    expect(words.size).toBe(4);
  });
});
