import { Link, useLoaderData, useSearchParams } from "react-router";
import { apiGet, cachedPage } from "@aihot/web/lib/api.server";
import { pageMeta } from "@aihot/web/lib/seo";
import type { GraduationTopicsResponse } from "../server.ts";

export { pageHeaders as headers } from "@aihot/web/lib/api.server";
export async function loader({ request }: { request: Request }) { return cachedPage(900, { data: await apiGet<GraduationTopicsResponse>("/api/university-radar/graduation-topics", { signal: request.signal }) }); }
export function meta() { return pageMeta({ title: "电气工程毕业设计选题", description: "基于中国高校电气科研方向生成的本科毕业设计选题建议。", path: "/graduation-topics" }); }

export default function GraduationTopicsPage() {
  const { data } = useLoaderData<typeof loader>();
  const [params] = useSearchParams();
  const university = params.get("university");
  const topics = university ? data.topics.filter((topic) => topic.university === university) : data.topics;
  return <main className="mx-auto max-w-[var(--page-max)] pb-14 pt-2 lg:pt-0"><header className="mb-5 border-b border-line pb-5"><p className="text-[12px] font-semibold uppercase tracking-[0.16em] text-accent">Graduation Topic Finder</p><h1 className="mt-2 text-[25px] font-bold tracking-[-0.02em] text-ink sm:text-[30px]">电气工程毕业设计选题</h1><p className="mt-2 max-w-3xl text-[13.5px] leading-7 text-ink-3">题目只根据已入库高校科研方向生成，优先使用 MATLAB、Simulink 或 Python 完成本科阶段的建模、控制与仿真验证。</p>{university && <p className="mt-3 text-[12px] text-ink-4">当前学校：{university} · <Link to="/graduation-topics" className="text-accent hover:underline">查看全部</Link></p>}</header>{topics.length === 0 ? <section className="card p-8 text-center text-[13px] text-ink-4">当前还没有可验证的高校科研数据用于生成选题。</section> : <section className="grid gap-4 md:grid-cols-2">{topics.map((topic) => <article key={`${topic.university}-${topic.title}`} className="card p-5"><div className="flex items-start justify-between gap-3"><div><h2 className="text-[16px] font-semibold leading-6 text-ink">{topic.title}</h2><p className="mt-2 text-[12px] text-ink-4">来源：{topic.university} · {topic.department}</p></div><span className="mono rounded-full bg-surface-2 px-2 py-1 text-[12px] text-accent">{topic.score} 分</span></div><div className="mt-4 flex flex-wrap gap-2">{topic.tools.map((tool) => <span key={tool} className="rounded-full border border-line px-2.5 py-1 text-[11px] text-ink-3">{tool}</span>)}<span className="rounded-full border border-line px-2.5 py-1 text-[11px] text-ink-3">{topic.difficulty === "easy" ? "简单" : topic.difficulty === "hard" ? "困难" : "中等"}</span></div><div className="mt-4 grid grid-cols-4 gap-2 border-t border-line-soft pt-3 text-center text-[11px] text-ink-4"><span>创新 {topic.innovationScore}</span><span>资料 {topic.materialScore}</span><span>实现 {topic.feasibilityScore}</span><span>工程 {topic.engineeringValueScore}</span></div></article>)}</section>}</main>;
}
