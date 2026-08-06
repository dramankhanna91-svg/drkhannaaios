"""Data model and SQLite persistence for captured leads.

A "lead" is one Instagram comment plus the AI triage attached to it. The store
is a plain SQLite file so it works with no external services and is easy to
export (see cli.py `export`).
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Iterable


@dataclass
class RawComment:
    """A comment as ingested, before triage."""

    comment_id: str
    username: str
    text: str
    timestamp: str = ""          # ISO8601 if known
    media_id: str = ""           # the post the comment is on
    source: str = "csv"          # "csv" or "graph"


@dataclass
class Lead:
    """A comment enriched with AI triage and outreach status."""

    comment_id: str
    username: str
    text: str
    timestamp: str = ""
    media_id: str = ""
    source: str = "csv"

    # --- filled in by triage ---
    category: str = ""           # enquiry / price / booking / compliment / spam / other
    is_enquiry: bool = False
    intent_summary: str = ""
    extracted_name: str = ""
    contact_hint: str = ""       # email / phone the person volunteered in the comment
    urgency: str = "low"         # low / medium / high
    language: str = ""
    suggested_public_reply: str = ""
    suggested_dm_reply: str = ""

    # --- workflow ---
    status: str = "new"          # new / triaged / replied / dismissed
    triaged_at: str = ""
    raw_triage: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_comment(cls, c: RawComment) -> "Lead":
        return cls(
            comment_id=c.comment_id,
            username=c.username,
            text=c.text,
            timestamp=c.timestamp,
            media_id=c.media_id,
            source=c.source,
        )


_SCHEMA = """
CREATE TABLE IF NOT EXISTS leads (
    comment_id             TEXT PRIMARY KEY,
    username               TEXT,
    text                   TEXT,
    timestamp              TEXT,
    media_id               TEXT,
    source                 TEXT,
    category               TEXT,
    is_enquiry             INTEGER,
    intent_summary         TEXT,
    extracted_name         TEXT,
    contact_hint           TEXT,
    urgency                TEXT,
    language               TEXT,
    suggested_public_reply TEXT,
    suggested_dm_reply     TEXT,
    status                 TEXT,
    triaged_at             TEXT,
    raw_triage             TEXT
);
"""


class LeadStore:
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute(_SCHEMA)
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

    def upsert(self, lead: Lead) -> None:
        d = asdict(lead)
        d["is_enquiry"] = 1 if lead.is_enquiry else 0
        d["raw_triage"] = json.dumps(lead.raw_triage or {})
        cols = ", ".join(d.keys())
        placeholders = ", ".join(f":{k}" for k in d.keys())
        updates = ", ".join(f"{k}=excluded.{k}" for k in d.keys() if k != "comment_id")
        self.conn.execute(
            f"INSERT INTO leads ({cols}) VALUES ({placeholders}) "
            f"ON CONFLICT(comment_id) DO UPDATE SET {updates}",
            d,
        )
        self.conn.commit()

    def add_comment_if_new(self, c: RawComment) -> bool:
        """Insert a freshly-ingested comment. Returns True if it was new."""
        cur = self.conn.execute(
            "SELECT 1 FROM leads WHERE comment_id = ?", (c.comment_id,)
        )
        if cur.fetchone():
            return False
        self.upsert(Lead.from_comment(c))
        return True

    def _row_to_lead(self, row: sqlite3.Row) -> Lead:
        d = dict(row)
        d["is_enquiry"] = bool(d["is_enquiry"])
        d["raw_triage"] = json.loads(d["raw_triage"] or "{}")
        return Lead(**d)

    def get(self, comment_id: str) -> Lead | None:
        row = self.conn.execute(
            "SELECT * FROM leads WHERE comment_id = ?", (comment_id,)
        ).fetchone()
        return self._row_to_lead(row) if row else None

    def iter_by_status(self, status: str | None = None) -> Iterable[Lead]:
        if status:
            rows = self.conn.execute(
                "SELECT * FROM leads WHERE status = ? ORDER BY timestamp DESC", (status,)
            )
        else:
            rows = self.conn.execute("SELECT * FROM leads ORDER BY timestamp DESC")
        for row in rows:
            yield self._row_to_lead(row)

    def mark(self, comment_id: str, status: str) -> None:
        self.conn.execute(
            "UPDATE leads SET status = ? WHERE comment_id = ?", (status, comment_id)
        )
        self.conn.commit()


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
