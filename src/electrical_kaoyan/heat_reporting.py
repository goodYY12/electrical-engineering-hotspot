from __future__ import annotations

import json
import os
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

from .collection import diagnose_collection, eligible_for_heat, read_attempts
from .media import read_posts, write_media_evidence
from .social import MediaTarget, Platform, analyze_heat, deduplicate_posts, load_heat_rules


def _resolve(base: Path, raw: str) -> Path:
    path = Path(raw)
    return (path if path.is_absolute() else base / path).resolve()


def _label(value: str) -> str:
    return {
        "insufficient_data": "数据不足", "very_low": "很低", "low": "低",
        "medium": "中等", "high": "高", "very_high": "很高",
        "unknown": "未知", "rising": "上升", "stable": "稳定", "falling": "下降",
        "low": "低", "medium": "中", "high": "高",
    }.get(value, value)


def generate_comparison_report(*, spec_path: Path, as_of: date, output: Path,
                               audit_output: Path, rules_path: Path) -> dict:
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    base = spec_path.parent
    rules = load_heat_rules(rules_path)
    expected = [Platform(item) for item in spec.get(
        "expected_platforms", ["xiaohongshu", "zhihu", "bilibili", "wechat"]
    )]
    cases = []
    findings: list[dict] = []
    for item in spec["targets"]:
        target_path = _resolve(base, item["target"])
        media_path = _resolve(base, item["media"])
        attempts_path = _resolve(base, item["attempts"])
        evidence_path = _resolve(base, item.get("evidence", f"{item['name']}-media-evidence.json"))
        target = MediaTarget.model_validate_json(target_path.read_text(encoding="utf-8"))
        posts = read_posts(media_path)
        attempts = read_attempts(attempts_path)
        heat = analyze_heat(posts, target_id=target.target_id, as_of=as_of,
                            expected_platforms=expected, rules=rules)
        assessment = diagnose_collection(target_id=target.target_id, posts=posts,
                                         attempts=attempts, expected_platforms=expected)
        write_media_evidence(path=evidence_path, target=target, posts=posts, report=heat,
                             rules=rules, attempts=attempts, assessment=assessment)
        evidence_payload = json.loads(evidence_path.read_text(encoding="utf-8"))
        if evidence_payload.get("target") != target.model_dump(mode="json"):
            findings.append({"severity": "error", "target": item["name"],
                             "code": "evidence_target_mismatch"})
        if evidence_payload.get("report") != heat.model_dump(mode="json"):
            findings.append({"severity": "error", "target": item["name"],
                             "code": "evidence_report_mismatch"})
        unique = [post for post in deduplicate_posts(posts) if post.duplicate_of is None]
        eligible = [post for post in unique if eligible_for_heat(post)]
        segments = Counter(post.audience_segment for post in eligible)
        categories = Counter(post.content_category for post in eligible)
        keywords = Counter(marker for post in eligible for marker in post.intent_markers)
        cases.append({
            "name": item["name"], "target": target, "heat": heat,
            "assessment": assessment, "segments": segments, "categories": categories,
            "keywords": keywords, "evidence": evidence_path,
        })
        if assessment.status != "adequate":
            findings.append({"severity": "warning", "target": item["name"],
                             "code": "data_not_adequate", "detail": assessment.status})
        xhs = next((p for p in assessment.platforms if p.platform == Platform.XIAOHONGSHU), None)
        if not xhs or xhs.status != "adequate":
            findings.append({"severity": "warning", "target": item["name"],
                             "code": "xiaohongshu_not_adequate",
                             "detail": xhs.status if xhs else "missing"})

    window = int(rules.get("observation_window_days", 90))
    lines = [
        f"# {spec.get('title', '公开媒体热度比较报告')}", "",
        f"- 截止日期：{as_of.isoformat()}",
        f"- 观察窗口：{(as_of - timedelta(days=window - 1)).isoformat()} 至 {as_of.isoformat()}（{window}天）",
        "- 边界：热度表示可观察的关注与意向，不代表报名人数、报录比或录取概率。", "",
        "## 一眼结论", "",
        "| 对象 | 热度 | 趋势 | 置信度 | 自然讨论 | 机构内容 | 代理证据 | 平台覆盖 | 采集诊断 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for case in cases:
        h, a = case["heat"], case["assessment"]
        lines.append(
            f"| {case['name']} | {_label(h.heat_level)} | {_label(h.momentum)} | {_label(h.confidence)} "
            f"| {h.organic_posts} | {h.commercial_posts} | {h.proxy_posts} "
            f"| {h.platform_coverage:.0%} | {a.status} |"
        )
    rankable = all(case["heat"].heat_level != "insufficient_data" for case in cases)
    lines += ["", "## 【分析判断】二次择校", ""]
    if rankable:
        ordered = sorted(cases, key=lambda case: case["heat"].organic_signal, reverse=True)
        lines.append(
            f"当前可观察自然关注信号较强的是{ordered[0]['name']}；这只触发重新评估，不能直接推出更难考或应当换校。"
        )
    else:
        lines.append(
            "至少一个对象缺少足够的独立自然讨论，当前不能可靠排序。不要因为机构曝光或搜索摘要单独二次择校。"
        )
    lines += ["", "## 【社区观察】用户群体、主题与关键词", ""]
    for case in cases:
        segment_text = "、".join(f"{k}:{v}" for k, v in case["segments"].most_common()) or "无正式样本"
        category_text = "、".join(f"{k}:{v}" for k, v in case["categories"].most_common()) or "无正式样本"
        keyword_text = "、".join(f"{k}:{v}" for k, v in case["keywords"].most_common(10)) or "无"
        lines += [f"### {case['name']}", "", f"- 用户群体：{segment_text}",
                  f"- 内容主题：{category_text}", f"- 意向关键词：{keyword_text}", ""]
    lines += ["## 【不确定项】数据完整性", ""]
    for case in cases:
        lines.append(f"- {case['name']}：{case['assessment'].status}；"
                     f"正式样本{case['assessment'].eligible_observations}条，"
                     f"代理样本{case['assessment'].proxy_observations}条。")
    lines += ["", "## 证据文件", ""]
    for case in cases:
        relative_evidence = os.path.relpath(case["evidence"], output.resolve().parent)
        lines.append(f"- {case['name']}：`{relative_evidence}`")
    lines += ["", "## 自检结论", "",
              "报告结构与计算可复核；数据是否足以排名由审计文件中的 `data_readiness` 单独表示。",
              f"审计文件：`{os.path.relpath(audit_output.resolve(), output.resolve().parent)}`"]
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")

    required_sections = ["一眼结论", "二次择校", "用户群体", "数据完整性", "证据文件", "自检结论"]
    rendered = output.read_text(encoding="utf-8")
    structural_errors = [name for name in required_sections if name not in rendered]
    evidence_errors = [
        f"missing evidence: {case['evidence']}" for case in cases if not case["evidence"].exists()
    ]
    content_errors = [item for item in findings if item["severity"] == "error"]
    integrity_errors = structural_errors + evidence_errors + [item["code"] for item in content_errors]
    audit = {
        "schema_version": "1.0", "as_of": as_of.isoformat(),
        "report": str(output.resolve()),
        "audit": str(audit_output.resolve()),
        "integrity_status": "pass" if not integrity_errors else "fail",
        "data_readiness": "adequate" if not findings else "incomplete",
        "rankable": rankable,
        "integrity_errors": integrity_errors,
        "structural_errors": structural_errors,
        "findings": findings,
        "boundaries_verified": all(term in rendered for term in ["不代表报名人数", "不能可靠排序"])
            if not rankable else "不代表报名人数" in rendered,
    }
    audit_output.parent.mkdir(parents=True, exist_ok=True)
    audit_output.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    return audit
