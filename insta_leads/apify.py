"""Ingest comments produced by an Apify Instagram Comment Scraper run.

You run the scraper on Apify (they operate the proxies and accept the platform
terms as the operator); this module just consumes the output. Two paths:

1. A file you exported from the Apify dataset (JSON array or JSON Lines).
2. A dataset id fetched via the Apify API, if APIFY_TOKEN is set.

Apify's Instagram comment actors vary slightly in field names, so we map the
common ones tolerantly.
"""

from __future__ import annotations

import json
from typing import Any, Iterator

from .config import Config
from .models import RawComment


def _pick(item: dict[str, Any], *keys: str, default: str = "") -> str:
    for k in keys:
        v = item.get(k)
        if v:
            return str(v)
    return default


def _to_comment(item: dict[str, Any], source: str = "apify") -> RawComment | None:
    text = _pick(item, "text", "comment", "commentText", "content")
    if not text:
        return None
    return RawComment(
        comment_id=_pick(item, "id", "commentId", "pk") or f"{source}-{hash(text) & 0xffffffff:x}",
        username=_pick(item, "ownerUsername", "username", "owner", "author", default="unknown"),
        text=text,
        timestamp=_pick(item, "timestamp", "createdAt", "created_at"),
        media_id=_pick(item, "postUrl", "postId", "postShortcode", "media_id", "post_url"),
        source=source,
    )


def read_json_file(path: str, source: str = "scraper") -> Iterator[RawComment]:
    """Read comments from any scraper's output: JSON array or JSON Lines.

    Fields are mapped tolerantly, so output from Apify, Scrapling, or a
    hand-rolled scraper all work as long as each record has a comment text and,
    ideally, a username. `source` just tags where the data came from.
    """
    with open(path, encoding="utf-8") as f:
        head = f.read(1)
        f.seek(0)
        if head == "[":
            items = json.load(f)
        else:  # JSON Lines
            items = [json.loads(line) for line in f if line.strip()]
    for item in items:
        c = _to_comment(item, source=source)
        if c:
            yield c


def read_apify_file(path: str) -> Iterator[RawComment]:
    """Read an exported Apify dataset (JSON array or JSON Lines)."""
    return read_json_file(path, source="apify")


def fetch_apify_dataset(config: Config, dataset_id: str) -> Iterator[RawComment]:
    """Fetch items from an Apify dataset you already ran. Needs APIFY_TOKEN."""
    if not config.apify_token:
        raise RuntimeError(
            "APIFY_TOKEN is not set. Export the dataset to a file and use "
            "`import-apify --file` instead, or set APIFY_TOKEN in your .env."
        )

    import requests

    url = f"https://api.apify.com/v2/datasets/{dataset_id}/items"
    resp = requests.get(
        url,
        params={"token": config.apify_token, "clean": "true", "format": "json"},
        timeout=60,
    )
    resp.raise_for_status()
    for item in resp.json():
        c = _to_comment(item)
        if c:
            yield c
