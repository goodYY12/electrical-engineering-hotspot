import { matchUniversity, type UniversityProfile } from "./universities.ts";

export const UNIVERSITY_RESEARCH_KEYWORDS = [
  "新能源", "光伏", "风电", "储能", "微电网", "综合能源", "智能电网", "能源互联网", "配电网", "优化调度",
  "逆变器", "变流器", "PWM", "电能质量", "预测控制", "优化控制", "人工智能",
] as const;

export function matchResearchDirections(text: string, university?: UniversityProfile | null): string[] {
  const source = university ?? matchUniversity(text);
  if (!source) return [];
  const lower = text.toLowerCase();
  return source.researchDirections.filter((direction) => direction.keywords.some((keyword) => lower.includes(keyword.toLowerCase()))).map((direction) => direction.name);
}

export function matchedKeywords(text: string, university?: UniversityProfile | null): string[] {
  const source = university ?? matchUniversity(text);
  const keywords = source?.researchDirections.flatMap((direction) => direction.keywords) ?? [...UNIVERSITY_RESEARCH_KEYWORDS];
  const lower = text.toLowerCase();
  return [...new Set(keywords.filter((keyword) => lower.includes(keyword.toLowerCase())))];
}
