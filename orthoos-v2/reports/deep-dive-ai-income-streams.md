# Deep dive — the two AI income streams

**Written 20 Aug 2026.** Expands B2 streams #2 (evaluation platforms,
target ₹1.2–1.8L/month) and #4 (direct clinical-AI consulting, target
₹1.5–2L/month). Labels: VERIFIED (sourced) / INFERENCE (estimate).

---

## Stream A — AI evaluation platforms (₹1.2–1.8L/month at 25–30 h)

### How it actually works

You are not "freelancing" in the usual sense. Platforms recruit credentialed
experts into a talent pool once, then match them to time-boxed projects from
AI labs. VERIFIED for Mercor (the top payer for physicians):

- **Application = 3 stages:** profile + resume → written work sample →
  **15-minute AI-conducted video interview** (6–8 structured questions,
  recorded, up to 3 attempts).
- Once approved into the **Physician Talent Network**, you're matched to
  projects on a rolling basis; typical commitments run **15–30 h/week**
  while a project lasts.
- **Pays into India via Stripe** (100+ countries) — so the LUT/FIRC/GST
  question from B0 Q13 is live from the first payout.

### What it pays (VERIFIED ranges, Aug 2026)

| Platform | Physician-relevant rate | Notes |
|---|---|---|
| Mercor | $100–210/h for MD work; primary-care review roles $130–170/h; specialty roles (radiology) reported up to $400/h; generalist RLHF $35–55/h | Highest tier; competitive acceptance |
| Outlier (Scale) | Radiology expert track "up to $150/h"; generalists $15–50/h | Specialty tracks only worth it |
| Handshake AI | Up to $125/h | Aimed at MS/PhD/postdoc profiles — your statistics training qualifies |
| DataAnnotation | Medical track $40–50+/h (starts $20 generalist) | Steadier, lower ceiling |
| Micro1 | Evaluator $20–65/h | Physician feedback reports wide/lower variance |
| Pareto AI | $35–60/h reported | Rates not published |

**The two verified risks:**
1. **Region tiering.** Some vendors pay India-based specialists far less
   (reports as low as $3–7/h for India-employed annotation staff at BPO-style
   vendors). The premium platforms (Mercor, Handshake) advertise global
   rates, but assume nothing — confirm the rate per project before
   accepting, and hold the ₹4,000/h floor from CLAUDE.md.
2. **Burstiness.** Frontier-lab work is project-driven: "work appears, then
   disappears for weeks." This is why the ₹1.2–1.8L row assumes top-2
   platforms concurrently, not one.

### Application playbook (from platform guidance + third-party playbooks)

- **Lead with the domain, not the CV.** Highest-paying tracks are
  domain-expert pools; the profile should open with the credential line:
  *practising orthopaedic surgeon (arthroscopy, arthroplasty) ·
  international journal editor · postgraduate-trained statistician.*
- Written sample: reuse portfolio piece #3 (hallucination audit) — it is
  exactly the work product these platforms sell.
- AI interview: structured, recorded, 3 attempts — treat attempt 1 as a
  scout. Answer like a clinical examiner: reasoning steps, error severity,
  evidence quality.
- Apply to all of them in one week (the fuse is long); after 60 days keep
  the top 2 by effective ₹/h and drop the rest (C6).
- Dedicated device/user profile for anything installing time-tracking.

### Realistic month-by-month (INFERENCE)

Applications week 1 → acceptances weeks 3–8 → first paid hours month 2–3.
Expected value at month 6: 25–30 h/month at a blended $60–100/h ≈
**₹1.3–2.6L/month in good months, with zero months possible** — which is
precisely why Stream B is the anchor and this is the bridge.

---

## Stream B — Direct clinical-AI consulting (₹1.5–2L/month at 15–20 h)

### What the work actually is (and why demand is real)

VERIFIED demand signals:
- OpenAI built **HealthBench with 262 physicians across 60 countries**
  writing case rubrics, and says "hundreds of physician advisors" shaped
  ChatGPT for Clinicians. Physician-written rubric design is now the
  standard evaluation method for health AI — and it is *exactly* portfolio
  piece #5.
