import { Form, Link, useLoaderData, useSearchParams } from "react-router";
import { apiGet, cachedPage } from "@aihot/web/lib/api.server";
import { pageMeta } from "@aihot/web/lib/seo";
import type { UniversityRadarResponse } from "../server.ts";
import { filterUniversityEntries } from "../filter.ts";

export { pageHeaders as headers } from "@aihot/web/lib/api.server";
export async function loader({ request }: { request: Request }) { return cachedPage(300, { radar: await apiGet<UniversityRadarResponse>("/api/university-radar", { signal: request.signal }) }); }
export function meta() { return pageMeta({ title: "中国高校电气科研雷达", description: "追踪中国高校电气工程科研动态，并生成适合本科毕业设计的研究方向。", path: "/university-radar" }); }

export default function UniversityRadarPage() {
  const { radar } = useLoaderData<typeof loader>();
  const [params] = useSearchParams();
  const filters = { university: params.get("university"), region: params.get("region"), direction: params.get("direction") };
  const entries = filterUniversityEntries(radar.entries, filters);
  const universities = radar.entries.map((entry) => entry.university).sort((a, b) => a.localeCompare(b, "zh-CN"));
  const regions = [...new Set(radar.entries.map((entry) => entry.region))].sort((a, b) => a.localeCompare(b, "zh-CN"));
  const directions = [...new Set(radar.entries.flatMap((entry) => entry.researchDirections.flatMap((direction) => direction.split("、"))))].sort((a, b) => a.localeCompare(b, "zh-CN"));
  const selectClass = "rounded-lg border border-line bg-surface px-3 py-2 text-[12px] text-ink";

  return <main className="mx-auto max-w-[var(--page-max)] pb-14 pt-2 lg:pt-0">
    <header className="mb-5 border-b border-line pb-5"><p className="text-[12px] font-semibold uppercase tracking-[0.16em] text-accent">University Research Radar</p><h1 className="mt-2 text-[25px] font-bold tracking-[-0.02em] text-ink sm:text-[30px]">中国高校电气科研雷达</h1><p className="mt-2 max-w-3xl text-[13.5px] leading-7 text-ink-3">展示已配置高校的科研板块；文章和数量只来自真实数据库，尚未采集到的学校会标记为待采集。</p></header>
    <section className="card mb-5 p-5"><div className="flex items-end justify-between"><div><p className="text-[12px] text-ink-4">已识别高校科研</p><p className="mt-1 text-[32px] font-semibold text-ink">{radar.totalArticles}<span className="ml-1 text-[14px] font-normal text-ink-4">条</span></p></div><span className="mono text-[11px] text-ink-4">{new Date(radar.generatedAt).toLocaleString("zh-CN", { hour12: false })}</span></div></section>
    <Form method="get" className="card mb-5 flex flex-wrap items-end gap-3 p-4">
      <label className="grid gap-1 text-[11px] text-ink-4">学校<select name="university" defaultValue={filters.university ?? ""} className={selectClass}><option value="">全部学校</option>{universities.map((university) => <option key={university}>{university}</option>)}</select></label>
      <label className="grid gap-1 text-[11px] text-ink-4">地区<select name="region" defaultValue={filters.region ?? ""} className={selectClass}><option value="">全部地区</option>{regions.map((region) => <option key={region}>{region}</option>)}</select></label>
      <label className="grid gap-1 text-[11px] text-ink-4">方向<select name="direction" defaultValue={filters.direction ?? ""} className={selectClass}><option value="">全部方向</option>{directions.map((direction) => <option key={direction}>{direction}</option>)}</select></label>
      <button type="submit" className="rounded-lg bg-accent px-4 py-2 text-[12px] font-semibold text-white">筛选</button>
      {(filters.university || filters.region || filters.direction) && <Link to="/university-radar" className="px-2 py-2 text-[12px] text-ink-4 hover:text-accent">清除</Link>}
    </Form>
    {entries.length === 0 ? <section className="card p-8 text-center text-[13px] text-ink-4">当前筛选条件下还没有已入库科研动态。</section> : <section className="grid gap-4 sm:grid-cols-2">{entries.map((entry) => <article key={entry.university} className="card p-5">
      <div className="flex items-start justify-between gap-3"><div><h2 className="text-[16px] font-semibold text-ink">{entry.university}</h2><p className="mt-1 text-[12px] text-ink-4">{entry.region} · {entry.department}</p></div><span className="mono rounded-full bg-surface-2 px-2 py-1 text-[12px] text-accent">{entry.articleCount} 条</span></div>
      <div className="mt-4 flex flex-wrap gap-2">{entry.researchDirections.map((direction) => <span key={direction} className="rounded-full border border-line px-2.5 py-1 text-[11px] text-ink-3">{direction}</span>)}</div>
      <div className="mt-4 border-t border-line-soft pt-3"><p className="text-[11px] font-semibold text-ink-4">科研动态</p>{entry.items.length > 0 ? <div className="mt-2 space-y-2">{entry.items.slice(0, 6).map((item) => <Link key={item.id} to={`/items/${item.id}`} className="block text-[12px] leading-5 text-ink-2 hover:text-accent">{item.title}<span className="mt-0.5 block text-[10px] text-ink-4">{item.source}</span></Link>)}</div> : <p className="mt-2 text-[12px] text-ink-4">待采集真实科研动态</p>}</div>
      {entry.graduationTopics.length > 0 && <div className="mt-4 border-t border-line-soft pt-3"><p className="text-[11px] font-semibold text-ink-4">推荐毕设方向</p><p className="mt-1 text-[12px] leading-6 text-ink-3">{entry.graduationTopics[0]}</p><Link to={`/graduation-topics?university=${encodeURIComponent(entry.university)}`} className="mt-2 inline-flex text-[12px] font-semibold text-accent hover:underline">查看毕设推荐 →</Link></div>}
    </article>)}</section>}
  </main>;
}
