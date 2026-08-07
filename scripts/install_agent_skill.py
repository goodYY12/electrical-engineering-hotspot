from __future__ import annotations

import argparse
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE = PROJECT_ROOT / "skills" / "electrical-kaoyan-navigator"


def default_destination(agent: str) -> Path:
    home = Path.home()
    if agent in {"claude-code", "workbuddy"}:
        return home / ".claude" / "skills"
    if agent == "codex":
        return home / ".agents" / "skills"
    raise ValueError("generic installs require --destination")


def install(destination: Path, *, force: bool = False) -> Path:
    target = destination.expanduser().resolve() / SOURCE.name
    if target.exists():
        if not force:
            raise FileExistsError(f"{target} already exists; use --force to replace it")
        shutil.rmtree(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(SOURCE, target, ignore=shutil.ignore_patterns("agents"))
    return target


def main() -> None:
    parser = argparse.ArgumentParser(description="Install the portable Agent Skill")
    parser.add_argument("--agent", choices=["codex", "claude-code", "workbuddy", "generic"],
                        default="generic")
    parser.add_argument("--destination", type=Path)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    destination = args.destination or default_destination(args.agent)
    print(install(destination, force=args.force))


if __name__ == "__main__":
    main()
