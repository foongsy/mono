#!/usr/bin/env python3
"""One-off AG-UI chat smoke test against local backend."""

from __future__ import annotations

import json
import sys
import uuid

import httpx

BASE = "http://localhost:7777"
THREAD_ID = str(uuid.uuid4())
RUN_ID = str(uuid.uuid4())

payload = {
    "threadId": THREAD_ID,
    "runId": RUN_ID,
    "state": None,
    "messages": [
        {
            "id": str(uuid.uuid4()),
            "role": "user",
            "content": "請用一句話介紹你自己。",
        }
    ],
    "tools": [],
    "context": [],
    "forwardedProps": {},
}


def main() -> int:
    print("=== GET /status ===")
    status = httpx.get(f"{BASE}/status", timeout=10)
    print(f"HTTP {status.status_code}: {status.text}")

    print("\n=== POST /agui (streaming) ===")
    text_chunks: list[str] = []
    events: list[str] = []

    with httpx.stream(
        "POST",
        f"{BASE}/agui",
        json=payload,
        headers={"Accept": "text/event-stream"},
        timeout=60,
    ) as response:
        print(f"HTTP {response.status_code}")
        if response.status_code != 200:
            print(response.read().decode())
            return 1

        for line in response.iter_lines():
            if not line or not line.startswith("data: "):
                continue
            data = line[6:]
            if data == "[DONE]":
                break
            try:
                event = json.loads(data)
            except json.JSONDecodeError:
                continue
            event_type = event.get("type")
            events.append(str(event_type))
            if event_type in ("TEXT_MESSAGE_CONTENT", "TEXT_MESSAGE_CHUNK"):
                delta = event.get("delta") or event.get("content") or ""
                if isinstance(delta, str) and delta:
                    text_chunks.append(delta)
                    print(delta, end="", flush=True)

    print("\n")
    assistant_text = "".join(text_chunks)
    print(f"\nEvent types seen: {sorted(set(events))}")
    print(f"Assistant text length: {len(assistant_text)} chars")
    if assistant_text:
        print(f"Preview: {assistant_text[:200]}")
        return 0
    print("FAIL: no assistant text received")
    return 1


if __name__ == "__main__":
    sys.exit(main())
