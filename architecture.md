# Architecture

## Decision

The project uses three layers with one source of truth for each concern:

1. `skills/electrical-kaoyan-navigator/` is the portable source-of-truth Skill. It contains concise agent procedure and progressive-disclosure references.
2. `.agents/skills/` and `.claude/skills/` contain thin project-discovery adapters for Codex and Claude Code/WorkBuddy.
3. `.codex-plugin/plugin.json` packages the root `skills/` directory as a skills-only plugin. No MCP server is required because acquisition runs locally with existing web/browser tools and the Python package.
4. `src/electrical_kaoyan/` contains deterministic acquisition, parsing, provenance, validation, statistics, and reporting code.

This follows the current Codex distinction: a Skill is the workflow authoring unit; a plugin is the installable distribution unit. The reference repository is useful for its evidence-first posture, but its one-row-per-year schema and planning/validation scripts are insufficient for field-level provenance, electrical subject modeling, revisions, conflicts, or real acquisition.

## Data flow

`query plan -> URL discovery -> archived fetch -> typed parse -> field evidence -> entity normalization -> cross-cycle alignment -> conflicts/quality issues -> domain analysis -> personal decision report`

Raw content is immutable. Re-fetching the same canonical URL creates a revision only when its content hash changes. Derived values link to input evidence IDs and retain a formula.

## Pre-registration heat

Heat is modeled as a latent attention signal rather than an applicant estimate. Observable public posts combine organic interest, commercial amplification, platform recommendation, duplication, and collection bias. The pipeline archives public pages, extracts intent/commercial markers, deduplicates content, caps each author's influence, applies recency decay, and reports separate organic/commercial signals with platform coverage and confidence.

The ordinal heat level is deliberately not a probability or a score-line forecast. A result is useful for monitoring and school-choice timing only when its observation window, queries, missing platforms, duplicate rate, author count, and commercial share remain visible.

Collection is a separate diagnostic layer. Every query attempt records its platform, method, outcome, yield, and access failure. Full public pages and date-verifiable visible observations may enter heat; search snippets, unverifiable screenshots, historical traces, and cross-platform mentions remain explicitly tiered proxy evidence. Diminishing returns across diverse queries produce a saturation measure. Sparse results are classified as low observable attention, access limitation, indexing gap, target ambiguity, or incomplete collection rather than collapsed into one generic absence.

## Cross-agent distribution

The canonical `skills/` Skill uses only open Agent Skills frontmatter. Codex discovers a thin `.agents/skills/` adapter; Claude Code and WorkBuddy discover a thin `.claude/skills/` adapter. A deterministic installer copies the complete canonical Skill into Codex, Claude Code/WorkBuddy, or a caller-specified generic skills directory. Codex-only plugin metadata remains isolated in `.codex-plugin/` and `agents/openai.yaml`.

## Storage

SQLite is the canonical local store because it is bundled with Python, transactional, portable, and easy to audit. JSON is used for the per-run evidence ledger; CSV and Markdown are exports, not canonical storage.

Candidate names are never required. Candidate identifiers are salted hashes scoped to a research case. Raw official files may be retained for audit, but structured exports minimize personal data.

## Deliberate corrections to the initial brief

- OCR is an optional fallback, not a default dependency. Text-layer and table extraction run first.
- Dynamic pages use browser automation only after a normal HTTP fetch cannot obtain public content.
- Search providers are adapters, not a scraping assumption. A run can accept discovered URLs from browser search, user input, or a configured API.
- “Five-school E2E” is a versioned verification corpus with source snapshots and manual check records. Live tests are opt-in so normal pytest never depends on mutable university sites.
- A single overall score is not the primary decision output. Comparison preserves independent risk dimensions and confidence.

## Package boundaries

- `models`: typed identifiers, cycles, facts, evidence, conflicts, profiles.
- `storage`: schema, repositories, migrations, exports.
- `search`: query generation, domain discovery, URL candidates.
- `collection`: observation tiers, query/failure ledger, saturation, and missingness diagnosis.
- `fetchers`: HTTP cache/retry/rate limiting and format dispatch.
- `parsers`: HTML tables, PDF, Excel, Word, admission lists.
- `normalize`: entity, year, subject, quota, and candidate normalization.
- `evidence`: field ledger, revisions, priority, conflict detection.
- `analysis`: statistics, structural breaks, subject changes, migration, profiles.
- `reporting`: Markdown/JSON/CSV with evidence citations.
- `cli`: research, compare, validate, import, export.
