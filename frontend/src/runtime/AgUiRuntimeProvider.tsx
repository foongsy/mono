import { AssistantRuntimeProvider } from "@assistant-ui/react";
import { useAgUiRuntime } from "@assistant-ui/react-ag-ui";
import { useCallback, useMemo, useState, type ReactNode } from "react";

import { getAgUiUrl } from "../lib/env";
import { TrimmingHttpAgent } from "./trimming-http-agent";

type AgUiRuntimeProviderProps = {
  children: ReactNode;
};

export function AgUiRuntimeProvider({ children }: AgUiRuntimeProviderProps) {
  const [lastError, setLastError] = useState<string | null>(null);

  const agent = useMemo(
    () =>
      new TrimmingHttpAgent({
        url: getAgUiUrl(),
        headers: { Accept: "text/event-stream" },
      }),
    [],
  );

  const onError = useCallback((error: Error) => {
    setLastError(error.message || "Agent run failed");
  }, []);

  const runtime = useAgUiRuntime({
    agent,
    showThinking: false,
    onError,
  });

  return (
    <AssistantRuntimeProvider runtime={runtime}>
      {lastError ? (
        <div className="runtime-error" role="alert">
          {lastError}
        </div>
      ) : null}
      {children}
    </AssistantRuntimeProvider>
  );
}
