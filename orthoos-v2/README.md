# ORTHOOS v2 — Revised Operating Brief

Evaluated and rewritten 20 Aug 2026. Replaces the v1 single-prompt document.

## How to use this directory

v1 was one giant prompt that asked a coding agent to do strategy, market
research, engineering and career coaching in a single pass. That produces
shallow output on all four. v2 splits it:

- **[`CLAUDE.md`](CLAUDE.md)** (Part A) — persistent rules every session inherits.
- **[`prompts/`](prompts/)** (Part B) — four prompts, run **in order**. B0 and B2
  run in a chat with web search (strategy needs research, not a repo). B1 and
  B3 run in Claude Code (engineering needs the repo).
- **[`plan/`](plan/)** (Part C) — the plan itself: economics, 90 days, first 7
  days, the two "machines", decision gates, and the one-thing decision.
  Already written — the agent refines it with your baseline numbers rather
  than regenerating it.
- **[`templates/`](templates/)** — the application tracker and weekly metrics
  sheet, ready to copy into a spreadsheet.
- **[`reports/`](reports/)** — outputs of executed steps: the B1 current-state
  report and the B2 income-stream scoring.

### Run order

| Step | File | Where | Gate |
|---|---|---|---|
| 1 | [`prompts/B0-baseline-questions.md`](prompts/B0-baseline-questions.md) | Chat (~20 min) | Answer before anything else |
| 2 | [`prompts/B1-discovery-audit.md`](prompts/B1-discovery-audit.md) | Claude Code, READ-ONLY | — |
| 3 | [`prompts/B2-income-stream-scoring.md`](prompts/B2-income-stream-scoring.md) | Chat with web search | After B0 |
| 4 | [`prompts/B3-build-mvp.md`](prompts/B3-build-mvp.md) | Claude Code | Only after B1 and B2 are signed off |

## What changed from v1 and why

| # | Change | Why |
|---|---|---|
| 1 | Added surgical income to the economic model | v1 modelled remote income to the rupee and Engine A not at all. A handful of extra surgeries per month is likely your single largest lever. |
| 2 | Reframed the remote target: rate is achievable, sustained hours are the risk | Market evidence supports $50–180/h for practising physicians on expert platforms, but projects pause, pay is region-tiered on some platforms, and 40–60 h/month is not guaranteed. |
| 3 | Fixed the Case Intake contradiction | Module 3 uploaded patient MRIs to an LLM; the safety section forbade exactly that without safeguards. v2 adds consent, de-identification, retention, and provider terms. DPDP penalty phase begins 13 Nov 2026. |
| 4 | Module 10 is no longer software | The "Remote AI Career Engine" is a spreadsheet plus applications. Building it as a module was procrastination. |
| 5 | Scoped 90 days to one funnel | 13 modules + 50 h/month remote work + content does not fit in 60–90 h/month. AI front desk, dashboard, location pages, and booking rebuild are deferred behind gates. |
| 6 | Added the credentials v1 omitted | Journal editorship and postgraduate statistics training are what move you from "rater" pricing to "evaluation lead / methodology consultant" pricing. |
| 7 | Inventoried assets v1 ignored | Multi-brand content pipeline, ElevenLabs/HeyGen/Higgsfield/Postiz stack, telemedicine intake forms, TallRise brand, physician directory. "Build" → "reuse". |
| 8 | Added Phase 0 baseline questions | No stream can be scored without current patient volume, conversion, and fee data. v1 audited the repo but not the business. |
| 9 | Added compliance box and budget/time caps | NMC/IMC advertising rules, Meta health-ad restrictions, official WhatsApp API requirement, cash cap, kill criteria. |
| 10 | Removed the six-persona role stack | Personas don't improve agent output; deliverable formats, stop conditions, and gates do. |
