from enum import StrEnum


class LinkStatus(StrEnum):
    WORKING = "working"
    DOWN = "down"
    UNKNOWN = "unknown"
    SEIZED = "seized"


DEFAULT_CATEGORIES: list[dict[str, str]] = [
    {"slug": "ai", "label": "AI"},
    {"slug": "archive-mirror", "label": "Archive / Mirror"},
    {"slug": "cybersecurity", "label": "Cybersecurity"},
    {"slug": "dark-web", "label": "Dark Web"},
    {"slug": "docs-reference", "label": "Docs / Reference"},
    {"slug": "forum", "label": "Forum"},
    {"slug": "news", "label": "News"},
    {"slug": "official", "label": "Official"},
    {"slug": "piracy", "label": "Piracy"},
    {"slug": "tool", "label": "Tool"},
    {"slug": "unverified", "label": "Unverified"},
    {"slug": "verified", "label": "Verified"},
    {"slug": "x", "label": "X"},
    {"slug": "youtube", "label": "YouTube"},
]
