"""Post an approved public reply to a comment on a post you own/manage.

This is the ONE outreach action implemented, and it is deliberately narrow:
replying to a comment on your own Instagram post, via the official Graph API,
after you have reviewed and approved the text.

Not implemented (and intentionally so): cold DMs, emails, or WhatsApp messages
to people who did not contact you first. Those violate Instagram/Meta and
WhatsApp policy. For people who DO message you, reply within Instagram's normal
inbox rules; for people who share their own contact details with consent, add
them to your CRM/export and follow up through your normal channels.
"""

from __future__ import annotations

from .config import Config


def post_comment_reply(config: Config, comment_id: str, message: str) -> dict:
    """Reply to a comment on your own media. Requires Instagram credentials."""
    if not config.instagram_enabled:
        raise RuntimeError(
            "Instagram is not configured. Set IG_ACCESS_TOKEN and "
            "IG_BUSINESS_ACCOUNT_ID in your .env to post replies."
        )

    import requests

    base = f"https://graph.facebook.com/{config.ig_graph_version}"
    url = f"{base}/{comment_id}/replies"
    resp = requests.post(
        url,
        data={"message": message, "access_token": config.ig_access_token},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()
