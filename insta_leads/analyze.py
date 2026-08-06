"""Aggregate analysis over a set of comments — competitor / market research.

This is the "one step ahead" layer: instead of scoring one comment at a time,
it looks at a whole batch of comments (e.g. everything on a competitor's post)
and reports the *patterns* — sentiment mix, recurring themes, the questions
people keep asking, pain points, praise, and content ideas.

It is deliberately AGGREGATE. It does not build a per-person contact list or
single anyone out for outreach — the output is insight about the audience, not
a targeting sheet. That keeps it useful for research and clear of the
harvest-and-spam line.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Sequence

from .models import RawComment

if TYPE_CHECKING:
    import anthropic

# Cap how many comments go into one analysis pass, to stay within context and
# keep cost predictable. Larger batches should be sampled or chunked upstream.
MAX_COMMENTS = 400

_SCHEMA = {
    "type": "object",
    "properties": {
        "comment_count": {"type": "integer"},
        "sentiment": {
            "type": "object",
            "properties": {
                "positive": {"type": "integer"},
                "neutral": {"type": "integer"},
                "negative": {"type": "integer"},
            },
            "required": ["positive", "neutral", "negative"],
            "additionalProperties": False,
            "description": "Approximate count of comments in each sentiment bucket.",
        },
        "top_themes": {
            "type": "array",
            "description": "Recurring topics, most common first.",
            "items": {
                "type": "object",
                "properties": {
                    "theme": {"type": "string"},
                    "approx_count": {"type": "integer"},
                    "example": {"type": "string", "description": "A representative comment."},
                },
                "required": ["theme", "approx_count", "example"],
                "additionalProperties": False,
            },
        },
        "common_questions": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Questions the audience keeps asking.",
        },
        "pain_points": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Frustrations, unmet needs, or gaps people mention.",
        },
        "praise_points": {
            "type": "array",
            "items": {"type": "string"},
            "description": "What people react positively to.",
        },
        "content_ideas": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Post/reel ideas suggested by what the audience wants.",
        },
        "summary": {
            "type": "string",
            "description": "2-3 sentence takeaway for a practice marketer.",
        },
    },
    "required": [
        "comment_count", "sentiment", "top_themes", "common_questions",
        "pain_points", "praise_points", "content_ideas", "summary",
    ],
    "additionalProperties": False,
}

_SYSTEM = (
    "You are a market-research analyst for a healthcare practice. You are given "
    "a batch of Instagram comments (often from a competitor's post) and you "
    "surface aggregate patterns: sentiment, recurring themes, the questions the "
    "audience keeps asking, pain points, what earns praise, and content ideas. "
    "Report on the audience as a whole. Do not single out or profile individual "
    "commenters, and do not extract anyone's personal contact details."
)


def analyze_comments(
    client: "anthropic.Anthropic", model: str, comments: Sequence[RawComment]
) -> dict:
    batch = list(comments)[:MAX_COMMENTS]
    if not batch:
        raise ValueError("No comments to analyze.")

    numbered = "\n".join(f"{i+1}. {c.text}" for i, c in enumerate(batch))
    user_content = (
        f"Here are {len(batch)} comments. Analyze them as a group.\n\n{numbered}"
    )

    response = client.messages.create(
        model=model,
        max_tokens=4096,
        system=_SYSTEM,
        messages=[{"role": "user", "content": user_content}],
        output_config={"format": {"type": "json_schema", "schema": _SCHEMA}},
    )

    if response.stop_reason == "refusal":
        raise RuntimeError(
            f"Model refused to analyze the batch: {getattr(response, 'stop_details', None)}"
        )

    text = next((b.text for b in response.content if b.type == "text"), "{}")
    return json.loads(text)


def format_report(result: dict) -> str:
    lines = []
    lines.append(f"Analyzed {result.get('comment_count', '?')} comments")
    s = result.get("sentiment", {})
    lines.append(
        f"Sentiment  : +{s.get('positive', 0)} / ~{s.get('neutral', 0)} / -{s.get('negative', 0)}"
    )
    lines.append("")
    lines.append(f"Summary    : {result.get('summary', '')}")

    def section(title, items, render):
        if not items:
            return
        lines.append("")
        lines.append(f"{title}:")
        for it in items:
            lines.append(f"  - {render(it)}")

    section("Top themes", result.get("top_themes"),
            lambda t: f"{t['theme']} (~{t['approx_count']})  e.g. \"{t['example']}\"")
    section("Common questions", result.get("common_questions"), lambda q: q)
    section("Pain points", result.get("pain_points"), lambda p: p)
    section("Praise points", result.get("praise_points"), lambda p: p)
    section("Content ideas", result.get("content_ideas"), lambda c: c)
    return "\n".join(lines)
