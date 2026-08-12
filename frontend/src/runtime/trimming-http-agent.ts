import { HttpAgent, type HttpAgentConfig } from "@ag-ui/client";

import { sliceLastNTurns } from "./trim-context";

const DEFAULT_MAX_TURNS = 10;

/**
 * HttpAgent that trims RunAgentInput.messages to the last N turns before send.
 */
export class TrimmingHttpAgent extends HttpAgent {
  private readonly maxTurns: number;

  constructor(config: HttpAgentConfig, maxTurns = DEFAULT_MAX_TURNS) {
    super(config);
    this.maxTurns = maxTurns;
    this.use((input, next) =>
      next.run({
        ...input,
        messages: sliceLastNTurns(input.messages, this.maxTurns),
      }),
    );
  }
}
