"""AI triage: classify a comment and draft replies with Claude.

This is the core engine. Given a raw comment it returns a structured
classification (is this an enquiry? what does the person want? how urgent?)
plus drafted replies you can review before anything is sent.

It uses the official Anthropic SDK with structured outputs, so the response is
always valid JSON matching the schema below — no fragile string parsing.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from .models import Lead, RawComment, now_iso

if TYPE_CHECKING:
    import anthropic

# JSON Schema for the structured output. Kept in sync with the fields we read
# below. `additionalProperties: false` + `required` are needed for strict
# structured outputs.
_TRIAGE_SCHEMA = {
    "type": "object",
    "properties": {
        "category": {
            "type": "string",
            "enum": [
                "appointment_enquiry",
                "price_enquiry",
                "general_question",
                "compliment",
                "complaint",
                "spam",
                "other",
            ],
            "description": "The single best category for this comment.",
        },
        "is_enquiry": {
            "type": "boolean",
            "description": "True if the person wants information or to book — i.e. a real lead.",
        },
        "intent_summary": {
            "type": "string",
            "description": "One short sentence: what does this person actually want?",
        },
        "extracted_name": {
            "type": "string",
            "description": "The person's first name if it appears, else empty string.",
        },
        "contact_hint": {
            "type": "string",
            "description": "Any email or phone number the person VOLUNTEERED in the comment text, else empty string.",
        },
        "urgency": {
            "type": "string",
            "enum": ["low", "medium", "high"],
            "description": "How time-sensitive the enquiry is.",
        },
        "language": {
            "type": "string",
            "description": "The language of the comment, e.g. 'English', 'Hindi'.",
        },
        "suggested_public_reply": {
            "type": "string",
            "description": (
                "A short, warm public reply to post under the comment. "
                "For a real enquiry, invite them to DM or share how to book. "
                "Empty string if no public reply is appropriate (e.g. spam)."
            ),
        },
        "suggested_dm_reply": {
            "type": "string",
            "description": (
                "A friendly direct-message reply to send IF the person messages you. "
                "Empty string if not applicable."
            ),
        },
    },
    "required": [
        "category",
        "is_enquiry",
        "intent_summary",
        "extracted_name",
        "contact_hint",
        "urgency",
        "language",
        "suggested_public_reply",
        "suggested_dm_reply",
    ],
    "additionalProperties": False,
}

_SYSTEM = (
    "You triage comments left on a medical/healthcare practice's Instagram posts. "
    "Your job is to spot genuine patient enquiries, understand what each person wants, "
    "and draft replies in the same language and a warm, professional tone. "
    "Reply drafts must never give medical advice, diagnoses, or promises of outcomes — "
    "they invite the person to get in touch or share how to book an appointment. "
    "Keep public replies to one or two sentences."
)


def triage_comment(
    client: "anthropic.Anthropic", model: str, comment: RawComment
) -> Lead:
    """Run one comment through Claude and return an enriched Lead."""
    user_content = (
        f"Comment by @{comment.username}:\n"
        f'"""{comment.text}"""\n\n'
        "Classify it and draft replies."
    )

    response = client.messages.create(
        model=model,
        max_tokens=1024,
        system=_SYSTEM,
        messages=[{"role": "user", "content": user_content}],
        output_config={
            "format": {"type": "json_schema", "schema": _TRIAGE_SCHEMA}
        },
    )

    if response.stop_reason == "refusal":
        raise RuntimeError(
            f"Model refused to triage comment {comment.comment_id}: "
            f"{getattr(response, 'stop_details', None)}"
        )

    text = next((b.text for b in response.content if b.type == "text"), "{}")
    data = json.loads(text)

    lead = Lead.from_comment(comment)
    lead.category = data["category"]
    lead.is_enquiry = data["is_enquiry"]
    lead.intent_summary = data["intent_summary"]
    lead.extracted_name = data["extracted_name"]
    lead.contact_hint = data["contact_hint"]
    lead.urgency = data["urgency"]
    lead.language = data["language"]
    lead.suggested_public_reply = data["suggested_public_reply"]
    lead.suggested_dm_reply = data["suggested_dm_reply"]
    lead.status = "triaged"
    lead.triaged_at = now_iso()
    lead.raw_triage = data
    return lead
