# 1. ACL injury — clinical reasoning with an explicit decision tree

*Synthetic case. No real patient data. Author: Dr. Aman Khanna, orthopaedic
surgeon (arthroscopy, sports medicine).*

## Why this piece exists

AI systems answering knee-injury questions tend to fail in a specific way:
they enumerate facts about the ACL correctly but cannot commit to a
decision path, or they commit to the wrong branch because they weight an
MRI sentence over the examination. This piece makes the surgeon's decision
process explicit enough that an AI's answer can be graded against each node.

## Synthetic case

A 24-year-old recreational footballer lands awkwardly from a jump, feels a
"pop", and cannot continue playing. The knee swells within two hours. Two
weeks later: moderate effusion resolved, range of motion nearly full,
Lachman test shows increased anterior translation with a soft endpoint,
pivot-shift is positive under gentle examination, no joint-line tenderness,
neurovascular examination normal.

## The decision tree

```
Acute knee injury with immediate swelling ("pop" + haemarthrosis pattern)
│
├─ 1. First question: is this an emergency?
│    Locked knee, gross instability, neurovascular deficit, fracture on
│    X-ray → urgent orthopaedic referral. (None present here.)
│
├─ 2. Establish the working diagnosis CLINICALLY.
│    Rapid effusion after a pivoting injury is an ACL rupture until proven
│    otherwise; Lachman with a soft endpoint is the most reliable clinical
│    sign. MRI CONFIRMS and looks for associated injury (meniscus,
│    cartilage, collaterals) — it does not replace the examination.
│
├─ 3. Associated injury changes the path.
│    Repairable meniscal tear or locked bucket-handle → earlier surgery,
│    because the meniscus takes priority. (None suspected here.)
│
└─ 4. Management is a shared decision built on THREE patient factors:
     a. Instability demand: pivoting sport, manual work on uneven ground?
     b. Functional instability: giving-way episodes in daily life?
     c. Willingness to complete 6–9 months of structured rehabilitation
        (required in BOTH arms — reconstruction is not a shortcut).
     │
     ├─ High-demand knee (this patient: wants to return to football)
     │   → Recommend ACL reconstruction, timed after motion is regained
     │     and swelling settled; prehabilitation first.
     │
     └─ Lower-demand knee, no giving-way
         → Structured rehabilitation with review; reconstruction later if
           functional instability appears. Delayed reconstruction after a
           genuine rehabilitation trial is a legitimate strategy, not a
           failure.
```

## The three grading points I extract from this tree

1. **Did the answer distinguish confirming a diagnosis from making one?**
   An answer that sends the patient for an MRI *to find out what is wrong*
   has the order backwards.
2. **Did it surface the shared-decision factors, or jump to a verdict?**
   "You need surgery" and "you don't need surgery" are both wrong answers
   to this case as stated.
3. **Did it state that rehabilitation is required in both arms?** Omitting
   this is the most common consequential gap: it materially misleads the
   patient about what reconstruction buys them.

That is the pattern of my evaluation work: turn specialist reasoning into
explicit, gradeable checkpoints.
