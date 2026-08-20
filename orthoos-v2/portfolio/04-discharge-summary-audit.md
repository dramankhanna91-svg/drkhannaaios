# 4. Documentation quality audit — synthetic discharge summary

*Fully synthetic document written for demonstration; every name, date and
detail is invented. Author of audit: Dr. Aman Khanna, orthopaedic surgeon.*

## The task

AI systems increasingly draft clinical documentation. Auditing that output
is different from auditing an answer to a question: the failure modes are
omissions, internal contradictions, and ambiguity that a busy reader will
resolve wrongly. Below, a synthetic AI-drafted discharge summary after
total knee replacement, followed by my structured audit.

## Document under audit (synthetic)

> **Discharge Summary — [Patient X], 66F**
> **Procedure:** Right total knee replacement (day 0).
> **Stay:** Uncomplicated. Physiotherapy commenced day 1. Wound clean and
> dry at discharge on day 3.
> **Medications on discharge:** Paracetamol 1 g QID; tramadol 50 mg PRN;
> diclofenac 50 mg TDS for 2 weeks.
> **Instructions:** Weight-bear as comfortable. Remove dressing at home
> after 5 days. Resume all home medications. Review in clinic in 6 weeks.

*(Stated background elsewhere in the notes: hypertension on telmisartan;
type 2 diabetes; eGFR 48; no baseline anticoagulant — relevant to finding
1: the VTE-prophylaxis omission is not explained by pre-existing
anticoagulation.)*

## Audit table

| # | Finding | Type | Severity | Detail |
|---|---|---|---|---|
| 1 | **No VTE prophylaxis on the discharge list** | Omission | **Critical** | Post-TKR patients require a documented venous-thromboembolism prophylaxis plan (pharmacological and/or mechanical, per local protocol). Its absence from a TKR discharge summary is a red-flag omission regardless of which agent the protocol favours. |
| 2 | NSAID (diclofenac) prescribed with eGFR 48 + ARB | Unsafe prescription | **Major** | Regular NSAID dosing in renal impairment combined with an angiotensin-receptor blocker risks acute kidney injury; needs renal-adjusted analgesia strategy instead. |
| 3 | "Weight-bear as comfortable" without device/progression | Ambiguity | Moderate | Acceptable clinically after TKR, but the summary names no walking aid, no progression, no physiotherapy follow-up — the GP and physio reading this cannot reconstruct the plan. |
| 4 | "Resume all home medications" | Dangerous boilerplate | **Major** | Blanket resumption contradicts finding 2 and skips the medication-reconciliation step the summary exists to document. |
| 5 | No wound-review or suture/clip plan; "remove dressing at home" | Omission + risk transfer | Moderate | Transfers a clinical check to the patient with no safety-net instruction (signs of infection, who to call). |
| 6 | No glycaemic instruction post-operatively | Omission | Moderate | Diabetic patient discharged day 3 with no statement on monitoring or sick-day rules. |
| 7 | Six-week review as the ONLY follow-up | Gap | Moderate | No interim contact point; combined with findings 1 and 5, the first 14 days — the highest-risk window — have no scheduled touchpoint. |
| 8 | Tramadol "PRN" with no maximum frequency or daily cap | Unsafe prescription | Moderate | An uncapped PRN opioid on a discharge list, in an older diabetic patient with eGFR 48 where dose spacing deserves comment, invites unsupervised dose creep. |

## Summary judgement (as delivered to a client)

Fluency masks a structurally unsafe document: one critical omission (VTE
prophylaxis), two major medication findings, an uncapped PRN opioid, and a
follow-up scheme that leaves the highest-risk fortnight uncovered. Verdict: **not fit for release without
clinician correction**; the specific correction list is the table above.

## What this demonstrates

Documentation audit needs a reviewer who knows what *must* be present for
this operation (VTE plan, reconciled medications, staged follow-up) — a
checklist a generalist reviewer or an unaided LLM will not reliably hold.
This is directly convertible into a rubric for automated document QA.
