"""Environment-backed settings for the AgentOS backend."""

from __future__ import annotations

import os
from dataclasses import dataclass

DEFAULT_LLM_MODEL_ID = "google/gemini-3.5-flash-lite"
DEFAULT_AI_GATEWAY_BASE_URL = "https://ai-gateway.vercel.sh/v1"
DEFAULT_AGENT_OS_HOST = "0.0.0.0"
DEFAULT_AGENT_OS_PORT = 7777


@dataclass(frozen=True, slots=True)
class Settings:
    ai_gateway_api_key: str | None
    llm_model_id: str
    ai_gateway_base_url: str
    agent_os_host: str
    agent_os_port: int


def get_settings() -> Settings:
    """Load settings from the process environment without import-time side effects."""
    port_raw = os.getenv("AGENT_OS_PORT", str(DEFAULT_AGENT_OS_PORT))
    return Settings(
        ai_gateway_api_key=os.getenv("AI_GATEWAY_API_KEY"),
        llm_model_id=os.getenv("LLM_MODEL_ID", DEFAULT_LLM_MODEL_ID),
        ai_gateway_base_url=os.getenv("AI_GATEWAY_BASE_URL", DEFAULT_AI_GATEWAY_BASE_URL),
        agent_os_host=os.getenv("AGENT_OS_HOST", DEFAULT_AGENT_OS_HOST),
        agent_os_port=int(port_raw),
    )
