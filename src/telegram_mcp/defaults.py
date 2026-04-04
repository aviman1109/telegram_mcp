"""Per-request default routing extracted from HTTP headers."""

from __future__ import annotations

from contextvars import ContextVar
from dataclasses import dataclass


@dataclass(frozen=True)
class RouteDefaults:
    chat_id: int | None = None
    topic_id: int | None = None


_current_defaults: ContextVar[RouteDefaults] = ContextVar("route_defaults", default=RouteDefaults())


def set_defaults(defaults: RouteDefaults) -> None:
    _current_defaults.set(defaults)


def get_defaults() -> RouteDefaults:
    return _current_defaults.get()


def extract_defaults_from_headers(headers: list[tuple[bytes, bytes]]) -> RouteDefaults:
    chat_id = None
    topic_id = None
    for key, value in headers:
        k = key.lower()
        if k == b"x-default-chat-id":
            try:
                chat_id = int(value.decode())
            except (ValueError, UnicodeDecodeError):
                pass
        elif k == b"x-default-topic-id":
            try:
                topic_id = int(value.decode())
            except (ValueError, UnicodeDecodeError):
                pass
    return RouteDefaults(chat_id=chat_id, topic_id=topic_id)
