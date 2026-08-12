import {
  AuiIf,
  ComposerPrimitive,
  MessagePrimitive,
  ThreadPrimitive,
  useAuiState,
} from "@assistant-ui/react";
import type { KeyboardEvent } from "react";

function UserMessage() {
  return (
    <MessagePrimitive.Root className="message message-user">
      <MessagePrimitive.Content />
    </MessagePrimitive.Root>
  );
}

function AssistantMessage() {
  return (
    <MessagePrimitive.Root className="message message-assistant">
      <MessagePrimitive.Content />
    </MessagePrimitive.Root>
  );
}

function Composer() {
  const text = useAuiState((s) => s.composer.text);
  const isRunning = useAuiState((s) => s.thread.isRunning);
  const canSend = text.trim().length > 0 && !isRunning;

  const handleKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && !event.shiftKey && text.trim().length === 0) {
      event.preventDefault();
    }
  };

  return (
    <ComposerPrimitive.Root className="composer">
      <ComposerPrimitive.Input
        className="composer-input"
        placeholder="輸入訊息…"
        autoFocus
        onKeyDown={handleKeyDown}
      />
      {/* FR-014: no Stop/Cancel — send only, disabled while running or empty */}
      <ComposerPrimitive.Send className="composer-send" disabled={!canSend}>
        傳送
      </ComposerPrimitive.Send>
    </ComposerPrimitive.Root>
  );
}

export function Thread() {
  return (
    <ThreadPrimitive.Root className="thread">
      <ThreadPrimitive.Viewport className="thread-viewport">
        <AuiIf condition={(s) => s.thread.isEmpty}>
          <div className="thread-empty">
            <p>開始對話 — 請用繁體中文提問。</p>
          </div>
        </AuiIf>

        <ThreadPrimitive.Messages
          components={{
            UserMessage,
            AssistantMessage,
          }}
        />

        <ThreadPrimitive.ViewportFooter className="thread-footer">
          <Composer />
        </ThreadPrimitive.ViewportFooter>
      </ThreadPrimitive.Viewport>
    </ThreadPrimitive.Root>
  );
}
