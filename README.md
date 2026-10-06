# ElectroRadar（电气工程智能热点雷达）

ElectroRadar 是一个面向电气工程师、科研人员和行业决策者的实时技术情报系统。它持续采集全球论文、行业新闻、政策标准和企业动态，经过 AI 筛选、专业分析、事件聚合与热度计算，回答一个问题：**今天电气行业最重要的技术变化是什么？**

本项目基于 [AIHOT](https://github.com/KKKKhazix/AIHOT) 二次开发，保留其成熟的数据流、事件聚合、热点计算、日报和公开 API，并通过行业包与独立模块扩展为电气工程版本。上游分析见 [docs/AIHOT_ANALYSIS.md](docs/AIHOT_ANALYSIS.md)。

## 已实现

- Dashboard：每日精选、今日热点 Top 10、AI 摘要与推荐理由。
- 实时热点：48 小时事件热榜、趋势、来源数量和参与者。
- 技术雷达：电力系统、智能电网、新能源、储能、电力电子、电机驱动、高压输电、控制系统、标准政策、产业动态。
- 行业日报：北京时间每天 08:00 自动生成，另有周报和月报。
- 搜索与主题：按关键词、时间、类别、标签和公司检索。
- AI 电气专家：输出技术背景、工程影响、产业影响、相关公司、相关技术、HotScore 与置信度。
- 自动任务：信源按小时至少检查一次；自动清洗、去重、分析、事件聚合、热度快照和成刊。
- Agent 接入：公开 API、RSS、MCP、Agent Markdown 和 `llms.txt`。

## 数据源

默认配置只使用无需密钥且已验证可访问的公开接口，包括 IEEE Spectrum、美国能源部、Federal Register、GE Vernova、arXiv、Crossref（IEEE、ScienceDirect、Springer）、Power Electronics News、Energy-Storage.news、ESS News、pv magazine、PV Tech、POWER Magazine、Utility Dive 和 Renewable Energy World。

付费、登录或授权受限的数据源应通过 `external` 推送或独立连接器接入。默认不绕过网站访问控制，也不会把抓取失败伪装成“没有热点”。

## 技术架构

| 层 | 技术 |
|---|---|
| Web | React 19、React Router 8 SSR、Tailwind CSS 4 |
| API | Fastify、TypeScript |
| Worker | pg-boss、Cron |
| 数据 | PostgreSQL 17、顺序迁移 |
| AI | OpenAI 兼容接口，可按步骤选择不同模型 |
| 部署 | Docker Compose、可选 Caddy HTTPS |

数据流：

```text
公开信源 → 采集 → 规范化与去重 → AI 预筛 → 两次独立评分
        → 电气专家结构化分析 → 事件聚合 → 热榜/技术雷达 → 日报与公开 API
```

文章的专业 `HotScore` 由四个等权维度组成：技术突破、产业影响、工程价值、市场关注。事件热榜按独立参与来源、时间衰减和讨论增量计算，两者含义不同。

## 快速启动

需要 Docker（含 Compose）和一个 OpenAI 兼容的模型 API Key。

```bash
git clone https://github.com/goodYY12/electrical-engineering-hotspot.git
cd electrical-engineering-hotspot
cp .env.example .env
```

编辑 `.env`，至少填写：

```dotenv
ADMIN_PASSWORD=至少12位密码
SESSION_SECRET=随机长字符串
IMG_PROXY_SIGN_SECRET=随机长字符串
POSTGRES_PASSWORD=随机长字符串
LLM_API_KEY=你的模型密钥
```

启动：

```bash
docker compose up -d --build
```

访问：

- 网站：<http://localhost:3000>
- 技术雷达：<http://localhost:3000/radar>
- 后台：<http://localhost:3000/admin>
- 健康检查：<http://localhost:3000/api/health>

首次启动会执行数据库迁移、导入默认信源并开始采集。模型处理速度取决于供应商限速和首批数据量。

如果本机代理使用 Fake IP（域名被解析到 `198.18.0.0/15`），安全抓取层会将其视为保留地址。开发环境可以在 `.env` 设置 `ALLOW_PRIVATE_NETWORK_FETCH=true`；生产环境请配置 `EGRESS_PROXY_URL`，不要关闭公网地址校验。可用 `npm run sources:check` 直接检查每个默认信源。

## 本地开发

需要 Node.js 24.11+ 和 PostgreSQL 17。

```bash
npm ci
npm run db:migrate
node scripts/seed.ts
npm run dev:api
npm run dev:worker
npm run dev:web
```

三个开发进程分别监听 API、后台任务和网页。数据库与 API 地址在 `.env` 中配置。

## 验证

```bash
npm run typecheck
npm run sources:check
npm run test:standalone
npm test
npm run build -w @aihot/web
node scripts/smoke.ts --base http://localhost:3000
```

## 关键目录

```text
apps/web/                         React Router SSR 前端
apps/api/                         Fastify API
apps/worker/                      采集与定时任务
packages/backend/                数据、AI、事件、热点、报告核心
packages/contracts/              前后端共享类型
industry/                        电气分类、主题、信源、提示词和阈值
site/                            ElectroRadar 品牌、文案与模块注册
modules/electrical-intelligence/ 技术雷达 API、页面、小时快照和迁移
database/migrations/             AIHOT 核心数据库迁移
docs/                            架构、部署与运维说明
```

## 配置与部署

- 完整环境变量见 [.env.example](.env.example)。
- Docker、域名、HTTPS、代理、备份和非 Docker 部署见 [docs/deploy.md](docs/deploy.md)。
- 信源格式与采集规则见 [docs/sources.md](docs/sources.md)。
- AI 评分与校准见 [docs/selection.md](docs/selection.md)。

`AIHOT_*` 环境变量名属于兼容上游的内部接口，项目品牌与公开页面均使用 ElectroRadar。

## 许可与署名

代码遵循 [MIT License](LICENSE)。本项目保留 AIHOT 的版权和 [NOTICE](NOTICE)；AIHOT 名称与 Logo 不属于 MIT 授权范围，ElectroRadar 使用独立名称与界面品牌。各数据源内容版权归原发布者，网站默认只展示摘要和原文链接。
