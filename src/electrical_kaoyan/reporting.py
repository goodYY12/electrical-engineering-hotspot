from __future__ import annotations

from datetime import UTC, date, datetime
from pathlib import Path

from .models import DataQualityIssue, EvidenceConflict, ProgramIdentity


def render_skeleton(program: ProgramIdentity, *, conflicts: list[EvidenceConflict],
                    issues: list[DataQualityIssue], cutoff: date | None = None) -> str:
    cutoff = cutoff or datetime.now(UTC).date()
    conflict_lines = "\n".join(f"- {c.field_path}: {c.status} ({c.conflict_id})" for c in conflicts) or "- 无"
    issue_lines = "\n".join(f"- [{i.severity}] {i.message}" for i in issues) or "- 无"
    return f"""# {program.school} {program.college} {program.major_code} 研究报告

- 数据截止日期：{cutoff.isoformat()}
- Program ID：`{program.program_id}`
- 招生年份：{program.admission_year}

## 【官方事实】

尚未录入可验证事实。

## 【计算结果】

尚无可计算的同口径数据。

## 【社区观察】

未启用或尚未录入。社区信息不作为官方事实。

## 【分析判断】

当前证据不足，无法给出可靠冲稳保定位。

## 【不确定项】

### 来源冲突

{conflict_lines}

### 数据质量问题

{issue_lines}

## 核心来源

详见 `evidence.json`。所有关键数字必须引用 Evidence ID。
"""


def write_markdown(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
