from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path
from typing import Annotated

import typer

from .collection import (
    ObservationMethod,
    SearchAttempt,
    append_attempt,
    attempt_id,
    diagnose_collection,
    read_attempts,
)
from .evidence import EvidenceLedger
from .media import (
    append_post,
    collect_public_url,
    platform_from_url,
    post_from_observation,
    read_posts,
    write_media_evidence,
)
from .models import DegreeType, ProgramIdentity, StudyMode
from .heat_reporting import generate_comparison_report
from .reporting import render_skeleton, write_markdown
from .search import generate_queries
from .social import MediaTarget, Platform, analyze_heat, load_heat_rules
from .storage import connect

app = typer.Typer(no_args_is_help=True, help="电气考研证据研究与择校分析")


@app.command()
def research(
    school: Annotated[str, typer.Option()],
    college: Annotated[str, typer.Option()],
    major: Annotated[str, typer.Option()],
    admission_year: Annotated[int, typer.Option()],
    years: Annotated[int, typer.Option(min=1, max=10)] = 5,
    degree_type: Annotated[DegreeType, typer.Option()] = DegreeType.PROFESSIONAL,
    study_mode: Annotated[StudyMode, typer.Option()] = StudyMode.FULL_TIME,
    major_name: Annotated[str, typer.Option()] = "电气工程",
    refresh: Annotated[bool, typer.Option()] = False,
    official_only: Annotated[bool, typer.Option()] = False,
    include_social: Annotated[bool, typer.Option()] = False,
    export: Annotated[str, typer.Option()] = "markdown",
    output: Annotated[Path, typer.Option()] = Path("runs"),
) -> None:
    """Create a research case and query plan; fetched facts are never fabricated."""
    del refresh  # consumed by acquisition adapters once URLs are supplied/discovered
    program = ProgramIdentity(
        school=school, college=college, major_code=major, major_name=major_name,
        degree_type=degree_type, study_mode=study_mode, admission_year=admission_year,
    )
    case = output / f"{program.program_id}"
    case.mkdir(parents=True, exist_ok=True)
    connect(case / "research.sqlite3").close()
    queries = generate_queries(school, college, major, admission_year)
    if not official_only and include_social:
        queries.extend(f"{school} {college} {term}" for term in ("考研经验", "专业课", "复试体验"))
    (case / "query-plan.json").write_text(json.dumps({
        "program": program.model_dump(mode="json"), "years": years,
        "official_only": official_only, "include_social": include_social,
        "queries": queries,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    ledger = EvidenceLedger()
    ledger.export(case / "evidence.json")
    if export == "markdown":
        write_markdown(case / "report.md", render_skeleton(program, conflicts=[], issues=[]))
    elif export == "json":
        (case / "report.json").write_text(json.dumps({
            "program": program.model_dump(mode="json"), "status": "evidence_required",
        }, ensure_ascii=False, indent=2), encoding="utf-8")
    elif export == "csv":
        (case / "facts.csv").write_text("entity_id,field_path,admission_year,value,evidence_id\n", encoding="utf-8")
    else:
        raise typer.BadParameter("export must be markdown, json, or csv")
    typer.echo(str(case.resolve()))


@app.command()
def validate(case: Annotated[Path, typer.Option(exists=True, file_okay=False)]) -> None:
    evidence = case / "evidence.json"
    if not evidence.exists():
        raise typer.BadParameter("case does not contain evidence.json")
    payload = json.loads(evidence.read_text(encoding="utf-8"))
    typer.echo(json.dumps({"evidence": len(payload.get("evidence", [])),
                           "facts": len(payload.get("facts", [])),
                           "conflicts": len(payload.get("conflicts", []))}))


@app.command()
def compare(case: Annotated[list[Path], typer.Option()], profile: Annotated[Path | None, typer.Option()] = None) -> None:
    del profile
    rows = []
    for path in case:
        evidence = json.loads((path / "evidence.json").read_text(encoding="utf-8"))
        rows.append({"case": str(path), "facts": len(evidence.get("facts", [])),
                     "conflicts": len(evidence.get("conflicts", [])),
                     "position": "无法判断", "confidence": "low"})
    typer.echo(json.dumps(rows, ensure_ascii=False, indent=2))


@app.command("media-collect")
def media_collect(
    target: Annotated[Path, typer.Option(exists=True, dir_okay=False)],
    url: Annotated[str, typer.Option()],
    output: Annotated[Path, typer.Option()] = Path("media.jsonl"),
    cache: Annotated[Path, typer.Option()] = Path(".cache/media"),
    rules: Annotated[Path, typer.Option(exists=True, dir_okay=False)] = Path("config/heat_rules.yaml"),
    query: Annotated[str | None, typer.Option()] = None,
    refresh: Annotated[bool, typer.Option()] = False,
    attempt_log: Annotated[Path, typer.Option()] = Path("search-log.jsonl"),
) -> None:
    """Collect one public media page without bypassing access controls."""
    media_target = MediaTarget.model_validate_json(target.read_text(encoding="utf-8"))
    now = datetime.now().astimezone()
    try:
        post = collect_public_url(url=url, target=media_target, output=output, cache=cache,
                                  rules=load_heat_rules(rules), query=query, refresh=refresh)
    except Exception as exc:
        message = str(exc)
        limited_markers = ("403", "429", "captcha", "login", "access denied", "forbidden")
        outcome = "access_limited" if any(item in message.lower() for item in limited_markers) else "error"
        append_attempt(attempt_log, SearchAttempt(
            attempt_id=attempt_id(media_target.target_id, platform_from_url(url), query or url, now),
            target_id=media_target.target_id, platform=platform_from_url(url), query=query or url,
            method="public_html", attempted_at=now, outcome=outcome,
            access_reason=message[:500], result_url=url,
        ))
        raise typer.BadParameter(f"collection failed and was logged: {message}") from exc
    append_attempt(attempt_log, SearchAttempt(
        attempt_id=attempt_id(media_target.target_id, post.platform, query or url, now),
        target_id=media_target.target_id, platform=post.platform, query=query or url,
        method="public_html", attempted_at=now, outcome="success", results_seen=1,
        new_exact_matches=1, result_url=url,
    ))
    typer.echo(post.model_dump_json(indent=2))


@app.command("media-add")
def media_add(
    target: Annotated[Path, typer.Option(exists=True, dir_okay=False)],
    platform: Annotated[Platform, typer.Option()],
    url: Annotated[str, typer.Option()],
    title: Annotated[str, typer.Option()],
    text: Annotated[str, typer.Option()],
    output: Annotated[Path, typer.Option()] = Path("media.jsonl"),
    author_id: Annotated[str | None, typer.Option()] = None,
    published_at: Annotated[str | None, typer.Option(help="ISO-8601 timestamp")] = None,
    likes: Annotated[int | None, typer.Option(min=0)] = None,
    collects: Annotated[int | None, typer.Option(min=0)] = None,
    comments: Annotated[int | None, typer.Option(min=0)] = None,
    query: Annotated[str | None, typer.Option()] = None,
    extraction_method: Annotated[ObservationMethod, typer.Option()] = ObservationMethod.AGENT_BROWSER,
    exact_target_match: Annotated[bool, typer.Option()] = True,
    verified_field: Annotated[list[str] | None, typer.Option()] = None,
    source_locator: Annotated[str | None, typer.Option()] = None,
    audience_segment: Annotated[str, typer.Option()] = "unknown",
    content_category: Annotated[str, typer.Option()] = "other",
    rules: Annotated[Path, typer.Option(exists=True, dir_okay=False)] = Path("config/heat_rules.yaml"),
) -> None:
    """Add an observation read from a public browser page, screenshot, or user export."""
    media_target = MediaTarget.model_validate_json(target.read_text(encoding="utf-8"))
    post = post_from_observation(
        url=url, target=media_target, platform=platform, title=title, text=text,
        rules=load_heat_rules(rules), author_id=author_id,
        published_at=datetime.fromisoformat(published_at) if published_at else None,
        likes=likes, collects=collects, comments=comments, query=query,
        extraction_method=extraction_method,
        exact_target_match=exact_target_match, verified_fields=verified_field,
        source_locator=source_locator,
        audience_segment=audience_segment, content_category=content_category,
    )
    append_post(output, post)
    typer.echo(post.model_dump_json(indent=2))


@app.command("media-heat")
def media_heat(
    input: Annotated[Path, typer.Option(exists=True, dir_okay=False)],
    target: Annotated[Path, typer.Option(exists=True, dir_okay=False)],
    as_of: Annotated[str, typer.Option(help="YYYY-MM-DD")],
    expected_platform: Annotated[list[Platform] | None, typer.Option()] = None,
    attempts: Annotated[Path | None, typer.Option(exists=True, dir_okay=False)] = None,
    rules: Annotated[Path, typer.Option(exists=True, dir_okay=False)] = Path("config/heat_rules.yaml"),
    output: Annotated[Path | None, typer.Option()] = None,
    evidence_output: Annotated[Path, typer.Option()] = Path("media-evidence.json"),
) -> None:
    """Estimate ordinal pre-registration attention with coverage and uncertainty."""
    media_target = MediaTarget.model_validate_json(target.read_text(encoding="utf-8"))
    try:
        cutoff = date.fromisoformat(as_of)
    except ValueError as exc:
        raise typer.BadParameter("as-of must be YYYY-MM-DD") from exc
    posts = read_posts(input)
    heat_rules = load_heat_rules(rules)
    expected = expected_platform or []
    search_attempts = read_attempts(attempts)
    assessment = diagnose_collection(target_id=media_target.target_id, posts=posts,
                                     attempts=search_attempts, expected_platforms=expected)
    report = analyze_heat(posts, target_id=media_target.target_id, as_of=cutoff,
                          expected_platforms=expected, rules=heat_rules)
    write_media_evidence(path=evidence_output, target=media_target, posts=posts,
                         report=report, rules=heat_rules, attempts=search_attempts,
                         assessment=assessment)
    rendered = json.dumps({
        **report.model_dump(mode="json"),
        "collection_assessment": assessment.model_dump(mode="json"),
    }, ensure_ascii=False, indent=2)
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    typer.echo(f"Evidence: {evidence_output.resolve()}", err=True)
    typer.echo(rendered)


@app.command("media-log-attempt")
def media_log_attempt(
    target: Annotated[Path, typer.Option(exists=True, dir_okay=False)],
    platform: Annotated[Platform, typer.Option()],
    query: Annotated[str, typer.Option()],
    outcome: Annotated[str, typer.Option()],
    log: Annotated[Path, typer.Option()] = Path("search-log.jsonl"),
    method: Annotated[str, typer.Option()] = "public_search",
    results_seen: Annotated[int, typer.Option(min=0)] = 0,
    new_exact_matches: Annotated[int, typer.Option(min=0)] = 0,
    access_reason: Annotated[str | None, typer.Option()] = None,
    result_url: Annotated[str | None, typer.Option()] = None,
    notes: Annotated[str | None, typer.Option()] = None,
) -> None:
    """Record a successful, empty, failed, or access-limited collection attempt."""
    allowed = {"success", "no_results", "access_limited", "parse_failed", "error"}
    if outcome not in allowed:
        raise typer.BadParameter(f"outcome must be one of: {', '.join(sorted(allowed))}")
    media_target = MediaTarget.model_validate_json(target.read_text(encoding="utf-8"))
    now = datetime.now().astimezone()
    attempt = SearchAttempt(
        attempt_id=attempt_id(media_target.target_id, platform, query, now),
        target_id=media_target.target_id, platform=platform, query=query, method=method,
        attempted_at=now, outcome=outcome, results_seen=results_seen,
        new_exact_matches=new_exact_matches, access_reason=access_reason,
        result_url=result_url, notes=notes,
    )
    append_attempt(log, attempt)
    typer.echo(attempt.model_dump_json(indent=2))


@app.command("media-diagnose")
def media_diagnose(
    target: Annotated[Path, typer.Option(exists=True, dir_okay=False)],
    input: Annotated[Path, typer.Option(exists=True, dir_okay=False)],
    attempts: Annotated[Path, typer.Option(exists=True, dir_okay=False)],
    expected_platform: Annotated[list[Platform], typer.Option()],
) -> None:
    """Explain whether sparse data means low visibility, access limits, or incomplete work."""
    media_target = MediaTarget.model_validate_json(target.read_text(encoding="utf-8"))
    assessment = diagnose_collection(
        target_id=media_target.target_id, posts=read_posts(input),
        attempts=read_attempts(attempts), expected_platforms=expected_platform,
    )
    typer.echo(assessment.model_dump_json(indent=2))


@app.command("media-compare-report")
def media_compare_report(
    spec: Annotated[Path, typer.Option(exists=True, dir_okay=False)],
    as_of: Annotated[str, typer.Option(help="YYYY-MM-DD")],
    output: Annotated[Path, typer.Option()] = Path("media-comparison-report.md"),
    audit_output: Annotated[Path, typer.Option()] = Path("media-report-audit.json"),
    rules: Annotated[Path | None, typer.Option(exists=True, dir_okay=False)] = None,
) -> None:
    """Generate and self-audit a reusable multi-school media heat report."""
    try:
        cutoff = date.fromisoformat(as_of)
    except ValueError as exc:
        raise typer.BadParameter("as-of must be YYYY-MM-DD") from exc
    audit = generate_comparison_report(
        spec_path=spec, as_of=cutoff, output=output, audit_output=audit_output,
        rules_path=rules or Path(__file__).resolve().parents[2] / "config" / "heat_rules.yaml",
    )
    typer.echo(json.dumps(audit, ensure_ascii=False, indent=2))
