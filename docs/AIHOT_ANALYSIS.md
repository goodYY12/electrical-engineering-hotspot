# AIHOT 源码分析与 ElectroRadar 改造映射

分析基线：`KKKKhazix/AIHOT@7b6be438204c671c76ed8f6520e70aa4eaa7f038`（2026-10-06），MIT 许可；保留 `LICENSE` 与 `NOTICE`，ElectroRadar 使用独立名称与视觉标识。

## 1. 目录与技术栈

AIHOT 是 npm workspaces 单仓库：`apps/web` 为 React 19 + React Router 8 SSR + Tailwind 4，`apps/api` 为 Fastify，`apps/worker` 为 pg-boss 定时任务与队列，`packages/backend` 放业务逻辑，`packages/contracts` 放跨进程契约，`database/migrations` 管理 PostgreSQL 17，`site` 放品牌和站点文案，`industry` 放行业分类、信源、提示词与精选门槛。Docker Compose 启动 PostgreSQL、setup、API、worker、web，并可选 Caddy HTTPS。

## 2. 前后端与数据库

前端只通过 HTTP 读取 API，不接触数据库或模型密钥。API 提供站点接口、公开 API v1、RSS、MCP、后台、媒体代理和分享图。worker 负责采集、正文提取、AI 分析、事件归组、热度快照、报告、告警和清理。

核心数据链以 `sources → articles → analyses → publications → facts/stories → story_signals/hot_rankings → reports` 为主。迁移还覆盖付费请求回执、预算、任务运行、热度历史、反馈、会话、全文翻译和检索索引。发布迁移不可改写，新增变更使用新迁移。

## 3. 数据采集与 AI 流程

采集器原生支持 RSS/Atom、HTML 列表、JSON API、X 搜索、公众号和外部推送。抓取结果先做 URL 与内容身份判重，补齐正文与发布时间，再进入：行业预筛 → 两次独立评分 → 结构化分类/标签/主体/事实 → 标题摘要与推荐理由 → 事件归组与代表报道选择。模型只由 worker 调用；付费请求先写回执，并受分钟、小时、每日预算熔断保护。

ElectroRadar 复用这条链路，把行业包替换为电气工程词表、信源和专家提示词。AI HotScore 使用技术突破、产业影响、工程价值、市场关注四个等权维度；事件热度继续使用多来源参与、时间衰减和趋势比较，两者分别表示“专家重要性”和“公开讨论活跃度”。

## 4. 原热点算法

AIHOT 在 48 小时窗口内按独立参与方计数，同一机构多渠道合并；每个参与方只取窗口内最近信号，按 24 小时半衰期指数衰减。至少两个参与方且包含一个 editorial 来源才进入候选。榜单比较六小时前同一可比信源队列，输出 new/up/down/flat、来源数、参与者数与小时热度曲线。

## 5. 复用与改造范围

直接复用：单仓库结构、采集器、正文提取、判重、模型回执与预算、队列、事件归组、热点衰减、报告编排、API/RSS/MCP、管理后台、SSR 页面、Docker 和迁移体系。

重点改造：

1. `site/`：ElectroRadar 名称、文案、深色优先的科技蓝/电力橙/能源绿视觉。
2. `industry/`：电力系统、储能、新能源、电力电子、电机驱动、高压、控制、政策标准等分类；企业与机构词典；电气专家提示词；可验证的公共信源。
3. `modules/electrical-intelligence/`：技术雷达、专家分析输出和电气专属公开接口。
4. worker：保持每小时采集与分析，日报固定北京时间 08:00。
5. 数据：保留 AIHOT 主表，在模块迁移中增加电气专家分析与雷达快照，避免破坏上游升级路径。

## 6. 实施顺序

先完成品牌、行业包、信源与提示词，再增加专家分析字段和技术雷达模块，最后执行类型检查、数据库迁移检查、单元测试、web 构建和 Docker smoke test。条款与隐私模板在正式公开部署前由站点运营者确认。
