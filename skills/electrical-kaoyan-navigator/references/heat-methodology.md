# Pre-registration media heat methodology

## First-principles model

Before registration, the real applicant count does not exist as an observable fact. The useful latent variable is **current attention with intent**, which can influence later school choice but is not identical to applications.

Observable traces arise from different causes:

`observed media = organic attention + commercial amplification + platform recommendation + repeated copies + collection bias`

The system therefore estimates an ordinal attention signal only after separating these components. It does not claim statistical representativeness.

## Stronger and weaker traces

Prefer signals that require independent, sustained action:

- independent organic authors discussing the same target
- posts spread across multiple days and platforms
- comments or saves that indicate planning intent
- specific questions about subject, catalogue, retest, books, or switching schools
- momentum relative to the target's own earlier observation window

Downweight:

- training agencies, paid consulting, material sellers, contact diversion
- duplicated or near-duplicated copy
- one author posting repeatedly
- pure reposts, generic rankings, clickbait, and institution-generated campaigns
- raw likes without visible intent or comparable exposure

## Processing

1. Define the exact program identity and query set.
2. Record the observation window, every query attempted, platforms reached, failures, and access limitations. Read `collection-recovery.md` for missingness diagnosis.
3. Archive public pages and retain URL, timestamps, content hash, extraction method, and visible metrics.
4. Normalize posts; classify likely commercial content with transparent rules.
5. Deduplicate exact URLs/content and cluster near-duplicate text.
6. Cap each author's contribution to prevent prolific accounts from dominating.
7. Apply recency decay with a disclosed half-life. Keep raw and decayed components.
8. Separate organic heat, commercial heat, and momentum.
9. Keep snippet-only, screenshot-only without a verified date, historical, and cross-platform traces as proxy evidence; they cannot satisfy the minimum heat sample.
10. Output an ordinal level: `very_low`, `low`, `medium`, `high`, `very_high`, or `insufficient_data`.
11. Output confidence from coverage, independent-source count, time span, missing platforms, and commercial share.
12. When data are insufficient, output one collection diagnosis instead of treating all missingness alike.

## Interpretation boundary

Heat answers: “Within the observable public sample, is attention around this exact target unusually active, broad, sustained, or rising?”

It does not answer: “How many people will register?” A high-heat/low-confidence result is a monitoring alert, not proof that the program will become harder. Always show data cutoff, observation window, unique authors, organic/commercial counts, platform coverage, duplicate rate, and confidence.
