FROM casper-ai-platform-garmin-mcp:latest AS base

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=38094 \
    MCP_TRANSPORT=http \
    MCP_PATH=/mcp

COPY pyproject.toml README.md ./
COPY src ./src

RUN pip install --no-cache-dir --upgrade pip setuptools wheel hatchling && \
    pip install --no-cache-dir ".[test]"

FROM base AS production

EXPOSE 38094

CMD ["telegram-mcp"]
