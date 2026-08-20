# B1 — Discovery audit

**Run in:** Claude Code. **READ-ONLY.**

---

Read CLAUDE.md first. This session is read-only. Do not create, edit, delete,
or run anything that writes. Do not print secret values; list env var names only.

Inspect: repository, environment variable names, n8n workflow exports,
webhook contracts (inputs/outputs/auth), database schema and storage,
deployment config, logs location, backup state.

Also inventory assets OUTSIDE this repo that I tell you about or that are
referenced in config: multi-brand content pipeline (Excel calendars, agent
pipeline, VPS cron), Postiz, ElevenLabs, HeyGen, Higgsfield, Canva, Airtable,
Google Calendar, existing telemedicine intake forms and video assessment
protocol, Google Business Profile, domains.

Produce CURRENT STATE REPORT in exactly this format:

1. ARCHITECTURE — one diagram (text) of what actually runs today.
2. INTEGRATIONS — table: system | status (live / partial / dead) | evidence.
3. DATA — schema, where patient data lives, encryption, retention, PHI in
   logs (yes/no, where).
4. AUTOMATION — each n8n workflow: purpose | last successful run | failure modes.
5. SECURITY — secrets handling, auth on webhooks, exposed ports, backup state.
6. BOOKING + PAYMENT — current flow end to end, with the exact point it
   breaks (if it does).
7. REUSE / FIX / KILL — one table, every component, one line each, effort in hours.
8. TOP 3 RISKS — ranked, each with the one-sentence mitigation.
9. FIRST BUILD — the single smallest change that lets a paying patient go
   from WhatsApp to confirmed paid slot with zero manual steps, with hour
   estimate.
10. QUESTIONS — anything you could not determine from the repo.

Label each finding VERIFIED (seen in code/config) or INFERENCE.
