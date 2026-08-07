# 电气考研择校与考情分析

这是一个面向中国大陆电气工程考研的证据驱动研究工具。它把公开信息保存为可复核证据，再完成招生实体对齐、名额拆分、拟录取统计、专业课变化、风险画像和个性化冲稳保分析。

它也提供报名前的公开媒体热度参考：通过独立作者、跨日持续性、择校意图、互动、时间衰减、重复内容和营销特征，输出近似热度、趋势和置信度。热度不是报名人数，也不用于伪造录取概率。

当前项目同时提供：

- 通用 Skill 内容：`skills/electrical-kaoyan-navigator/`，遵循开放 Agent Skills 规范。
- Codex 当前推荐的可安装形式：根目录的 skills-only plugin 清单 `.codex-plugin/plugin.json`。
- Claude Code 与 WorkBuddy：`.claude/skills/electrical-kaoyan-navigator/` 路由到同一份通用 Skill。
- 可独立执行的 Python 包：`src/electrical_kaoyan/`。

## 边界

本系统提供数据整理和决策辅助，招生政策以教育部、研招网和目标院校最终公告为准。社媒只作为弱信号。由于不存在完整、同口径的考生总体样本，系统不输出虚假的录取概率。未知值不会填成 0；冲突不会静默覆盖；关键数字应能沿 Evidence ID 回到原始来源。

## 开发与安装

```text
python -m venv .venv
.venv/Scripts/python -m pip install -e ".[dev,pdf]"
python -m pytest
```

仓库内启动 Codex 时，Skill 可从 `.agents/skills/` 被发现。用于分发时，将本仓库作为本地 plugin/marketplace 源安装；插件清单直接引用同一份 Skill，避免内容漂移。若宿主未立即显示变更，刷新或重启 Codex。

## 使用

```text
python -m electrical_kaoyan research --school "重庆大学" --college "电气工程学院" --major 085801 --admission-year 2027 --years 5 --official-only --export markdown
python -m electrical_kaoyan research --school "华北电力大学" --college "电气与电子工程学院" --major 080800 --admission-year 2027 --include-social --refresh --export json
python -m electrical_kaoyan compare --case runs/cqu-085801-2027 --case runs/ncepu-080800-2027 --profile profile.json
```

### 报名前媒体热度

先创建目标文件：

```json
{
  "school": "重庆大学",
  "college": "电气工程学院",
  "major_code": "085801",
  "admission_year": 2027
}
```

由 Agent 使用公开网页搜索发现帖子 URL 后，逐条归档；不得绕过登录、验证码或访问控制：

```text
python -m electrical_kaoyan media-collect --target target.json --url "公开页面URL" --output media.jsonl
python -m electrical_kaoyan media-add --target target.json --platform xiaohongshu --url "公开页面URL" --title "页面标题" --text "Agent在公开页面看到的正文摘要" --author-id "匿名作者ID" --likes 20 --collects 8 --comments 3 --output media.jsonl
python -m electrical_kaoyan media-heat --target target.json --input media.jsonl --as-of 2026-08-08 --expected-platform zhihu --expected-platform xiaohongshu --expected-platform bilibili --output heat.json --evidence-output media-evidence.json
```

结果同时显示自然讨论、商业内容、重复率、独立作者、平台覆盖、时间窗口、趋势和置信度。缺失的平台不会被当作零热度；`media-evidence.json` 保存目标、规则哈希、完整观察和去重关系，便于复核。

仓库提供合成示例（不代表真实院校热度）：

```text
python -m electrical_kaoyan media-heat --target examples/target.json --input examples/media-sample.jsonl --as-of 2026-08-08 --expected-platform zhihu --expected-platform xiaohongshu --expected-platform bilibili
```

## 跨 Agent 安装

仓库克隆后，Codex 和 Claude Code/WorkBuddy 可以直接识别各自的项目级入口。安装到个人目录：

```text
python scripts/install_agent_skill.py --agent codex
python scripts/install_agent_skill.py --agent claude-code
python scripts/install_agent_skill.py --agent workbuddy
python scripts/install_agent_skill.py --agent generic --destination "/your/agent/skills"
```

其他支持开放 Agent Skills 规范的工具可直接复制 `skills/electrical-kaoyan-navigator`。不支持自动发现的 Agent 仍可读取该目录中的 `SKILL.md`，并在项目根目录运行 Python CLI。

Claude Code 的项目 Skill 入口是 `.claude/skills/`；WorkBuddy 建立在 Claude Code 之上，因此使用同一入口。Codex 使用 `.agents/skills/`，插件安装则使用根目录 `skills/`。这些入口只负责发现，所有研究规则都指向同一个开放标准 Skill。

## 数据与合规边界

- 只读取公开可访问页面，不绕过登录、验证码、付费墙、访问控制或反爬保护。
- 动态页面可由 Agent 浏览器读取后通过 `media-add` 结构化记录；用户导出的公开内容也可采用同一路径。
- 不永久保存真实姓名；作者 ID 应匿名化。
- 热度只描述可观察公开样本中的注意力，不能推导真实报名人数、报录比、分数线或录取概率。
- 比较院校热度时必须采用相同观察窗口、平台集合和查询协议；否则只并列展示，不作机械排名。

每个研究目录至少包含 `evidence.json`、研究数据库、抓取归档、质量问题和报告。实时网页会变化；可复现测试使用固定 fixture，联网验证另以 `live` 标记。

更完整的设计依据见 `architecture.md`。本项目没有 Fork 或复制通用参考仓库；其局限与本项目的结构性差异也记录在该文件中。
