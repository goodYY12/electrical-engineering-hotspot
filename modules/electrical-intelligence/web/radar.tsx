import { useLoaderData } from "react-router";
import type { RadarEntry, RadarResponse } from "../server";
import { apiGet, cachedPage } from "@aihot/web/lib/api.server";
import { pageMeta } from "@aihot/web/lib/seo";
import type { Screen } from "@aihot/web/components/shell/screens";

export const handle: Screen = { tab: "me", name: "技术雷达" };
export { pageHeaders as headers } from "@aihot/web/lib/api.server";

export async function loader({ request }: { request: Request }) {
  const radar = await apiGet<RadarResponse>("/api/electrical/radar", { signal: request.signal });
  return cachedPage(300, { radar });
}

export function meta() {
  return pageMeta({
    title: "电气工程技术雷达",
    description: "追踪新型电力系统、储能、光伏、风电、电力电子、SiC/GaN、电机、智能电网和高压输电的实时热度。",
    path: "/radar",
  });
}

const COLORS = ["#21d4d1", "#ff9f43", "#50d890", "#668cff", "#ef6f9c", "#9d7cff", "#ffc857", "#2ec4b6", "#ff6b5f", "#5bc0eb"];

function polygonPoints(entries: RadarEntry[], radius: number, cx = 180, cy = 180): string {
  const max = Math.max(entries.length, 3);
  return entries.map((entry, index) => {
    const angle = -Math.PI / 2 + (index * Math.PI * 2) / max;
    const r = radius * entry.heat / 100;
    return `${cx + Math.cos(angle) * r},${cy + Math.sin(angle) * r}`;
  }).join(" ");
}

function gridPoints(count: number, radius: number, cx = 180, cy = 180): string {
  return Array.from({ length: count }, (_, index) => {
    const angle = -Math.PI / 2 + (index * Math.PI * 2) / count;
    return `${cx + Math.cos(angle) * radius},${cy + Math.sin(angle) * radius}`;
  }).join(" ");
}

function RadarChart({ entries }: { entries: RadarEntry[] }) {
  const display = entries.slice(0, 10);
  return (
    <div className="relative mx-auto aspect-square w-full max-w-[540px]">
      <svg viewBox="0 0 360 360" className="size-full" role="img" aria-label="电气工程技术领域热度雷达图">
        <defs>
          <radialGradient id="radar-fill"><stop offset="0" stopColor="#21d4d1" stopOpacity=".45" /><stop offset="1" stopColor="#668cff" stopOpacity=".13" /></radialGradient>
        </defs>
        {[45, 90, 135].map((radius) => <polygon key={radius} points={gridPoints(display.length, radius)} fill="none" stroke="currentColor" className="text-line" strokeWidth="1" />)}
        {display.map((_, index) => {
          const angle = -Math.PI / 2 + (index * Math.PI * 2) / display.length;
          return <line key={index} x1="180" y1="180" x2={180 + Math.cos(angle) * 135} y2={180 + Math.sin(angle) * 135} stroke="currentColor" className="text-line" strokeWidth="1" />;
        })}
        <polygon points={polygonPoints(display, 135)} fill="url(#radar-fill)" stroke="#21d4d1" strokeWidth="2" />
        {display.map((entry, index) => {
          const angle = -Math.PI / 2 + (index * Math.PI * 2) / display.length;
          const r = 135 * entry.heat / 100;
          return <circle key={entry.key} cx={180 + Math.cos(angle) * r} cy={180 + Math.sin(angle) * r} r="4" fill={COLORS[index]} stroke="var(--surface)" strokeWidth="2" />;
        })}
      </svg>
    </div>
  );
}

