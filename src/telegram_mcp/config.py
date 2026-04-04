"""Configuration for the Telegram MCP server."""

from __future__ import annotations

import os
from dataclasses import dataclass


def _parse_csv_env(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


@dataclass(frozen=True)
class AppConfig:
    bot_token: str
    telegram_api_base: str

    # Server
    transport: str
    host: str
    port: int
    path: str
    allowed_hosts: list[str]
    allowed_origins: list[str]


def load_app_config() -> AppConfig:
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    if not bot_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is required")

    default_allowed_hosts = ["127.0.0.1:*", "localhost:*", "[::1]:*"]
    default_allowed_origins = [
        "http://127.0.0.1:*",
        "http://localhost:*",
        "http://[::1]:*",
    ]

    return AppConfig(
        bot_token=bot_token,
        telegram_api_base=os.getenv("TELEGRAM_API_BASE", "https://api.telegram.org"),
        transport=os.getenv("MCP_TRANSPORT", "http"),
        host=os.getenv("MCP_HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "38094")),
        path=os.getenv("MCP_PATH", "/mcp"),
        allowed_hosts=default_allowed_hosts + _parse_csv_env(os.getenv("MCP_ALLOWED_HOSTS")),
        allowed_origins=default_allowed_origins + _parse_csv_env(os.getenv("MCP_ALLOWED_ORIGINS")),
    )
