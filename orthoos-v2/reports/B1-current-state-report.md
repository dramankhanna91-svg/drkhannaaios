# B1 — CURRENT STATE REPORT

**Run:** 20 Aug 2026, read-only, against `drkhannaaios` @ branch
`claude/orthoos-v2-brief-4vzhla`. Labels: VERIFIED (seen in code/config) /
REPORTED (stated by Dr. Khanna in B0) / INFERENCE.

**Headline finding (VERIFIED):** this repository contains only the OrthoOS v2
brief itself (16 markdown files: CLAUDE.md, prompts, plan, templates). There
is no application code, no n8n workflow exports, no environment files, no
database schema, no deployment config, and no logs in the repo. Every
operational asset lives outside it (VPS, n8n, WhatsApp layers, Razorpay,
domains, content pipeline) and none has been exported here for inspection.
Most audit sections below are therefore thin by necessity; section 10 lists
exactly what to provide for a full audit.

## 1. ARCHITECTURE

What actually runs today, per repo + B0:

```
[Repo: docs only — nothing runs from it]                        VERIFIED

Outside the repo (REPORTED, not inspected):
  Patients ──(word of mouth / existing patients)──► OPD, Surat
  GBP (claimed, active) ──► calls/visits (volume unknown)
  Domain(s) + live website (low traffic, <~500 visits/mo)
  WhatsApp: access to Libromi + Meta Cloud API + Evolution API
            (which is live for patients: UNKNOWN)
  Razorpay: KYC complete, personal account (live-capable)
  VPS running n8n (per CLAUDE.md profile; workflows not exported)
  Content stack: ElevenLabs / HeyGen / Higgsfield / Postiz / Canva /
                 Airtable (referenced in brief; not verified)
```

## 2. INTEGRATIONS

| System | Status | Evidence |
|---|---|---|
| n8n on VPS | unknown — not in repo | CLAUDE.md profile mentions it; no exports (INFERENCE: exists) |
| WhatsApp — Meta Cloud API | access held; live status unknown | B0 Q8 (REPORTED) |
| WhatsApp — Libromi | access held; live status unknown | B0 Q8 (REPORTED) |
| WhatsApp — Evolution API | access held; MUST NOT carry patient/payment flows | B0 Q8 (REPORTED); CLAUDE.md rule (VERIFIED in repo) |
| Razorpay | live-capable (KYC complete, personal) | B0 Q9 (REPORTED) |
| Google Business Profile | claimed, active; metrics unknown | B0 Q5 (REPORTED) |
| Website/domains | live, low traffic; names unknown | B0 Q10 (REPORTED) |
| Content pipeline (ElevenLabs/HeyGen/Higgsfield/Postiz) | referenced, unverified | Brief §0.1 item 7 |
| Google Calendar | unverified | Not mentioned in B0 answers |
| Telemedicine intake forms | referenced, unverified | Brief §0.1 item 7 |

## 3. DATA

- VERIFIED: no patient data, PHI, or schema of any kind in this repo.
- UNKNOWN: where existing patient data (intake forms, telemedicine records)
  lives, whether encrypted, retention policy, and whether PHI appears in n8n
  execution logs. This must be answered before the MVP accepts its first
  upload (CLAUDE.md retention rule).

## 4. AUTOMATION

- No n8n workflow exports in the repo. Cannot enumerate workflows, last-run
  status, or failure modes. Export workflows (JSON, secrets stripped) into
  `orthoos-v2/audit-inputs/` to complete this section.

## 5. SECURITY

- VERIFIED: no secrets, tokens, or env files committed to the repo (clean).
- UNKNOWN: VPS exposed ports, webhook auth, backup state, n8n access control.

## 6. BOOKING + PAYMENT

- REPORTED: Razorpay can take payments today (KYC complete). No evidence of
  any existing booking flow (calendar, slot logic, or payment link) — the
  end-to-end WhatsApp → paid slot flow does not exist yet. INFERENCE: the
  break point is "everything after the patient's first message is manual".

## 7. REUSE / FIX / KILL

| Component | Verdict | Effort (h) |
|---|---|---|
| OrthoOS v2 brief (this repo) | REUSE — operating doc | 0 |
| Razorpay account (personal) | REUSE — payment links for MVP | 1 (create link + test) |
| GBP (claimed, active) | FIX — overhaul per C5 (categories, Q&As, posts, reviews) | 4–6 |
| Website/domain | FIX — add second-opinion landing page + condition pages | 6–10 |
| WhatsApp official layer (Meta/Libromi) | FIX — pick ONE, confirm number + templates | 2–4 |
| Evolution API for patient flows | KILL (for patient/payment use) — policy risk per CLAUDE.md | 0 |
| n8n workflows | UNKNOWN — audit after export | — |
| Content stack | REUSE — per brief, pending verification | — |

## 8. TOP 3 RISKS

1. **Patient-data path undefined** — no verified consent/de-identification/
   retention setup anywhere; DPDP penalty phase begins 13 Nov 2026.
   Mitigation: implement the CLAUDE.md consent + de-identification flow
   before the first real case is accepted.
2. **Unofficial WhatsApp in the loop** — Evolution API access exists and may
   be live for patients. Mitigation: confirm and move all patient-facing
   flows to Meta Cloud API or Libromi before launch.
3. **Baseline numbers are ranges, not figures** — surgical volumes/fees and
   GBP metrics unknown, so the Day-30/60/90 gates can't be measured
   precisely. Mitigation: fill the specific numbers into B0 within week 1.

## 9. FIRST BUILD

Smallest change letting a paying patient go from WhatsApp to a confirmed
paid slot with zero manual steps: **one n8n workflow** — official WhatsApp
template with a link → landing page (existing site) → Razorpay Payment Link
→ webhook (signature-verified) → Google Calendar appointment-schedule
confirmation + WhatsApp confirmation template. Reuses site, Razorpay,
official WhatsApp. INFERENCE: **6–10 hours** including test payment,
assuming the official WhatsApp number and templates are already approved
(add 2–4 h if not).

## 10. QUESTIONS (blocking a full audit)

1. n8n workflow exports (JSON, secrets stripped) and the list of env var
   NAMES on the VPS.
2. Which WhatsApp layer is live on the patient-facing number; template
   approval status.
3. Domain names + Search Console access; where the site is hosted.
4. Where telemedicine intake data currently lives and its retention state.
5. VPS backup state and exposed ports.
6. Surgeries/month by type and net fee per type (B0 Q2/Q3 refinement).
