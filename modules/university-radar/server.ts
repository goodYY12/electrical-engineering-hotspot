import type { FastifyInstance } from "fastify";
import { sql } from "@aihot/backend/db";
import { defineServerModule } from "@aihot/backend/modules";
import { selectedCondition } from "@aihot/backend/publication/scope";
import { UNIVERSITY_PROFILES } from "./universities.ts";
import { generateGraduationTopics, type GraduationTopic } from "./topic-generator.ts";

export interface UniversityRadarEntry { university: string; department: string; articleCount: number; researchDirections: string[]; graduationTopics: string[] }
export interface UniversityRadarResponse { generatedAt: string; totalArticles: number; entries: UniversityRadarEntry[] }
export interface GraduationTopicsResponse { generatedAt: string; topics: Array<GraduationTopic & { university: string; department: string }> }

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

async function readGraduationTopics(): Promise<GraduationTopicsResponse> {
  const now = new Date();
  const topics = UNIVERSITY_PROFILES.flatMap((profile) => generateGraduationTopics(profile, []).map((topic) => ({ ...topic, university: profile.name, department: profile.department })));
  return { generatedAt: now.toISOString(), topics };
}

export const UNIVERSITY_RADAR_SERVER = defineServerModule({
  name: "university-radar",
  http: (app: FastifyInstance) => {
    app.get("/api/university-radar", async (_request, reply) => { reply.header("Cache-Control", "public, max-age=60, s-maxage=300"); return readRadar(); });
    app.get("/api/university-radar/graduation-topics", async (_request, reply) => { reply.header("Cache-Control", "public, max-age=300, s-maxage=900"); return readGraduationTopics(); });
  },
  sitemap: { pages: [{ loc: "/university-radar", changefreq: "hourly", priority: 0.7 }, { loc: "/graduation-topics", changefreq: "daily", priority: 0.6 }] },
  llms: () => ({ api: ["- `/api/university-radar`：中国高校电气科研动态和毕业设计方向。", "- `/api/university-radar/graduation-topics`：本科毕业设计选题建议。"], pages: ["- `/university-radar`：中国高校电气科研雷达。", "- `/graduation-topics`：电气工程本科毕业设计选题。"] }),
});
