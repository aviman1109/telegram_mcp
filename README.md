# Telegram MCP

Telegram Bot API MCP server with per-workspace routing for the [Model Context Protocol](https://modelcontextprotocol.io/).

## Features

- **notify** — Send to the workspace's default channel (routed via HTTP headers in `.mcp.json`)
- **send_message** — Send to any specific chat/topic (for cross-channel delivery)
- **get_bot_info** — Retrieve bot identity and capabilities
- Per-workspace default routing via `X-Default-Chat-Id` and `X-Default-Topic-Id` headers
- Supports `Markdown`, `MarkdownV2`, and `HTML` parse modes

## Requirements

- Python 3.11+
- A Telegram Bot token from [@BotFather](https://t.me/BotFather)
- The bot must be added to target groups with send-message permission

## Configuration

### Environment Variables

| Variable | Required | Description |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | Yes | Bot API token from BotFather |
| `PORT` | No | Server port (default: `38094`) |
| `MCP_TRANSPORT` | No | `http` (default), `sse`, or `stdio` |
| `MCP_HOST` | No | Bind address (default: `0.0.0.0`) |
| `MCP_PATH` | No | MCP endpoint path (default: `/mcp`) |
| `MCP_ALLOWED_HOSTS` | No | Comma-separated allowed hosts |
| `MCP_ALLOWED_ORIGINS` | No | Comma-separated allowed origins |

### Per-Workspace Routing

Each workspace's `.mcp.json` can include HTTP headers that set the default Telegram destination for `notify()`:

```json
{
  "mcpServers": {
    "telegram": {
      "type": "http",
      "url": "http://127.0.0.1:38094/mcp",
      "headers": {
        "X-Default-Chat-Id": "-1003728321833",
        "X-Default-Topic-Id": "3"
      }
    }
  }
}
```

| Header | Description |
|---|---|
| `X-Default-Chat-Id` | Default Telegram chat ID (required for `notify`) |
| `X-Default-Topic-Id` | Default `message_thread_id` for topic routing (omit for General topic) |

### Known Chat IDs

| chat_id | Name | Use |
|---|---|---|
| `8209401698` | Casper DM (`@aviman1109` ↔ `@casper_nexus_bot`) | **Training / race live push** — iOS Siri reads DM aloud; topic messages do not broadcast |
| `-1003728321833` | 指揮中心 group | Platform / multi-topic routing (see topics 3–6 above) |

DMs require the user to `/start` the bot first.

## Usage

### Docker Compose

```bash
docker compose up -d telegram-mcp
```

### Standalone

```bash
pip install .
TELEGRAM_BOT_TOKEN=<token> telegram-mcp
```

## Tools

### notify

Send a message to this workspace's default channel. No need to specify `chat_id` or `topic_id` — they come from the HTTP headers configured in `.mcp.json`.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `text` | `str` | Yes | Message content |
| `parse_mode` | `str` | No | `Markdown`, `MarkdownV2`, or `HTML` |
| `disable_notification` | `bool` | No | Send silently |

Returns an error if no default headers are configured.

### send_message

Send a message to any specific chat or topic. Use this for cross-channel delivery.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `chat_id` | `int` | Yes | Telegram chat ID (negative for groups) |
| `text` | `str` | Yes | Message content |
| `topic_id` | `int` | No | `message_thread_id` for forum topic delivery |
| `parse_mode` | `str` | No | `Markdown`, `MarkdownV2`, or `HTML` |
| `disable_notification` | `bool` | No | Send silently |

**Note:** The Telegram General topic does not accept `message_thread_id`. Omit `topic_id` to post to General.

### get_bot_info

Returns bot identity: id, username, name, and capabilities.

## Secrets

Store the bot token in a `.env` file or inject via your secrets manager:

```
TELEGRAM_BOT_TOKEN=your_token_here
```

## Project Structure

```
telegram_mcp/
├── Dockerfile
├── pyproject.toml
├── README.md
├── src/telegram_mcp/
│   ├── __init__.py
│   ├── __main__.py
│   ├── server.py       # MCP server bootstrap + header extraction middleware
│   ├── config.py       # Environment-based configuration
│   ├── client.py       # Telegram Bot API async client
│   ├── defaults.py     # Per-request routing via contextvars
│   └── tools.py        # MCP tool definitions (notify, send_message, get_bot_info)
└── secrets/
    └── telegram.env.tpl  # 1Password template
```

## License

MIT
