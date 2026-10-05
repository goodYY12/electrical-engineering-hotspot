---
name: electrical-kaoyan-navigator
description: Research, audit, compare, and explain mainland China electrical-engineering postgraduate admissions, especially 080800 and 085801. Use for 电气考研择校、考情、社媒热度、报名前关注趋势、平台数据抓不到、搜索摘要、访问受限、招生名额、推免、统考、复试、拟录取、专业课改考、冲稳保、院校比较、就业证据或备考迁移分析. Diagnoses collection gaps, treats public media as an approximate early signal, and never invents admissions facts or probabilities.
---

# Electrical Kaoyan Navigator

Build an auditable admissions case, not a prediction.

## Workflow

1. Normalize the target into school, college, major code/name, degree type, study mode, direction, special program, campus, and admission year. Never merge entities merely because their names or major codes match.
2. Collect the available user profile. Continue with explicit unknowns when optional fields are absent.
3. Read `references/search-playbook.md` and `references/source-policy.md`. Use the host's current web search or browser tool to discover and open current official domains and pages before using secondary sources. Query generation is only a search plan: it is never evidence that a live search ran.
4. For pre-registration popularity questions, read `references/heat-methodology.md`. If pages are sparse, blocked, snippet-only, or ambiguous, also read `references/collection-recovery.md`. Log every query and failure before diagnosing missingness.
   When comparing schools, annotate each full observation with `audience_segment` and `content_category`, then generate the comparison through a JSON spec. Do not hand-rank sparse targets.
   For an interactive live view, run `python -m electrical_kaoyan hotspot-web --port 8787` and open `http://127.0.0.1:8787`. Supply the target college's official admissions page when available; the public search channel may return only proxy evidence or no exact matches.
5. Run `python -m electrical_kaoyan research ...` to initialize the case. Pass every public URL found during live discovery with repeated `--source-url URL`; add `--refresh` when the current response must be fetched instead of reused from cache. Prefer five completed admission cycles; use at least three when older evidence is unavailable.
   Inspect `acquisition.json` immediately. `status=discovery_required` means no live collection occurred. Do not present the generated query plan, empty report, or empty evidence ledger as research results. If the host has no web/search/browser capability, state that live discovery is unavailable and return the query plan as pending work.
6. Read `references/data-model.md` before manually correcting or importing data. Preserve field-level evidence, raw snapshots, hashes, revisions, extraction method, confidence, and formulas.
7. Run validation. Keep conflicts and quality issues visible; never silently overwrite or auto-correct them.
8. Read `references/electrical-domain.md` before interpreting subject changes, research strengths, employment, or migration cost.
9. Read `references/decision-framework.md` before personal positioning or school comparison.
10. Render the report with `references/report-template.md`. Separate official facts, derived results, community observations, analysis, and uncertainty.
11. Run `media-compare-report` for a reusable heat comparison. Treat `integrity_status=pass` and `data_readiness=adequate` as separate gates: a correct report can still have insufficient evidence.

## Non-negotiable rules

- Treat `admission_year` as the cycle key; distinguish exam year, announcement date, and effective year.
- Keep planned total, recommended-exempt, special quota, estimated unified quota, and actual unified admissions separate.
- Preserve unknown as unknown; never coerce it to zero.
- Do not treat a retest line as the minimum admitted score.
- Do not compare raw self-set subject scores across schools as if scales were equivalent.
- Treat social posts as weak signals and extract verifiable claims. Never promote them to official facts.
- Use heat only as a pre-registration attention reference. Separate organic attention, commercial amplification, platform coverage, and sampling uncertainty.
- Never translate media volume or heat level into applicant count, application ratio, score-line prediction, or admission probability.
- Do not output fabricated application ratios, precise difficulty scores, discrimination claims, score-suppression claims, grid-recognition rankings, or admission probabilities.
- Respect access controls, robots policy, rate limits, paywalls, CAPTCHAs, and login boundaries. Record `access_limited=true` rather than bypassing controls.
- Keep search snippets, screenshots, cross-platform mentions, and unverifiable dates as proxy evidence. Never promote them to full heat observations.
- Do not call attention low until diverse successful queries approach saturation; otherwise report the specific collection limitation.

## Commands

Use the package CLI; wrapper scripts under `scripts/` expose the same operations.

```text
python -m electrical_kaoyan research --school "重庆大学" --college "电气工程学院" --major 085801 --admission-year 2027 --years 5 --export markdown
python -m electrical_kaoyan research --school "重庆大学" --college "电气工程学院" --major 085801 --admission-year 2027 --source-url "https://example.edu.cn/current-notice" --refresh --export markdown
python -m electrical_kaoyan compare --case CASE_DIR --case OTHER_CASE_DIR --profile profile.json
python -m electrical_kaoyan validate --case CASE_DIR
python -m electrical_kaoyan media-collect --target target.json --url URL --output media.jsonl
python -m electrical_kaoyan media-add --target target.json --platform xiaohongshu --url URL --title TITLE --text TEXT --output media.jsonl
python -m electrical_kaoyan media-log-attempt --target target.json --platform xiaohongshu --query QUERY --outcome access_limited --access-reason login_required
python -m electrical_kaoyan media-diagnose --target target.json --input media.jsonl --attempts search-log.jsonl --expected-platform zhihu --expected-platform xiaohongshu
python -m electrical_kaoyan media-heat --target target.json --input media.jsonl --attempts search-log.jsonl --as-of 2026-08-08 --evidence-output media-evidence.json
python -m electrical_kaoyan media-compare-report --spec comparison-spec.json --as-of 2026-08-08 --output heat-report.md --audit-output report-audit.json
python -m electrical_kaoyan hotspot-web --port 8787
```

Always return the report path, `evidence.json` or `media-evidence.json` path, audit path, cutoff date, unresolved conflicts, missing evidence, confidence, and `data_readiness`. Never describe the dataset as complete while the audit says `incomplete`.
