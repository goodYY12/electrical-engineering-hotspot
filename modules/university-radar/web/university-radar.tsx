import { useLoaderData } from "react-router";
import { apiGet, cachedPage } from "@aihot/web/lib/api.server";
import { pageMeta } from "@aihot/web/lib/seo";
import type { UniversityRadarResponse } from "../server.ts";

export { pageHeaders as headers } from "@aihot/web/lib/api.server";
export async function loader({ request }: { request: Request }) { return cachedPage(300, { radar: await apiGet<UniversityRadarResponse>("/api/university-radar", { signal: request.signal }) }); }
export function meta() { return pageMeta({ title: "中国高校电气科研雷达", description: "追踪中国高校电气工程科研动态，并生成适合本科毕业设计的研究方向。", path: "/university-radar" }); }

export default function UniversityRadarPage() {
  const { radar } = useLoaderData<typeof loader>();
  return <main className="mx-auto max-w-[var(--page-max)] pb-14 pt-2 lg:pt-0">
    <header className="mb-5 border-b border-line pb-5"><p className="text-[12px] font-semibold uppercase tracking-[0.16em] text-accent">University Research Radar</p><h1 className="mt-2 text-[25px] font-bold tracking-[-0.02em] text-ink sm:text-[30px]">中国高校电气科研雷达</h1><p className="mt-2 max-w-3xl text-[13.5px] leading-7 text-ink-3">从公开高校科研动态中识别研究方向，并把有足够证据的方向转成可落地的本科毕业设计选题。</p></header>
    <section className="card mb-5 p-5"><div className="flex items-end justify-between"><div><p className="text-[12px] text-ink-4">今日识别高校科研</p><p className="mt-1 text-[32px] font-semibold text-ink">{radar.totalArticles}<span className="ml-1 text-[14px] font-normal text-ink-4">条</span></p></div><span className="mono text-[11px] text-ink-4">{new Date(radar.generatedAt).toLocaleString("zh-CN", { hour12: false })}</span></div></section>
    <section className="grid gap-4 sm:grid-cols-2">{radar.entries.map((entry) => <article key={entry.university} className="card p-5"><div className="flex items-start justify-between gap-3"><div><h2 className="text-[16px] font-semibold text-ink">{entry.university}</h2><p className="mt-1 text-[12px] text-ink-4">{entry.department}</p></div><span className="mono rounded-full bg-surface-2 px-2 py-1 text-[12px] text-accent">{entry.articleCount} 条</span></div><div className="mt-4 flex flex-wrap gap-2">{(entry.researchDirections.length ? entry.researchDirections : ["等待科研动态"]).map((direction) => <span key={direction} className="rounded-full border border-line px-2.5 py-1 text-[11px] text-ink-3">{direction}</span>)}</div>{entry.graduationTopics.length > 0 && <div className="mt-4 border-t border-line-soft pt-3"><p className="text-[11px] font-semibold text-ink-4">推荐毕设方向</p><p className="mt-1 text-[12px] leading-6 text-ink-3">{entry.graduationTopics[0]}</p></div>}</article>)}</section>
  </main>;
}
