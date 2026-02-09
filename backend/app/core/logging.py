import logging
import re
from typing import Any

EMAIL_RE = re.compile(r"(^[^@]{2})[^@]*(@.*)$")


def mask_email(value: str) -> str:
    match = EMAIL_RE.match(value)
    if not match:
        return value
    return f"{match.group(1)}***{match.group(2)}"


def sanitize_log_data(data: dict[str, Any]) -> dict[str, Any]:
    sanitized = {}
    for key, value in data.items():
        if key.lower() in {"password", "token", "access_token", "refresh_token"}:
            sanitized[key] = "***"
        elif key.lower() == "email" and isinstance(value, str):
            sanitized[key] = mask_email(value)
        else:
            sanitized[key] = value
    return sanitized


def configure_logging(level: str) -> None:
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s [%(request_id)s] %(message)s",
    )


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "request_id"):
            record.request_id = "-"
        return True


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.addFilter(RequestIdFilter())
    return logger
