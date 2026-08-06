# drkhannaaios — Instagram comment triage for a healthcare practice

Capture enquiries left as **comments on your own Instagram posts**, use AI to
sort the real patient enquiries from spam and compliments, understand what each
person wants, and draft warm, on-brand replies you approve before anything is
sent.

## What this does (and what it deliberately doesn't)

**It does:**

- Ingest comments — from a **CSV you provide**, or from a post on the
  **Instagram Business/Creator account you own or manage** (official Graph API).
- Ingest comments scraped by an **Apify** Instagram comment actor you run
  (`import-apify`) — e.g. comments on a competitor's public post.
- **AI triage** each comment with Claude: category (appointment enquiry / price
  question / compliment / spam / …), whether it's a real lead, the person's
  intent, name, any contact details they volunteered, urgency, and language.
- **Aggregate analysis** across a batch of comments (`analyze`) — sentiment mix,
  recurring themes, the questions the audience keeps asking, pain points, praise,
  and content ideas. This is the competitor/market-research view.
- Draft a short **public reply** and a **DM reply** for you to review.
- Keep every lead in a local **SQLite database** and **export a CSV** — your
  CRM / follow-up ("audience") list.
- Optionally **post an approved reply** to a comment on your own post.

**It deliberately does NOT:**

- Scrape comments from **other people's** posts (e.g. another doctor's account).
- Send **cold DMs, emails, or WhatsApp messages** to people who did not contact
  you first.
- Push scraped usernames into a Meta "custom audience".

Those actions violate Instagram/Meta and WhatsApp policy and are the fastest way
to get a clinic's accounts and phone number banned, so they are not built here.
For people who **do** message you, reply within Instagram's normal inbox rules;
for people who **share their own** contact details with consent, add them to the
exported list and follow up through your usual channels.

**On scraping competitor comments:** run the scrape on **Apify** (they operate
the proxies and accept the platform terms as the operator) and feed the output
into `import-apify`. This tool does not implement stealth/anti-detection
scraping itself. The `analyze` command is **aggregate** — it reports patterns
about the audience, not a per-person contact list to message.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# then edit .env and set ANTHROPIC_API_KEY
```

CSV import and listing work with **no credentials at all**. You only need
Instagram credentials for the `pull` and `reply` commands.

## Usage

```bash
# 1. Bring comments in (no credentials needed). Try the included sample:
python -m insta_leads import --csv sample_comments.csv

# 2. Run the AI triage over anything new (needs ANTHROPIC_API_KEY):
python -m insta_leads triage

# 3. Review the captured enquiries:
python -m insta_leads list --enquiries

# 4. Export a CRM / follow-up sheet:
python -m insta_leads export --out leads.csv --enquiries
```

### Competitor / market research

Run an Instagram comment scraper on Apify against a public post, export the
dataset, then:

```bash
# Load the scraped comments:
python -m insta_leads import-apify --file apify_dataset.json
# ...or fetch a dataset by id (needs APIFY_TOKEN):
python -m insta_leads import-apify --dataset-id <DATASET_ID>

# Aggregate analysis over everything (or one post's comments):
python -m insta_leads analyze
python -m insta_leads analyze --media https://instagram.com/p/XYZ
```

`analyze` reports sentiment mix, top themes, common questions, pain points,
praise, and content ideas — audience-level insight, not a targeting list.

### Optional — your own Instagram account

With `IG_ACCESS_TOKEN` and `IG_BUSINESS_ACCOUNT_ID` set in `.env`:

```bash
# Pull comments from a post you own/manage (use its media id):
python -m insta_leads pull --media <MEDIA_ID>

# Post an AI-drafted reply (you confirm before it sends):
python -m insta_leads reply <COMMENT_ID>
```

Getting the token requires a Meta app with the `instagram_manage_comments`
permission on your Business/Creator account — see Meta's Instagram Graph API
docs. This is the same account whose posts you want to manage.

## CSV format

Header row required. `username` and `text` are the only fields you really need
(a stable id is generated from the text if `comment_id` is missing):

```csv
comment_id,username,text,timestamp,media_id
c001,priya_sharma,"How do I book an appointment?",2026-08-01T09:12:00Z,POST1
```

## Configuration

| Env var | Default | Purpose |
|---|---|---|
| `ANTHROPIC_API_KEY` | — | Claude API key (required for `triage`) |
| `INSTA_LEADS_MODEL` | `claude-opus-5` | Triage model. Use `claude-haiku-4-5` for cheaper high-volume runs. |
| `INSTA_LEADS_DB` | `leads.db` | SQLite file path |
| `APIFY_TOKEN` | — | Apify token, for `import-apify --dataset-id` (optional) |
| `IG_ACCESS_TOKEN` | — | Instagram Graph API token (optional) |
| `IG_BUSINESS_ACCOUNT_ID` | — | Your IG Business/Creator account id (optional) |
| `IG_GRAPH_VERSION` | `v21.0` | Graph API version |

## Layout

```
insta_leads/
  config.py    env / .env configuration
  models.py    Lead dataclass + SQLite store
  ingest.py    CSV import + Graph API comment fetch (your own posts)
  apify.py     import comments from an Apify scraper run (competitor posts)
  triage.py    the AI brain — classify + draft replies via Claude
  analyze.py   aggregate analysis over a batch of comments (research)
  reply.py     post an approved reply to your own post
  cli.py       command-line interface
```
