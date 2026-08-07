# Source and evidence policy

## Grades

- **S**: Ministry of Education, CHSI/YZ, university graduate school/admissions office, college site, official catalogue, syllabus, retest rule, roster, or admission notice. May directly support admissions facts.
- **A**: other official university channels, employment reports, official news, laboratories, and research platforms. May support institutional facts; trace core admissions numbers to S where possible.
- **B**: reputable education media or secondary pages that identify an official origin. Use for discovery and retain only when the primary source is unavailable.
- **C**: Zhihu, Xiaohongshu, Bilibili, forums, public experience posts. Use for experience, perceived difficulty, popularity leads, and claims requiring verification. Never use alone for quota, subject, score line, admitted count, ratio, or rule.

Within a grade prefer the source that is more specific to the exact program, newer for the same cycle, explicit about scope, and a primary document rather than a summary page. Do not discard a lower-priority contradiction.

## Field evidence

Attach evidence to each fact, not merely its parent row. Record:

`evidence_id`, canonical URL, title, source type/grade, publication and access dates, page/table, raw snippet, extraction method, confidence, content hash, archive path, and revision.

For a derived fact also record `derived=true`, the formula, and all input evidence IDs. Render derived values as calculations, never as quoted official facts.

## Conflicts

Create a conflict when two applicable facts disagree after entity, year, unit, and scope normalization. Investigate whether the numbers represent college versus program, planned versus actual, total versus unified-exam, full-time versus part-time, or an updated notice. Select a preferred fact only with an explicit resolution rationale; retain all alternatives.

## Access and archival rules

- Fetch public content only. Do not bypass authentication, CAPTCHA, paywall, robots restrictions, or anti-abuse controls.
- Prefer HTTP and text extraction; use a browser for genuinely dynamic public pages; use OCR only for scanned pages.
- Apply per-domain delay, bounded retries, exponential backoff, cache, stable User-Agent, and `--refresh` for explicit re-fetch.
- Store canonical URL, timestamps, SHA-256, media type, raw path, parsed path, response status, and access limitations.
- A changed hash creates a new revision. Never overwrite the prior archived body.

## Social claims

Extract the proposition separately from sentiment and engagement. Record claim type, target entity/cycle, author self-description, commercial signals, verification status, and evidence links. Valid statuses are `unverified`, `verified_by_official`, `corroborated`, and `contradicted`.

Separate organic and commercial posts. Likes and repeated marketing copy measure visibility, not truth or applicant count.
