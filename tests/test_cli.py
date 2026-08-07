from typer.testing import CliRunner

import electrical_kaoyan.cli as cli_module
from electrical_kaoyan.cli import app

runner = CliRunner()


def test_cli_help_registers_all_commands():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "media-collect" in result.stdout
    assert "media-add" in result.stdout
    assert "media-heat" in result.stdout
    assert "media-log-attempt" in result.stdout
    assert "media-diagnose" in result.stdout


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
