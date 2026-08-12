"""Integration tests for AG-UI GET /status health endpoint."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_status_returns_2xx_when_app_is_listening(client_no_gateway_key: AsyncClient) -> None:
    response = await client_no_gateway_key.get("/status")
    assert 200 <= response.status_code < 300


@pytest.mark.asyncio
async def test_status_returns_2xx_without_valid_gateway_key(
    client_invalid_gateway_key: AsyncClient,
) -> None:
    """Health must not depend on LLM credentials (contracts/ag-ui-v1.md §1)."""
    response = await client_invalid_gateway_key.get("/status")
    assert 200 <= response.status_code < 300
