import assert from "node:assert/strict";
import test from "node:test";
import sources from "../industry/sources.json" with { type: "json" };
import { analyzeUniversityResearch } from "../modules/university-radar/analyzer.ts";
import { UNIVERSITY_CROSSREF_SOURCES, UNIVERSITY_OFFICIAL_SOURCES } from "../modules/university-radar/sources.ts";
import { UNIVERSITY_DIRECTIONS, UNIVERSITY_PROFILES } from "../modules/university-radar/universities.ts";
import { unsupportedConfig } from "@aihot/backend/sources/config-keys";

test("南京师范大学论文 affiliation 生成高校科研 metadata", () => {
  const metadata = analyzeUniversityResearch({
    title: "Optimal switching control for a hybrid renewable energy system",
    body: "机构：Nanjing Normal University；研究包含新能源、储能和微电网。",
    sourceName: "Crossref · 南京师范大学电气论文",
    sourceConfig: { category: "university", universityRadar: true, university: "南京师范大学" },
  });
  assert.ok(metadata);
  assert.equal(metadata.isUniversityResearch, true);
  assert.equal(metadata.university, "南京师范大学");
  assert.equal(metadata.department, "电气与自动化工程学院");
  assert.equal(metadata.researchType, "论文");
  assert.ok(metadata.keywords.includes("新能源"));
});

test("南京师范大学高校源和 Crossref 源均能通过配置校验", () => {
  const defs = [...(sources as { sources: Array<{ id: string; kind: "web_list" | "json_list"; category?: string; config: Record<string, unknown> }> }).sources, ...UNIVERSITY_CROSSREF_SOURCES, ...UNIVERSITY_OFFICIAL_SOURCES];
  for (const id of ["web-njnu-electrical", "json-crossref-njnu-electrical"]) {
    const source = defs.find((item) => item.id === id);
    assert.ok(source);
    assert.deepEqual(unsupportedConfig(source.kind, source.config), []);
    assert.equal(source.category, "university");
    assert.equal(source.config.university, "南京师范大学");
  }
});

test("20 所高校都有地区、Crossref P0 和受控研究方向", () => {
  assert.equal(UNIVERSITY_PROFILES.length, 20);
  assert.equal(UNIVERSITY_CROSSREF_SOURCES.length, 20);
  assert.equal(UNIVERSITY_OFFICIAL_SOURCES.length, 5);
  for (const university of UNIVERSITY_PROFILES) {
    assert.ok(university.region);
    assert.ok(UNIVERSITY_CROSSREF_SOURCES.some((source) => source.config.university === university.name));
    for (const direction of university.researchDirections) assert.ok(UNIVERSITY_DIRECTIONS.includes(direction.name as (typeof UNIVERSITY_DIRECTIONS)[number]));
  }
});
