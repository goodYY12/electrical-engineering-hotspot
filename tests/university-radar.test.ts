import assert from "node:assert/strict";
import test from "node:test";
import { analyzeUniversityResearch } from "../modules/university-radar/analyzer.ts";
import { matchResearchDirections } from "../modules/university-radar/keywords.ts";
import { UNIVERSITY_PROFILES, matchUniversity } from "../modules/university-radar/universities.ts";

test("高校画像覆盖首批 20 所高校，并能识别南京师范大学别名", () => {
  assert.equal(UNIVERSITY_PROFILES.length, 20);
  assert.equal(matchUniversity("NNU 电气与自动化工程学院" )?.name, "南京师范大学");
});

test("南京师范大学科研关键词映射到研究方向", () => {
  const university = matchUniversity("南京师范大学")!;
  assert.deepEqual(matchResearchDirections("南京师范大学 光伏 储能 微电网", university), ["新能源电力系统"]);
  assert.deepEqual(matchResearchDirections("南京师范大学 逆变器 PWM 电能质量", university), ["电力电子"]);
});

test("高校科研分析生成可落地的 metadata 和本科毕设建议", () => {
  const metadata = analyzeUniversityResearch({
    title: "南京师范大学电气与自动化工程学院开展光伏储能微电网研究",
    body: "研究围绕新能源、储能和微电网能量管理，使用 MATLAB/Simulink 进行仿真验证。",
    sourceName: "南京师范大学电气科研动态",
    sourceConfig: { category: "university" },
  });
  assert.ok(metadata);
  assert.equal(metadata.university, "南京师范大学");
  assert.equal(metadata.department, "电气与自动化工程学院");
  assert.equal(metadata.isUniversityResearch, true);
  assert.equal(metadata.researchType, "新闻");
  assert.equal(metadata.graduationPossible, true);
  assert.ok(metadata.graduationTopics.some((topic) => topic.title.includes("MATLAB")));
  assert.ok(metadata.graduationScore >= 45 && metadata.graduationScore <= 100);
});
