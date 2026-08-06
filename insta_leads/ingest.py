"""Ingest comments into the store.

Two supported sources:

1. CSV import  — works with no credentials. Export or assemble a CSV of
   comments you're allowed to act on, and load it. Columns (header row required):
       comment_id, username, text, timestamp, media_id
   Only `username` and `text` are strictly required; a comment_id is generated
   if missing.

2. Instagram Graph API — pulls comments from a post on the Business/Creator
   account you own or manage. Requires IG_ACCESS_TOKEN + the media (post) id.
   This is the compliant path: the Graph API only returns comments on media you
   have permission for. It cannot read arbitrary third-party posts.
"""

from __future__ import annotations

import csv
import hashlib
from typing import Iterator

from .config import Config
from .models import RawComment


def _make_id(username: str, text: str, given: str | None) -> str:
    if given:
        return given
    digest = hashlib.sha1(f"{username}|{text}".encode("utf-8")).hexdigest()[:16]
    return f"csv-{digest}"


def read_comments_csv(path: str) -> Iterator[RawComment]:
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            username = (row.get("username") or "").strip()
            text = (row.get("text") or "").strip()
            if not text:
                continue
            yield RawComment(
                comment_id=_make_id(username, text, (row.get("comment_id") or "").strip() or None),
                username=username or "unknown",
                text=text,
                timestamp=(row.get("timestamp") or "").strip(),
                media_id=(row.get("media_id") or "").strip(),
                source="csv",
            )


def fetch_comments_graph(config: Config, media_id: str) -> Iterator[RawComment]:
    """Fetch comments on a post you own/manage via the Instagram Graph API.

    Raises RuntimeError if Instagram credentials are not configured.
    """
    if not config.instagram_enabled:
        raise RuntimeError(
            "Instagram is not configured. Set IG_ACCESS_TOKEN and "
            "IG_BUSINESS_ACCOUNT_ID in your .env to use the Graph API, "
            "or import comments from a CSV instead."
        )

    import requests  # local import so CSV-only users don't need it

    base = f"https://graph.facebook.com/{config.ig_graph_version}"
    url = f"{base}/{media_id}/comments"
    params = {
        "fields": "id,username,text,timestamp",
        "access_token": config.ig_access_token,
        "limit": 50,
    }

    while url:
        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        payload = resp.json()
        for item in payload.get("data", []):
            yield RawComment(
                comment_id=item["id"],
                username=item.get("username", "unknown"),
                text=item.get("text", ""),
                timestamp=item.get("timestamp", ""),
                media_id=media_id,
                source="graph",
            )
        # Follow pagination cursor if present.
        url = payload.get("paging", {}).get("next")
        params = None  # `next` already contains the query string
