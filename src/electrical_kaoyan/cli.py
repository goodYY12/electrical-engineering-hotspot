from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path
from typing import Annotated

import typer

from .evidence import EvidenceLedger
from .media import (
    append_post,
    collect_public_url,
    post_from_observation,
    read_posts,
    write_media_evidence,
)
from .models import DegreeType, ProgramIdentity, StudyMode
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
) -> None:
    """Collect one public media page without bypassing access controls."""
    media_target = MediaTarget.model_validate_json(target.read_text(encoding="utf-8"))
    post = collect_public_url(url=url, target=media_target, output=output, cache=cache,
                              rules=load_heat_rules(rules), query=query, refresh=refresh)
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
    extraction_method: Annotated[str, typer.Option()] = "agent_browser",
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
    )
    append_post(output, post)
    typer.echo(post.model_dump_json(indent=2))


@app.command("media-heat")
def media_heat(
    input: Annotated[Path, typer.Option(exists=True, dir_okay=False)],
    target: Annotated[Path, typer.Option(exists=True, dir_okay=False)],
    as_of: Annotated[str, typer.Option(help="YYYY-MM-DD")],
    expected_platform: Annotated[list[Platform] | None, typer.Option()] = None,
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
    report = analyze_heat(posts, target_id=media_target.target_id, as_of=cutoff,
                          expected_platforms=expected_platform or [], rules=heat_rules)
    write_media_evidence(path=evidence_output, target=media_target, posts=posts,
                         report=report, rules=heat_rules)
    rendered = report.model_dump_json(indent=2)
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    typer.echo(f"Evidence: {evidence_output.resolve()}", err=True)
    typer.echo(rendered)
