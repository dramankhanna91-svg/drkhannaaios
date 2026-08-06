"""Runtime configuration, loaded from environment / .env."""

from __future__ import annotations

import os
from dataclasses import dataclass

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # dotenv is optional; env vars still work without it
    pass


@dataclass
class Config:
    model: str
    db_path: str
    ig_access_token: str | None
    ig_business_account_id: str | None
    ig_graph_version: str

    @property
    def instagram_enabled(self) -> bool:
        return bool(self.ig_access_token and self.ig_business_account_id)


def load_config() -> Config:
    return Config(
        model=os.getenv("INSTA_LEADS_MODEL", "claude-opus-5"),
        db_path=os.getenv("INSTA_LEADS_DB", "leads.db"),
        ig_access_token=os.getenv("IG_ACCESS_TOKEN") or None,
        ig_business_account_id=os.getenv("IG_BUSINESS_ACCOUNT_ID") or None,
        ig_graph_version=os.getenv("IG_GRAPH_VERSION", "v21.0"),
    )
