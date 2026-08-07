from pathlib import Path

import yaml

from scripts.install_agent_skill import SOURCE, install


def frontmatter(path: Path) -> dict:
    content = path.read_text(encoding="utf-8")
    _, block, _ = content.split("---", 2)
    return yaml.safe_load(block)


def test_canonical_skill_uses_only_open_spec_frontmatter():
    metadata = frontmatter(SOURCE / "SKILL.md")
    assert set(metadata) <= {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
    assert metadata["name"] == "electrical-kaoyan-navigator"


def test_claude_adapter_points_to_canonical_skill():
    adapter = Path(".claude/skills/electrical-kaoyan-navigator/SKILL.md")
    assert adapter.exists()
    assert "skills/electrical-kaoyan-navigator/SKILL.md" in adapter.read_text(encoding="utf-8")


def test_generic_installer_copies_complete_skill(tmp_path):
    target = install(tmp_path)
    assert (target / "SKILL.md").exists()
    assert (target / "references" / "heat-methodology.md").exists()
    assert (target / "references" / "collection-recovery.md").exists()
    assert not (target / "agents").exists()
