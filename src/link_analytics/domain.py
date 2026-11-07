"""Validation and privacy-aware request classification for tracked links."""

import hashlib
import hmac
import re
import secrets
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date
from urllib.parse import urlsplit, urlunsplit

_BOT = re.compile(
    r"bot|crawler|spider|preview|slack|discord|facebookexternalhit|whatsapp|curl|wget|python|httpx|headless",
    re.IGNORECASE,
)


def normalize_destination(value: str) -> str:
    """Accept nonempty HTTPS links to supported Telegram domains."""
    value = value.strip()
    if any(ord(char) < 32 or ord(char) == 127 for char in value) or "\\" in value:
        raise ValueError("Invalid URL")
    try:
        url = urlsplit(value)
        if (
            url.scheme != "https"
            or url.netloc.lower() not in {"t.me", "telegram.me"}
            or not url.path.strip("/")
            or url.username
            or url.password
        ):
            raise ValueError("Expected an HTTPS link to a Telegram destination")
    except ValueError as exc:
        raise ValueError("Invalid Telegram destination") from exc
    return urlunsplit(("https", "t.me", url.path, url.query, url.fragment))


def classify_request(method: str, headers: Mapping[str, str]) -> str:
    """Separate likely transitions from technical requests using simple heuristics."""
    headers = {key.lower(): value for key, value in headers.items()}
    if method.upper() == "HEAD":
        return "head"
    if any("prefetch" in headers.get(key, "").lower() for key in ("purpose", "sec-purpose", "x-purpose")):
        return "prefetch"
    user_agent = headers.get("user-agent", "")
    return "technical" if not user_agent or _BOT.search(user_agent) else "transition"


def signed_browser_token(secret: bytes, value: str = "") -> str:
    """Verify an existing signed token or issue a fresh random token."""
    token, separator, signature = value.partition(".")
    expected = hmac.new(secret, ("tracking-cookie|" + token).encode(), hashlib.sha256).hexdigest()
    if separator and re.fullmatch(r"[0-9a-f]{32}", token) and hmac.compare_digest(signature, expected):
        return value
    token = secrets.token_hex(16)
    signature = hmac.new(secret, ("tracking-cookie|" + token).encode(), hashlib.sha256).hexdigest()
    return f"{token}.{signature}"


def visitor_hash(secret: bytes, day: date, browser_token: str) -> str:
    """Create a day-scoped pseudonymous identifier without storing raw request data."""
    message = f"tracking-v1|{day.isoformat()}|{browser_token}".encode()
    return hmac.new(secret, message, hashlib.sha256).hexdigest()


@dataclass(frozen=True)
class DailyMetrics:
    requests: int
    transitions: int
    unique_daily: int

    def __post_init__(self) -> None:
        if not 0 <= self.unique_daily <= self.transitions <= self.requests:
            raise ValueError("Metrics must satisfy 0 <= unique <= transitions <= requests")

    @property
    def technical_requests(self) -> int:
        return self.requests - self.transitions
