from typer.testing import CliRunner

from electrical_kaoyan.cli import app

runner = CliRunner()


def test_cli_help_registers_all_commands():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "media-collect" in result.stdout
    assert "media-add" in result.stdout
    assert "media-heat" in result.stdout


def test_media_heat_rejects_invalid_date(tmp_path):
    target = tmp_path / "target.json"
    target.write_text('{"school":"重庆大学","major_code":"085801"}', encoding="utf-8")
    media = tmp_path / "media.jsonl"
    media.write_text("", encoding="utf-8")
    result = runner.invoke(app, ["media-heat", "--input", str(media), "--target", str(target),
                                 "--as-of", "not-a-date"])
    assert result.exit_code != 0
    assert "YYYY-MM-DD" in result.output
