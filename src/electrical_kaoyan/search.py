from __future__ import annotations

INTENTS = (
    "招生目录", "考试大纲", "推免", "复试细则", "复试名单", "拟录取",
    "调剂", "就业质量报告", "专业课调整",
)


def generate_queries(school: str, college: str, major_code: str, admission_year: int,
                     official_domain: str | None = None) -> list[str]:
    prefix = f"site:{official_domain} " if official_domain else ""
    targets = {f"{school} {college}", f"{school} {major_code}"}
    return [f"{prefix}{target} {admission_year} {intent}" for target in sorted(targets)
            for intent in INTENTS]