function MiniTrend({ entry }: { entry: RadarEntry }) {
  const values = entry.points.slice(-24).map((point) => point.heat);
  if (values.length < 2) return <span className="text-[11px] text-ink-4">等待首批小时快照</span>;
  const width = 96;
  const height = 28;
  const points = values.map((value, index) => `${index * width / (values.length - 1)},${height - value * height / 100}`).join(" ");
  return <svg viewBox={`0 0 ${width} ${height}`} className="h-7 w-24" aria-hidden="true"><polyline points={points} fill="none" stroke="currentColor" className="text-accent" strokeWidth="2" vectorEffect="non-scaling-stroke" /></svg>;
}

export default function RadarPage() {
  const { radar } = useLoaderData<typeof loader>();
  return (
    <main className="mx-auto max-w-[var(--page-max)] pb-14 pt-2 lg:pt-0">
      <header className="mb-5 border-b border-line pb-5">
        <p className="text-[12px] font-semibold uppercase tracking-[0.16em] text-accent">Technology Intelligence</p>
        <h1 className="mt-2 text-[25px] font-bold tracking-[-0.02em] text-ink sm:text-[30px]">电气工程技术雷达</h1>
        <p className="mt-2 max-w-3xl text-[13.5px] leading-7 text-ink-3">从论文、新闻、政策和企业动态中计算各技术领域的当前热度。数据每小时更新，方向变化按前后两个 24 小时窗口比较。</p>
      </header>

      <div className="grid gap-5 xl:grid-cols-[minmax(0,1.12fr)_minmax(360px,.88fr)]">
        <section className="card overflow-hidden p-4 sm:p-6">
          <div className="flex items-center justify-between">
            <div><h2 className="text-[15px] font-semibold text-ink">领域热度分布</h2><p className="mt-1 text-[12px] text-ink-4">满分 100 · AI 价值评分与信息增量综合</p></div>
            <span className="mono text-[11px] text-ink-4">{new Date(radar.generatedAt).toLocaleString("zh-CN", { hour12: false })}</span>
          </div>
          <RadarChart entries={radar.entries} />
          <div className="grid grid-cols-2 gap-x-4 gap-y-2 sm:grid-cols-5">
            {radar.entries.map((entry, index) => <div key={entry.key} className="flex items-center gap-2 text-[12px] text-ink-3"><span className="size-2 rounded-full" style={{ background: COLORS[index] }} /><span>{entry.label}</span></div>)}
          </div>
        </section>

        <section className="card overflow-hidden">
          <div className="border-b border-line px-5 py-4"><h2 className="text-[15px] font-semibold text-ink">技术热度排行</h2><p className="mt-1 text-[12px] text-ink-4">近 24 小时信号与近 7 日专业评分</p></div>
          <ol className="divide-y divide-line-soft">
            {radar.entries.map((entry, index) => (
              <li key={entry.key} className="grid grid-cols-[28px_minmax(0,1fr)_auto] items-center gap-3 px-5 py-3">
                <span className="mono text-[12px] font-semibold text-ink-4">{String(index + 1).padStart(2, "0")}</span>
                <div className="min-w-0">
                  <div className="flex items-center gap-2"><span className="truncate text-[14px] font-semibold text-ink">{entry.label}</span><span className={`text-[11px] ${entry.trend === "up" ? "text-ok" : entry.trend === "down" ? "text-hot" : "text-ink-4"}`}>{entry.trend === "up" ? "↑" : entry.trend === "down" ? "↓" : "→"} {Math.abs(entry.change)}%</span></div>
                  <div className="mt-1 flex items-center gap-3 text-[11px] text-ink-4"><span>{entry.articleCount} 条新情报</span><span>AI 均分 {entry.averageHotScore}</span></div>
                </div>
                <div className="flex items-center gap-3"><MiniTrend entry={entry} /><span className="mono w-8 text-right text-[20px] font-semibold text-ink">{entry.heat}</span></div>
              </li>
            ))}
          </ol>
        </section>
      </div>

      <p className="mt-5 rounded-card border border-line bg-surface px-5 py-4 text-[12.5px] leading-6 text-ink-3">{radar.method} 技术热度表示信息价值与活跃程度，不等同于市场规模、投资回报或技术成熟度。</p>
    </main>
  );
}
