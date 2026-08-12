import type { Message } from "@ag-ui/client";

/**
 * Keep the last N message turns from the transcript (FR-012, N=10).
 * Each AG-UI message counts as one turn for v1.
 */
export function sliceLastNTurns<T extends Message>(messages: T[], n: number): T[] {
  if (n <= 0) return [];
  if (messages.length <= n) return [...messages];
  return messages.slice(messages.length - n);
}
