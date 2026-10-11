import assert from "node:assert/strict";
import test from "node:test";
import sources from "../industry/sources.json" with { type: "json" };
import { analyzeUniversityResearch } from "../modules/university-radar/analyzer.ts";
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
  const defs = (sources as { sources: Array<{ id: string; kind: "web_list" | "json_list"; category?: string; config: Record<string, unknown> }> }).sources;
  for (const id of ["web-njnu-electrical", "json-crossref-njnu-electrical"]) {
    const source = defs.find((item) => item.id === id);
    assert.ok(source);
    assert.deepEqual(unsupportedConfig(source.kind, source.config), []);
    assert.equal(source.category, "university");
    assert.equal(source.config.university, "南京师范大学");
  }
});
