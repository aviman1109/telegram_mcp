"""Telegram Bot API client."""

from __future__ import annotations

import re

import httpx

from telegram_mcp.config import AppConfig


def _md_to_html(text: str) -> str:
    """Convert common Markdown patterns to Telegram-compatible HTML.

    Handles: **bold**, *italic*, `code`, ```pre```, ~strikethrough~,
    [text](url), headings (#/##/###), horizontal rules (---), and tables.
    """
    # Escape HTML entities first
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    # Code blocks (``` ... ```)
    text = re.sub(r"```(\w*)\n(.*?)```", r"<pre>\2</pre>", text, flags=re.DOTALL)

    # Inline code (`...`)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)

    # Headings (# / ## / ###) → bold
    text = re.sub(r"^#{1,6}\s+(.+)$", r"<b>\1</b>", text, flags=re.MULTILINE)

    # Horizontal rules (--- or ===) → em dash line
    text = re.sub(r"^[-=]{3,}\s*$", "─────────────", text, flags=re.MULTILINE)

    # Tables: strip separator rows (|---|---|) and convert data rows to plain text
    def _table_row(m: re.Match) -> str:
        row = m.group(0)
        # Skip separator rows (only dashes, pipes, colons, spaces)
        if re.match(r"^\|[\s\-:|]+\|$", row.strip()):
            return ""
        # Extract cells, strip whitespace
        cells = [c.strip() for c in row.strip().strip("|").split("|")]
        return "  ".join(cells)

    text = re.sub(r"^\|.+\|$", _table_row, text, flags=re.MULTILINE)

    # Bold (**...**)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)

    # Italic (*...* but not inside bold tags)
    text = re.sub(r"(?<!</b>)\*(.+?)\*", r"<i>\1</i>", text)

    # Italic (_..._)
    text = re.sub(r"(?<!\w)_(.+?)_(?!\w)", r"<i>\1</i>", text)

    # Strikethrough (~...~)
    text = re.sub(r"~(.+?)~", r"<s>\1</s>", text)

    # Links [text](url)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)

    return text


class TelegramClient:
    """Thin async wrapper around the Telegram Bot API."""

    def __init__(self, config: AppConfig) -> None:
        self._base = f"{config.telegram_api_base}/bot{config.bot_token}"
        self._http = httpx.AsyncClient(timeout=30)

    async def send_message(
        self,
        chat_id: int,
        text: str,
        topic_id: int | None = None,
        parse_mode: str | None = None,
        disable_notification: bool = False,
    ) -> dict:
        # Auto-convert Markdown → HTML for reliable Telegram rendering
        if parse_mode and parse_mode.lower() in ("markdown", "markdownv2"):
            text = _md_to_html(text)
            parse_mode = "HTML"

        payload: dict = {
            "chat_id": chat_id,
            "text": text,
        }
        if topic_id is not None:
            payload["message_thread_id"] = topic_id
        if parse_mode:
            payload["parse_mode"] = parse_mode
        if disable_notification:
            payload["disable_notification"] = True

        resp = await self._http.post(f"{self._base}/sendMessage", json=payload)
        data = resp.json()
        if not data.get("ok"):
            desc = data.get("description", resp.text)
            raise RuntimeError(f"Telegram API error ({resp.status_code}): {desc}")
        return data

    async def get_me(self) -> dict:
        resp = await self._http.get(f"{self._base}/getMe")
        data = resp.json()
        if not data.get("ok"):
            desc = data.get("description", resp.text)
            raise RuntimeError(f"Telegram API error ({resp.status_code}): {desc}")
        return data

    async def close(self) -> None:
        await self._http.aclose()
