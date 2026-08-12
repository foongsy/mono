"""Shared pytest fixtures for backend integration tests."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from agent_os import build_agent_os
from config import Settings


@pytest.fixture
def settings_no_gateway_key() -> Settings:
    return Settings(
        ai_gateway_api_key=None,
        llm_model_id="google/gemini-3.5-flash-lite",
        ai_gateway_base_url="https://ai-gateway.vercel.sh/v1",
        agent_os_host="0.0.0.0",
        agent_os_port=7777,
    )


@pytest.fixture
def settings_invalid_gateway_key() -> Settings:
    return Settings(
        ai_gateway_api_key="invalid-key-for-health-check",
        llm_model_id="google/gemini-3.5-flash-lite",
        ai_gateway_base_url="https://ai-gateway.vercel.sh/v1",
        agent_os_host="0.0.0.0",
        agent_os_port=7777,
    )


@pytest.fixture
async def client_no_gateway_key(settings_no_gateway_key: Settings):
    _, app = build_agent_os(settings_no_gateway_key)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest.fixture
async def client_invalid_gateway_key(settings_invalid_gateway_key: Settings):
    _, app = build_agent_os(settings_invalid_gateway_key)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
