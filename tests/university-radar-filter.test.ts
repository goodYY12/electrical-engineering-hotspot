import assert from "node:assert/strict";
import test from "node:test";
import { filterUniversityEntries } from "../modules/university-radar/filter.ts";
import type { UniversityRadarEntry } from "../modules/university-radar/server.ts";

const entries: UniversityRadarEntry[] = [
  { university: "南京师范大学", region: "江苏", department: "电气与自动化工程学院", articleCount: 2, researchDirections: ["新能源电力系统", "储能"], graduationTopics: ["光伏储能"], items: [] },
  { university: "清华大学", region: "北京", department: "电机系", articleCount: 1, researchDirections: ["电力电子"], graduationTopics: ["变流器控制"], items: [] },
];

test("高校雷达按学校、地区和方向筛选真实条目", () => {
  assert.deepEqual(filterUniversityEntries(entries, { university: "清华大学" }).map((entry) => entry.university), ["清华大学"]);
  assert.deepEqual(filterUniversityEntries(entries, { region: "江苏" }).map((entry) => entry.university), ["南京师范大学"]);
  assert.deepEqual(filterUniversityEntries(entries, { direction: "储能" }).map((entry) => entry.university), ["南京师范大学"]);
  assert.deepEqual(filterUniversityEntries(entries, { region: "重庆" }), []);
});
