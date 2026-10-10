import type { FastifyInstance } from "fastify";
import { sql } from "@aihot/backend/db";
import { defineServerModule } from "@aihot/backend/modules";
import { selectedCondition } from "@aihot/backend/publication/scope";
import { UNIVERSITY_PROFILES } from "./universities.ts";

export interface UniversityRadarEntry { university: string; department: string; articleCount: number; researchDirections: string[]; graduationTopics: string[] }
export interface UniversityRadarResponse { generatedAt: string; totalArticles: number; entries: UniversityRadarEntry[] }

async function readRadar(): Promise<UniversityRadarResponse> {
  const now = new Date();
  const rows = await sql<{ university: string; department: string; article_count: number; directions: string[] | null; graduation_topics: string[] | null }[]>`
    SELECT an.output->'universityRadar'->>'university' AS university,
      an.output->'universityRadar'->>'department' AS department, count(*)::int AS article_count,
      array_agg(DISTINCT an.output->'universityRadar'->>'researchDirection') AS directions,
      array_agg(DISTINCT topic->>'title') FILTER (WHERE topic->>'title' IS NOT NULL) AS graduation_topics
    FROM publications p JOIN analyses an ON an.id = p.analysis_id
    LEFT JOIN LATERAL jsonb_array_elements(coalesce(an.output->'universityRadar'->'graduationTopics', '[]'::jsonb)) topic ON true
    WHERE ${selectedCondition(now)} AND an.output ? 'universityRadar'
    GROUP BY an.output->'universityRadar'->>'university', an.output->'universityRadar'->>'department'`;
  const entries = rows.map((row) => ({ university: row.university, department: row.department, articleCount: Number(row.article_count), researchDirections: (row.directions ?? []).filter(Boolean), graduationTopics: row.graduation_topics ?? [] }));
  for (const profile of UNIVERSITY_PROFILES) if (!entries.some((entry) => entry.university === profile.name)) entries.push({ university: profile.name, department: profile.department, articleCount: 0, researchDirections: profile.researchDirections.map((direction) => direction.name), graduationTopics: profile.graduationTopics });
  entries.sort((a, b) => b.articleCount - a.articleCount || a.university.localeCompare(b.university, "zh-CN"));
  return { generatedAt: now.toISOString(), totalArticles: entries.reduce((sum, entry) => sum + entry.articleCount, 0), entries };
}

export const UNIVERSITY_RADAR_SERVER = defineServerModule({
  name: "university-radar",
  http: (app: FastifyInstance) => app.get("/api/university-radar", async (_request, reply) => { reply.header("Cache-Control", "public, max-age=60, s-maxage=300"); return readRadar(); }),
  sitemap: { pages: [{ loc: "/university-radar", changefreq: "hourly", priority: 0.7 }] },
  llms: () => ({ api: ["- `/api/university-radar`：中国高校电气科研动态和毕业设计方向。"], pages: ["- `/university-radar`：中国高校电气科研雷达。"] }),
});
