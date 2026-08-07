# Public-media collection recovery

Use this workflow when relevant content appears to exist but direct collection is sparse or blocked.

## Observation paths and evidence strength

1. `public_html`: accessible original page with archived response. Strongest path.
2. `user_export`: user-provided platform export with a stable locator. Treat as full content but disclose provenance.
3. `agent_browser`: content visibly read in an allowed browser session. Record visible fields and locator.
4. `screenshot`: transcribe only visible fields; retain the screenshot locator and mark unverified fields unknown.
5. `search_snippet`: discovery evidence only. It may support a bounded proxy signal but never engagement heat.
6. `historical_snapshot`: use only when snapshot date, original URL, and target identity are traceable.
7. `cross_platform_corroboration`: discovery-only evidence unless the original content is independently recovered.

Never bypass login, CAPTCHA, paywall, robots policy, rate limits, or access controls. An allowed signed-in browser may read what the user can normally see; it must not automate prohibited access.

## Required collection log

For every query attempt, record platform, exact query, method, time, outcome, result count, new exact matches, access reason, and notes. Log empty results and failures as carefully as successes.

Use at least three meaningfully different query formulations before calling a platform saturated. Vary school alias, college, major code/name, subject code, admission year, and exclusions. Do not count cosmetic punctuation changes as different queries.

## Missingness diagnosis

- `adequate`: at least three exact, date-verifiable observations are available on the platform.
- `low_observed_attention`: at least three diverse successful public queries reached diminishing returns without enough exact observations.
- `access_limited`: login, CAPTCHA, browser block, or comparable failures dominate.
- `indexing_gap`: snippets or indirect traces exist but full dated observations do not.
- `target_ambiguity`: discoveries cannot be separated from a similar school, college, or program.
- `collection_incomplete`: the query set or platform coverage is not yet sufficient to diagnose.

Only `low_observed_attention` supports a cautious statement that observable attention is low. None of these statuses proves zero discussion.

## Recovery order

1. Improve entity-specific queries and exclusions.
2. Try another public search index or the platform's public search.
3. Use an allowed Agent browser and record visible fields.
4. Ask for a user export or screenshot when the user's signed-in view is necessary.
5. Check a lawful historical snapshot or cross-platform trace.
6. Stop when additional queries yield no new exact sources, disclose saturation and unresolved gaps.

Weak traces remain in `media-evidence.json` as proxy observations. They must not acquire invented dates, authors, engagement counts, or commercial identities.
