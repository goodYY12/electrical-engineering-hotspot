import type { FastifyInstance } from "fastify";
import { CATEGORIES } from "@aihot/industry/taxonomy";
import { sql } from "@aihot/backend/db";
import { defineServerModule } from "@aihot/backend/modules";
import { selectedCondition } from "@aihot/backend/publication/scope";

const CATEGORY_KEYS = new Set<string>(CATEGORIES.map((category) => category.key));

interface CategoryAggregate {
  category: string;
  article_count: number;
  avg_hot_score: number;
  previous_count: number;
}

interface SnapshotRow {
  category: string;
  captured_at: Date;
  heat: number;
}

export interface RadarPoint {
  at: string;
  heat: number;
}

export interface RadarEntry {
  key: string;
  label: string;
  heat: number;
  trend: "up" | "down" | "flat";
  change: number;
  articleCount: number;
  averageHotScore: number;
  points: RadarPoint[];
}

export interface RadarResponse {
  generatedAt: string;
  windowDays: number;
  entries: RadarEntry[];
  method: string;
}

export const radarHeat = (average: number, count: number) => Math.round(Math.min(100, average * 0.75 + Math.min(100, count * 8) * 0.25));

async function aggregateCategories(): Promise<CategoryAggregate[]> {
  const now = new Date();
  return sql<CategoryAggregate[]>`
    SELECT p.category,
      count(*) FILTER (WHERE p.timeline_at >= ${new Date(now.getTime() - 24 * 60 * 60_000)})::int AS article_count,
      coalesce(avg(p.score) FILTER (WHERE p.timeline_at >= ${new Date(now.getTime() - 7 * 24 * 60 * 60_000)}), 0)::float8 AS avg_hot_score,
      count(*) FILTER (
        WHERE p.timeline_at >= ${new Date(now.getTime() - 48 * 60 * 60_000)}
          AND p.timeline_at < ${new Date(now.getTime() - 24 * 60 * 60_000)}
      )::int AS previous_count
    FROM publications p
    WHERE ${selectedCondition(now)}
      AND p.timeline_at >= ${new Date(now.getTime() - 7 * 24 * 60 * 60_000)}
      AND p.category IS NOT NULL
    GROUP BY p.category`;
}

export async function snapshotElectricalRadar(): Promise<{ categories: number }> {
  const rows = await aggregateCategories();
  const capturedAt = new Date();
  capturedAt.setMinutes(0, 0, 0);
  for (const row of rows) {
    if (!CATEGORY_KEYS.has(row.category)) continue;
    await sql`
      INSERT INTO electrical_radar_snapshots
        (captured_at, category, heat, article_count, avg_hot_score)
      VALUES
        (${capturedAt}, ${row.category}, ${radarHeat(row.avg_hot_score, row.article_count)}, ${row.article_count}, ${row.avg_hot_score})
      ON CONFLICT (captured_at, category) DO UPDATE SET
        heat = EXCLUDED.heat,
        article_count = EXCLUDED.article_count,
        avg_hot_score = EXCLUDED.avg_hot_score`;
  }
  return { categories: rows.length };
}

async function readRadar(): Promise<RadarResponse> {
  const [aggregates, snapshots] = await Promise.all([
    aggregateCategories(),
    sql<SnapshotRow[]>`
      SELECT category, captured_at, heat::float8
      FROM electrical_radar_snapshots
      WHERE captured_at >= now() - interval '30 days'
      ORDER BY captured_at ASC`,
  ]);
  const byCategory = new Map(aggregates.map((row) => [row.category, row]));
  const points = new Map<string, RadarPoint[]>();
  for (const row of snapshots) {
    const values = points.get(row.category) ?? [];
    values.push({ at: row.captured_at.toISOString(), heat: Math.round(row.heat) });
    points.set(row.category, values);
  }

  const entries = CATEGORIES.map((category): RadarEntry => {
    const aggregate = byCategory.get(category.key);
    const count = aggregate?.article_count ?? 0;
    const previous = aggregate?.previous_count ?? 0;
    const change = previous === 0 ? (count > 0 ? 100 : 0) : Math.round(((count - previous) / previous) * 100);
    return {
      key: category.key,
      label: category.label,
      heat: radarHeat(aggregate?.avg_hot_score ?? 0, count),
      trend: change > 5 ? "up" : change < -5 ? "down" : "flat",
      change,
      articleCount: count,
      averageHotScore: Math.round(aggregate?.avg_hot_score ?? 0),
      points: points.get(category.key) ?? [],
    };
  }).sort((a, b) => b.heat - a.heat || b.articleCount - a.articleCount);

  return {
    generatedAt: new Date().toISOString(),
    windowDays: 30,
    entries,
    method: "领域热度由近 7 日 AI HotScore 均值（75%）与近 24 小时入选信息量（25%）组成；趋势比较前后两个 24 小时窗口。",
  };
}

function registerHttp(app: FastifyInstance): void {
  app.get("/api/electrical/radar", async (_request, reply) => {
    reply.header("Cache-Control", "public, max-age=60, s-maxage=300");
    return readRadar();
  });
}

export const ELECTRICAL_INTELLIGENCE_SERVER = defineServerModule({
  name: "electrical-intelligence",
  http: registerHttp,
  schedules: [{ name: "electrical.radar-snapshot", cron: "7 * * * *", run: snapshotElectricalRadar }],
  sitemap: { pages: [{ loc: "/radar", changefreq: "hourly", priority: 0.8 }] },
  llms: () => ({
    api: ["- `/api/electrical/radar`：电气技术领域热度、趋势和 30 天快照。"],
    pages: ["- `/radar`：电气工程技术雷达。"],
    pace: ["技术雷达每小时更新一次"],
  }),
});
