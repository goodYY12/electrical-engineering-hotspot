# 高校科研雷达维护记录

## 当前目标

让高校科研数据沿用 ElectroRadar 原有采集、分析和公开读取链路，页面只展示真实数据库内容。模块不新增数据库表、不改变部署结构。

## 已完成

- 20 所高校 profile，包含中文名、英文别名、地区、学院和六类电气研究方向。
- 20 个 Crossref affiliation 数据源（P0）。重点高校另外配置学院官网科研动态源（P1）。
- 论文使用 DOI 作为外部身份，已有 URL 和内容哈希去重机制继续生效。
- analyzer 输出统一的 `universityRadar` 元数据，写入现有 `analyses.output` JSON：

```json
{
  "isUniversityResearch": true,
  "university": "南京师范大学",
  "department": "电气与自动化工程学院",
  "researchDirection": "新能源电力系统",
  "keywords": ["新能源", "储能"],
  "researchType": "论文",
  "graduationPossible": true,
  "graduationTopics": ["基于MATLAB的光伏储能系统能量管理策略研究"],
  "difficulty": "medium",
  "score": 86
}
```

- `/university-radar` 从真实数据库读取学校、地区、方向和科研动态。
- `/graduation-topics` 只根据真实高校条目生成推荐题目。
- Railway API 和 worker 已部署提交 `fb85ffc`；线上接口已验证返回南京师范大学和山东大学科研数据。

## 使用方式

打开 [高校科研雷达](https://electroradar.vercel.app/university-radar)，选择学校、地区或方向。学校卡片中的科研动态链接会进入文章详情；也可以直接打开 [高校雷达 API](https://electroradar-api-production.up.railway.app/api/university-radar) 查看当前数据库返回。

## 本地验证

```bash
npm run typecheck
npm test
npm run build -w @aihot/web
```

线上检查重点是确认 API 返回 `entries[].items`，且每个条目有文章 `id` 和 `title`。没有模型密钥时页面仍可打开；采集和 AI 分析需要在 worker 环境配置对应变量。

## 下一步扩展

新增高校只需在 `modules/university-radar/universities.ts` 增加 profile，并由 `sources.ts` 自动生成 Crossref source；不要复制 collector 或新建表。官网 P1 source 只对有稳定公开科研栏目且经过可访问性检查的学校增加。

## 部署记录

| 日期 | 提交 | 结果 |
|---|---|---|
| 2026-10-11 | `fb85ffc` | Railway API/worker 成功；高校雷达 API 返回真实数据；GitHub Web 与 Docker checks 通过 |

后续每次完成高校雷达相关工作，都在本文件的“部署记录”追加日期、提交和线上验证结果。
