# Search playbook

## Discovery order

1. Discover and verify the university's official root domain.
2. Locate graduate school/admissions and the exact college domain; cache an allowlist with verification evidence.
3. Search official domains for catalogue, subjects, syllabus, recommendation roster, retest rules/roster, proposed admission roster, transfer, employment, laboratories, and revisions.
4. Use CHSI/YZ and Ministry sources.
5. Use reputable secondary pages only to find missing primary sources.
6. Search public social/community pages for weak signals only when requested.

Do not maintain a sole fixed URL per university. Retain discovered URL, canonical URL, referring query, domain classification, and confidence.

## Query templates

Combine school, college, `080800`/`085801`, admission year, and one intent: `招生目录`, `考试大纲`, `推免`, `复试细则`, `复试名单`, `拟录取`, `调剂`, `就业质量报告`, `电路`, `专业课调整`. Add `site:<verified-domain>` for official discovery.

For weak signals add one term such as `改考`, `专业课`, `复试体验`, `压分`, `报录比`, `就业`, `国家电网`; never interpret result count as applicant count.

## Stop conditions

Stop expanding search when a specific official source directly establishes the fact and no conflict is present. For missing facts record queries attempted, access limitations, and the smallest useful request for user-provided material.
