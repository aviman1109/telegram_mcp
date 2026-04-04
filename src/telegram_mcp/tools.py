"""MCP tool definitions for Telegram Bot API."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from telegram_mcp.client import TelegramClient
from telegram_mcp.defaults import get_defaults


def register_tools(mcp: FastMCP, client: TelegramClient) -> None:
    @mcp.tool()
    async def notify(
        text: str,
        parse_mode: str = "Markdown",
        disable_notification: bool = False,
    ) -> str:
        """Send a message to this workspace's default Telegram channel.

        Uses the default chat_id and topic_id configured via HTTP headers in .mcp.json.
        For sending to a different channel, use send_message instead.

        Args:
            text: Message text. Supports Markdown (default) or HTML.
            parse_mode: Format: "Markdown", "MarkdownV2", or "HTML". Default "Markdown".
            disable_notification: If True, send silently.

        Returns:
            Confirmation with message ID, or error if no defaults are configured.
        """
        defaults = get_defaults()
        if defaults.chat_id is None:
            return "Error: No default chat_id configured. Use send_message with explicit chat_id instead, or configure X-Default-Chat-Id header in .mcp.json."

        result = await client.send_message(
            chat_id=defaults.chat_id,
            text=text,
            topic_id=defaults.topic_id,
            parse_mode=parse_mode,
            disable_notification=disable_notification,
        )
        if result.get("ok"):
            msg = result["result"]
            return f"Message sent (id={msg['message_id']}, chat={msg['chat']['id']})"
        return f"Failed to send: {result}"

    @mcp.tool()
    async def send_message(
        chat_id: int,
        text: str,
        topic_id: int | None = None,
        parse_mode: str = "Markdown",
        disable_notification: bool = False,
    ) -> str:
        """Send a message to any Telegram chat or group topic.

        Use this for cross-channel delivery when the content belongs in a different
        channel than your default. See server instructions for the channel directory.

        Args:
            chat_id: Telegram chat ID (negative for groups).
            text: Message text. Supports Markdown (default) or HTML.
            topic_id: Optional message_thread_id for sending to a specific topic.
                      Omit for the General topic (系統通知).
            parse_mode: Format: "Markdown", "MarkdownV2", or "HTML". Default "Markdown".
            disable_notification: If True, send silently.

        Returns:
            Confirmation with message ID.
        """
        result = await client.send_message(
            chat_id=chat_id,
            text=text,
            topic_id=topic_id,
            parse_mode=parse_mode,
            disable_notification=disable_notification,
        )
        if result.get("ok"):
            msg = result["result"]
            return f"Message sent (id={msg['message_id']}, chat={msg['chat']['id']})"
        return f"Failed to send: {result}"

    @mcp.tool()
    async def get_bot_info() -> dict:
        """Get information about the configured Telegram bot.

        Returns:
            Bot details: id, name, username, can_join_groups, etc.
        """
        result = await client.get_me()
        if result.get("ok"):
            return result["result"]
        return result