- Peer-reviewed methodology papers on case-specific clinical rubrics and
  scalable health-agent evaluation are appearing (arXiv, 2026) — the field
  is professionalising, which favours people who can both grade cases AND
  design the methodology.
- Fracture-detection AI is a crowded, commercially live category (Gleamer
  BoneView, Radiobotics RBfracture, AZmed Rayvolve, ImageBiopsy Lab, Qure.ai
  MSK, DeepTek knee JSN) and these products compete on **published clinical
  validation** — head-to-head registry studies are being published. Every
  one of those studies needs a clinician + statistician to design it.

### The honest correction on "advisory boards"

VERIFIED: startup advisory-board *cash* is small — surveyed physicians most
commonly earn **under $5k/year per company** in cash, usually paired with
0.25–0.75% advisor equity vesting 2–3 years, at 2–5 h/month. A seat ≈
₹1.5L/month is a myth.

**So the ₹1.5–2L/month row is built from project contracts, not board
seats:**

| Contract type | Typical shape (INFERENCE, anchored to verified rates) | ₹ |
|---|---|---|
| Rubric/eval-set build for an MSK or health-AI product | Fixed project, 20–40 h | ₹1.5–4L per project |
| Reader-study / clinical-validation design + analysis | Project, 30–60 h, co-authored paper | ₹2–6L per study |
| Ongoing evaluation-lead retainer | 10–15 h/month | ₹1–1.8L/month |
| Advisory board seat | 2–5 h/month | small cash + equity; take for pipeline, not income |

Anchors: physicians' expected fee for a 2–4 h advisory consultation clusters
at **$1,000–2,500**; biostat consulting runs $70–400/h at firms/universities;
imaging-AI expert work advertises $150/h+ even on open platforms. ₹8–15k/h
for a surgeon-statistician-editor on project work is mid-market, not
premium.

### The wedge: clinical validation, not "advice"

Generic "clinical advisor" pitches compete with every MD on LinkedIn. The
differentiated offer — the only one that uses all three credentials at
once — is:

> "I design and run the clinical-validation and evaluation studies your
> MSK AI product needs — case rubrics, reader studies, statistical analysis,
> publication-grade write-up."

That is a budget line these companies already spend on (regulatory,
publications, sales evidence), and almost nobody combines operating surgeon
+ postgraduate statistics + journal editorship.

### The 20-contact target list (start here)

MSK/fracture imaging-AI (VERIFIED active):
1. **Qure.ai** (Mumbai — MSK fracture X-ray; Indian, easiest first meeting)
2. **DeepTek** (Pune — knee joint-space-narrowing; Indian)
3. **ImageBiopsy Lab** (Vienna — leading MSK imaging AI; absorbed RBfracture)
4. **Gleamer** (Paris — BoneView, CE+FDA)
5. **Radiobotics** (Copenhagen — RBfracture)
6. **AZmed** (Paris — Rayvolve)
7. **Lunit**, 8. **Aidoc**, 9. **Annalise.ai** (broader radiology AI with
   MSK lines)

Adjacent (fill to 20): AI-lab health teams (route: Mercor/Handshake postings
+ direct applications — labs run physician-advisor programs at hundreds of
seats); medical-education companies building ortho question banks; CROs and
device firms needing protocol/statistics review; journals/publishers paying
for methodology review; Indian spine/ortho AI startups (verify current
players in-session before contacting — UNVERIFIED).

### Outreach mechanics (month 2, ~10 h total)

- Channel: LinkedIn + founder/clinical-team email; 20 contacts, 3 waves.
- Message: 4 sentences — who you are (credential line), the wedge offer,
  one portfolio link (the rubric piece), one specific observation about
  *their* product's validation gap. No generic flattery.
- Ask: a 20-minute call. Convert to: paid pilot (one rubric set or one
  study design) at a fixed fee — never free "advisory chats" beyond call 1.
