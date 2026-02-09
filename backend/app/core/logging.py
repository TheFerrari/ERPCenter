from __future__ import annotations

import logging
from typing import Any

import structlog


SENSITIVE_FIELDS = {"password", "token", "access_token", "refresh_token", "authorization"}


def _mask_value(value: Any) -> Any:
    if isinstance(value, str):
        if "@" in value:
            name, domain = value.split("@", 1)
            return f"{name[:2]}***@{domain}"
        if len(value) > 6:
            return f"{value[:2]}***{value[-2:]}"
    return value


def _sanitize_event(_, __, event_dict: dict[str, Any]) -> dict[str, Any]:
    sanitized = {}
    for key, value in event_dict.items():
        if key.lower() in SENSITIVE_FIELDS:
            sanitized[key] = "***"
        else:
            sanitized[key] = _mask_value(value)
    return sanitized


def configure_logging(level: str = "INFO") -> None:
    logging.basicConfig(level=level)
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            _sanitize_event,
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


logger = structlog.get_logger()
