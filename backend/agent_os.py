"""AgentOS + AG-UI backend for the agent chat app."""

from __future__ import annotations

import json
import logging
from typing import Any

from agno.agent import Agent
from agno.models.openai.like import OpenAILike
from agno.os import AgentOS
from agno.os.interfaces.agui import AGUI
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from config import Settings, get_settings

logger = logging.getLogger(__name__)

CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

TC_INSTRUCTIONS = """You are a helpful assistant in a Traditional Chinese chat app.
When the user writes in Traditional Chinese, reply in Traditional Chinese (繁體中文).
Keep answers concise and conversational unless the user asks for detail.
If the user writes in another language, you may reply in that language."""

# GET /status is provided by Agno AGUI and reports process readiness only.
# It does NOT validate AI_GATEWAY_API_KEY or call the LLM — see contracts/ag-ui-v1.md §1.


class AgUiRunLoggingMiddleware(BaseHTTPMiddleware):
    """Emit structured JSON logs for AG-UI runs (Principle VI)."""

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        if request.method == "POST" and request.url.path.rstrip("/").endswith("/agui"):
            body = await request.body()
            self._log_run_start(body)

            async def receive() -> dict[str, Any]:
                return {"type": "http.request", "body": body, "more_body": False}

            request = Request(request.scope, receive)

        return await call_next(request)

    @staticmethod
    def _log_run_start(body: bytes) -> None:
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            logger.warning(json.dumps({"event": "agui_run_start", "error": "invalid_json_body"}))
            return

        run_id = payload.get("runId")
        thread_id = payload.get("threadId")
        request_id = run_id

        logger.info(
            json.dumps(
                {
                    "event": "agui_run_start",
                    "request_id": request_id,
                    "thread_id": thread_id,
                    "run_id": run_id,
                }
            )
        )


def create_chat_agent(settings: Settings) -> Agent:
    return Agent(
        id="chat-agent",
        model=OpenAILike(
            id=settings.llm_model_id,
            api_key=settings.ai_gateway_api_key or "not-provided",
            base_url=settings.ai_gateway_base_url,
        ),
        instructions=TC_INSTRUCTIONS,
    )


def build_agent_os(settings: Settings | None = None) -> tuple[AgentOS, FastAPI]:
    settings = settings or get_settings()
    chat_agent = create_chat_agent(settings)

    base_app = FastAPI(title="Agent Chat Backend")
    base_app.add_middleware(AgUiRunLoggingMiddleware)

    agent_os = AgentOS(
        agents=[chat_agent],
        interfaces=[AGUI(agent=chat_agent)],
        cors_allowed_origins=CORS_ORIGINS,
        base_app=base_app,
    )
    return agent_os, agent_os.get_app()


_agent_os, app = build_agent_os()


def main() -> None:
    settings = get_settings()
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    _agent_os.serve(
        app="agent_os:app",
        host=settings.agent_os_host,
        port=settings.agent_os_port,
        reload=True,
    )


if __name__ == "__main__":
    main()