- Expected conversion (INFERENCE): 20 contacts → 3–5 replies → 1–2 calls →
  **1 paid pilot by month 3–4; retainer by month 9–12.** That single
  retainer is the difference between ₹2L and ₹5L months.

### Rules that protect the licence (from CLAUDE.md)

Synthetic cases only in portfolios; no identifiable data to any platform;
disclose all engagements per the non-promotional rule; check the employment
contract before signing (B0 Q6: no meaningful restrictions — but quote the
clauses before the first contract); every foreign payout through the
LUT/FIRC path the CA sets up.

---

## Sources

- [Mercor — Physician Talent Network](https://work.mercor.com/jobs/list_AAABnJzK0z1CNefOyERAAb9m/physician-talent-network)
- [Mercor — AI training jobs for healthcare professionals](https://www.mercor.com/experts/healthcare/)
- [HireFeed — how to get hired on Mercor (2026 playbook)](https://hirefeed.co.in/blog/how-to-get-hired-on-mercor-2026)
- [AI Gig Jobs — Mercor review & guide 2026](https://aigigjobs.vercel.app/platforms/mercor)
- [RemoWork — Mercor hiring process for AI trainers 2026](https://remowork.life/blog/mercor-hiring-process-ai-trainers-2026)
- [Mozibox — AI training for physicians: platforms, pay, experiences](https://mozibox.com/articles/1769)
- [AI Gig Jobs — how doctors earn $150+/hr training models](https://www.aigigjobs.com/blog/medical-professionals-ai-earnings)
- [AlignList — Micro1 reviews](https://alignlist.com/companies/micro1)
- [EdTech — Handshake AI tutor application](https://www.edtech.com/jobs/ai-tutor-general-application-contract-handshake-ai-8663)
- [Outlier — radiology expert jobs](https://outlier.ai/experts/radiology)
- [iMerit press — India annotation pay context](https://imerit.ai/press/ai-data-jobs-attract-highly-skilled-indians/)
- [OpenAI — Introducing HealthBench](https://openai.com/index/healthbench/)
- [Fierce Healthcare — ChatGPT for Clinicians launch](https://www.fiercehealthcare.com/ai-and-machine-learning/openai-launches-chatgpt-clinicians-free-ai-tool-physicians-nps-and)
- [arXiv — case-specific rubrics for clinical AI evaluation](https://arxiv.org/pdf/2604.24710)
- [arXiv — RubricsTree health-agent evaluation](https://arxiv.org/pdf/2606.18203)
- [Sermo — pharmaceutical advisory board pay rates](https://www.sermo.com/resources/pharmaceutical-advisory-board/)
- [Fenwick — compensating physician advisors with equity](https://www.fenwick.com/insights/publications/compensating-physician-advisors-with-equity-considerations-for-life-sciences-companies)
- [Physician Side Gigs — being a physician startup advisor](https://www.physiciansidegigs.com/physician-startup-advisor)
- [ScienceDirect — prospective registry study of commercial fracture-detection AI](https://www.sciencedirect.com/science/article/pii/S1078817425003335)
- [PMC — commercially available AI tools for fracture detection](https://pmc.ncbi.nlm.nih.gov/articles/PMC10860511/)
- [Radiobotics — RBfracture joins ImageBiopsy Lab portfolio](https://radiobotics.com/press-release/automated-fracture-detection-rbfracture-now-part-of-the-imagebiopsy-lab-product-portfolio/)
- [Gleamer — BoneView](https://www.gleamer.ai/copilot/boneview)
- [Qure.ai — MSK radiology](https://www.qure.ai/us/blog/the-importance-of-ai-in-msk-radiology)
- [DeepTek](https://www.deeptek.ai/)
- [Tracxn — DeepTek profile](https://tracxn.com/d/companies/deeptek/__Ovgr1vMD3--mXI8KbpUaXyfmhlAsQjyn-ZhcCvzo_SU)
