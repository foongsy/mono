import type { Message } from "@ag-ui/client";
import { describe, expect, it, vi } from "vitest";

import { TrimmingHttpAgent } from "../src/runtime/trimming-http-agent";

function makeMessages(count: number): Message[] {
  return Array.from({ length: count }, (_, i) => ({
    id: `m-${i}`,
    role: i % 2 === 0 ? "user" : "assistant",
    content: `message ${i}`,
  })) as Message[];
}

function sseResponse(): Response {
  const body = 'data: {"type":"RUN_STARTED","threadId":"t1","runId":"r1"}\n\ndata: {"type":"RUN_FINISHED","threadId":"t1","runId":"r1"}\n\n';
  return new Response(body, {
    status: 200,
    headers: { "Content-Type": "text/event-stream" },
  });
}

describe("TrimmingHttpAgent", () => {
  it("sends only the last 10 messages from a 12-turn transcript", async () => {
    let capturedBody: { messages: Message[] } | undefined;

    const agent = new TrimmingHttpAgent({
      url: "http://testserver/agui",
      fetch: vi.fn(async (_url, init) => {
        capturedBody = JSON.parse(String(init?.body));
        return sseResponse();
      }),
    });

    agent.setMessages(makeMessages(12));
    await agent.runAgent({ runId: "run-test" });

    expect(capturedBody?.messages).toHaveLength(10);
    expect(capturedBody?.messages[0]?.id).toBe("m-2");
    expect(capturedBody?.messages[9]?.id).toBe("m-11");
  });
});
