"""Command-line interface for insta_leads.

Typical flow:

    # 1. bring comments in (no credentials needed for CSV)
    python -m insta_leads import --csv sample_comments.csv

    # 2. run the AI triage over anything new
    python -m insta_leads triage

    # 3. review the captured enquiries
    python -m insta_leads list --enquiries

    # 4. export a CRM / "audience" sheet of consented leads
    python -m insta_leads export --out leads.csv

    # (optional, needs Instagram credentials — replies on YOUR OWN posts)
    python -m insta_leads pull --media <MEDIA_ID>
    python -m insta_leads reply <COMMENT_ID>
"""

from __future__ import annotations

import argparse
import csv
import sys

from .config import load_config
from .ingest import fetch_comments_graph, read_comments_csv
from .models import LeadStore
from .reply import post_comment_reply
from .triage import triage_comment


def _cmd_import(args, config) -> int:
    store = LeadStore(config.db_path)
    added = 0
    total = 0
    for comment in read_comments_csv(args.csv):
        total += 1
        if store.add_comment_if_new(comment):
            added += 1
    store.close()
    print(f"Imported {total} comments from {args.csv} ({added} new).")
    return 0


def _cmd_pull(args, config) -> int:
    store = LeadStore(config.db_path)
    added = 0
    total = 0
    for comment in fetch_comments_graph(config, args.media):
        total += 1
        if store.add_comment_if_new(comment):
            added += 1
    store.close()
    print(f"Pulled {total} comments from media {args.media} ({added} new).")
    return 0


def _cmd_triage(args, config) -> int:
    import anthropic

    client = anthropic.Anthropic()
    store = LeadStore(config.db_path)
    done = 0
    for lead in list(store.iter_by_status("new")):
        from .models import RawComment

        raw = RawComment(
            comment_id=lead.comment_id,
            username=lead.username,
            text=lead.text,
            timestamp=lead.timestamp,
            media_id=lead.media_id,
            source=lead.source,
        )
        try:
            enriched = triage_comment(client, config.model, raw)
        except Exception as exc:  # keep going; surface the failure
            print(f"  ! failed on {lead.comment_id}: {exc}", file=sys.stderr)
            continue
        store.upsert(enriched)
        done += 1
        flag = "ENQUIRY" if enriched.is_enquiry else "        "
        print(f"[{flag}] @{enriched.username}: {enriched.intent_summary}")
    store.close()
    print(f"Triaged {done} new comment(s) with {config.model}.")
    return 0


def _cmd_list(args, config) -> int:
    store = LeadStore(config.db_path)
    status = args.status
    for lead in store.iter_by_status(status):
        if args.enquiries and not lead.is_enquiry:
            continue
        print("-" * 70)
        print(f"@{lead.username}  [{lead.category or 'untriaged'}]  "
              f"urgency={lead.urgency}  status={lead.status}")
        print(f"  comment : {lead.text}")
        if lead.intent_summary:
            print(f"  intent  : {lead.intent_summary}")
        if lead.contact_hint:
            print(f"  contact : {lead.contact_hint}")
        if lead.suggested_public_reply:
            print(f"  reply   : {lead.suggested_public_reply}")
        print(f"  id      : {lead.comment_id}")
    store.close()
    return 0


def _cmd_export(args, config) -> int:
    store = LeadStore(config.db_path)
    fields = [
        "comment_id", "username", "extracted_name", "category", "is_enquiry",
        "urgency", "intent_summary", "contact_hint", "language",
        "suggested_public_reply", "suggested_dm_reply", "status", "timestamp",
    ]
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        n = 0
        for lead in store.iter_by_status():
            if args.enquiries and not lead.is_enquiry:
                continue
            writer.writerow({k: getattr(lead, k) for k in fields})
            n += 1
    store.close()
    print(f"Exported {n} lead(s) to {args.out}.")
    return 0


def _cmd_reply(args, config) -> int:
    store = LeadStore(config.db_path)
    lead = store.get(args.comment_id)
    if not lead:
        print(f"No lead with id {args.comment_id}", file=sys.stderr)
        return 1

    message = args.message or lead.suggested_public_reply
    if not message:
        print("No message to send (no --message and no suggested reply).", file=sys.stderr)
        return 1

    print(f"About to reply to @{lead.username}:")
    print(f"  {message}")
    if not args.yes:
        confirm = input("Send this reply? [y/N] ").strip().lower()
        if confirm != "y":
            print("Cancelled.")
            return 0

    result = post_comment_reply(config, args.comment_id, message)
    store.mark(args.comment_id, "replied")
    store.close()
    print(f"Replied. API response: {result}")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="insta_leads", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_import = sub.add_parser("import", help="import comments from a CSV")
    p_import.add_argument("--csv", required=True)

    p_pull = sub.add_parser("pull", help="pull comments from your own post (Graph API)")
    p_pull.add_argument("--media", required=True, help="media (post) id you own/manage")

    sub.add_parser("triage", help="run AI triage over new comments")

    p_list = sub.add_parser("list", help="list captured leads")
    p_list.add_argument("--status", default=None,
                        help="filter by status: new/triaged/replied/dismissed")
    p_list.add_argument("--enquiries", action="store_true",
                        help="only show comments flagged as real enquiries")

    p_export = sub.add_parser("export", help="export leads to CSV (your CRM / audience list)")
    p_export.add_argument("--out", default="leads_export.csv")
    p_export.add_argument("--enquiries", action="store_true",
                        help="only export real enquiries")

    p_reply = sub.add_parser("reply", help="post an approved reply to a comment on your post")
    p_reply.add_argument("comment_id")
    p_reply.add_argument("--message", default=None,
                        help="override text (defaults to the AI-suggested reply)")
    p_reply.add_argument("--yes", action="store_true", help="skip the confirmation prompt")

    args = parser.parse_args(argv)
    config = load_config()

    dispatch = {
        "import": _cmd_import,
        "pull": _cmd_pull,
        "triage": _cmd_triage,
        "list": _cmd_list,
        "export": _cmd_export,
        "reply": _cmd_reply,
    }
    return dispatch[args.command](args, config)


if __name__ == "__main__":
    raise SystemExit(main())
