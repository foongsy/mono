import { describe, expect, it } from "vitest";

import { sliceLastNTurns } from "../src/runtime/trim-context";

type Msg = { id: string; role: "user" | "assistant"; content: string };

function makeMessages(count: number): Msg[] {
  return Array.from({ length: count }, (_, i) => ({
    id: `m-${i}`,
    role: i % 2 === 0 ? "user" : "assistant",
    content: `message ${i}`,
  }));
}

describe("sliceLastNTurns", () => {
  it("returns empty for empty input", () => {
    expect(sliceLastNTurns([], 10)).toEqual([]);
  });

  it("returns all messages when fewer than N", () => {
    const messages = makeMessages(4);
    expect(sliceLastNTurns(messages, 10)).toEqual(messages);
  });

  it("returns all messages when exactly N", () => {
    const messages = makeMessages(10);
    expect(sliceLastNTurns(messages, 10)).toEqual(messages);
  });

  it("returns last N when more than N", () => {
    const messages = makeMessages(12);
    const result = sliceLastNTurns(messages, 10);
    expect(result).toHaveLength(10);
    expect(result[0]).toEqual(messages[2]);
    expect(result[9]).toEqual(messages[11]);
  });

  it("returns empty when N is zero", () => {
    expect(sliceLastNTurns(makeMessages(5), 0)).toEqual([]);
  });
});
