from typer.testing import CliRunner

import electrical_kaoyan.cli as cli_module
from electrical_kaoyan.cli import app
from electrical_kaoyan.fetchers.http import FetchResult

runner = CliRunner()


def test_research_reports_when_live_discovery_has_not_run(tmp_path):
    result = runner.invoke(app, [
        "research", "--school", "重庆大学", "--college", "电气工程学院",
        "--major", "085801", "--admission-year", "2027", "--output", str(tmp_path),
    ])
    assert result.exit_code == 0, result.output
    case = next(tmp_path.iterdir())
    acquisition = __import__("json").loads((case / "acquisition.json").read_text(encoding="utf-8"))
    assert acquisition["status"] == "discovery_required"
    assert acquisition["fetched"] == []


def test_research_fetches_supplied_live_url_with_refresh(tmp_path, monkeypatch):
    calls = []

    def fetched(self, url, *, refresh=False):
        calls.append((url, refresh))
        raw = tmp_path / "notice.html"
        raw.write_text("招生公告", encoding="utf-8")
        return FetchResult(
            canonical_url=url, status_code=200, media_type="text/html",
            accessed_at="2026-10-05T00:00:00+00:00", content_hash="a" * 64,
            raw_path=str(raw), from_cache=False,
        )

    monkeypatch.setattr(cli_module.CachedHttpFetcher, "fetch", fetched)
    result = runner.invoke(app, [
        "research", "--school", "重庆大学", "--college", "电气工程学院",
        "--major", "085801", "--admission-year", "2027", "--output", str(tmp_path / "runs"),
        "--source-url", "https://example.edu.cn/current", "--refresh",
    ])
    assert result.exit_code == 0, result.output
    case = next((tmp_path / "runs").iterdir())
    acquisition = __import__("json").loads((case / "acquisition.json").read_text(encoding="utf-8"))
    assert acquisition["status"] == "archived"
    assert len(acquisition["fetched"]) == 1
    assert calls == [("https://example.edu.cn/current", True)]


def test_cli_help_registers_all_commands():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "media-collect" in result.stdout
    assert "media-add" in result.stdout
    assert "media-heat" in result.stdout
    assert "media-log-attempt" in result.stdout
    assert "media-diagnose" in result.stdout
    assert "media-compare-report" in result.stdout
    assert "hotspot-web" in result.stdout


def test_media_heat_rejects_invalid_date(tmp_path):
    target = tmp_path / "target.json"
    target.write_text('{"school":"重庆大学","major_code":"085801"}', encoding="utf-8")
    media = tmp_path / "media.jsonl"
    media.write_text("", encoding="utf-8")
    result = runner.invoke(app, ["media-heat", "--input", str(media), "--target", str(target),
                                 "--as-of", "not-a-date"])
    assert result.exit_code != 0
    assert "YYYY-MM-DD" in result.output


def test_media_heat_writes_evidence_ledger(tmp_path):
    target = tmp_path / "target.json"
    target.write_text('{"school":"重庆大学","major_code":"085801"}', encoding="utf-8")
    media = tmp_path / "media.jsonl"
    media.write_text("", encoding="utf-8")
    evidence = tmp_path / "media-evidence.json"
    result = runner.invoke(app, [
        "media-heat", "--input", str(media), "--target", str(target),
        "--as-of", "2026-08-08", "--evidence-output", str(evidence),
    ])
    assert result.exit_code == 0
    payload = __import__("json").loads(evidence.read_text(encoding="utf-8"))
    assert payload["target"]["school"] == "重庆大学"
    assert payload["rules_sha256"]
    assert payload["observations"] == []


def test_media_collect_logs_access_failure(tmp_path, monkeypatch):
    target = tmp_path / "target.json"
    target.write_text('{"school":"南京师范大学","major_code":"085801"}', encoding="utf-8")
    attempts = tmp_path / "search-log.jsonl"

    def blocked(**kwargs):
        del kwargs
        raise RuntimeError("403 access denied")

    monkeypatch.setattr(cli_module, "collect_public_url", blocked)
    result = runner.invoke(app, [
        "media-collect", "--target", str(target), "--url", "https://www.bilibili.com/video/x",
        "--attempt-log", str(attempts),
    ])
    assert result.exit_code != 0
    assert '"outcome":"access_limited"' in attempts.read_text(encoding="utf-8")


def test_media_compare_report_self_audits_sparse_data(tmp_path):
    target = tmp_path / "target.json"
    target.write_text('{"school":"南京师范大学","major_code":"085801"}', encoding="utf-8")
    media = tmp_path / "media.jsonl"
    media.write_text("", encoding="utf-8")
    attempts = tmp_path / "attempts.jsonl"
    attempts.write_text("", encoding="utf-8")
    spec = tmp_path / "spec.json"
    spec.write_text(__import__("json").dumps({
        "title": "测试报告",
        "expected_platforms": ["xiaohongshu"],
        "targets": [{
            "name": "南京师范大学",
            "target": "target.json", "media": "media.jsonl", "attempts": "attempts.jsonl",
            "evidence": "evidence.json",
        }],
    }, ensure_ascii=False), encoding="utf-8")
    report = tmp_path / "report.md"
    audit = tmp_path / "audit.json"
    result = runner.invoke(app, [
        "media-compare-report", "--spec", str(spec), "--as-of", "2026-08-08",
        "--output", str(report), "--audit-output", str(audit),
    ])
    assert result.exit_code == 0, result.output
    payload = __import__("json").loads(audit.read_text(encoding="utf-8"))
    assert payload["integrity_status"] == "pass"
    assert payload["data_readiness"] == "incomplete"
    assert payload["rankable"] is False
    assert "不能可靠排序" in report.read_text(encoding="utf-8")
