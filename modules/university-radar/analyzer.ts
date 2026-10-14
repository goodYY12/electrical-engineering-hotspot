import { matchResearchDirections, matchedKeywords } from "./keywords.ts";
import { generateGraduationTopics, type GraduationTopic } from "./topic-generator.ts";
import { matchUniversity, type UniversityProfile } from "./universities.ts";

export interface UniversityRadarMetadata {
  isUniversityResearch: true;
  university: string;
  region: string;
  department: string;
  direction: string;
  researchDirection: string;
  keywords: string[];
  technologyKeywords: string[];
  researchType: "论文" | "项目" | "成果" | "新闻";
  graduationPossible: boolean;
  graduationScore: number;
  score: number;
  difficulty: "easy" | "medium" | "hard";
  graduationTopics: GraduationTopic[];
}

const researchType = (text: string): UniversityRadarMetadata["researchType"] => {
  if (/论文|journal|paper|doi/i.test(text)) return "论文";
  // “电气与自动化工程学院” is an organization name, not evidence of an engineering project.
  if (/项目|示范|建设/.test(text)) return "项目";
  if (/成果|突破|发明|专利/.test(text)) return "成果";
  return "新闻";
};

export function analyzeUniversityResearch(input: { title: string; body?: string | null; sourceName?: string | null; sourceConfig?: Record<string, unknown> }): UniversityRadarMetadata | null {
  const text = [input.title, input.body ?? "", input.sourceName ?? ""].join(" ");
  const configuredUniversity = typeof input.sourceConfig?.university === "string" ? matchUniversity(String(input.sourceConfig.university)) : null;
  const university = matchUniversity(text) ?? configuredUniversity;
  const configured = input.sourceConfig?.universityRadar === true || input.sourceConfig?.category === "university";
  if (!university && !configured) return null;
  const profile = university;
  if (!profile) return null;
  const directions = matchResearchDirections(text, profile);
  const keywords = matchedKeywords(text, profile);
  const topics = generateGraduationTopics(profile, directions);
  const score = Math.min(100, 45 + directions.length * 12 + Math.min(20, keywords.length * 3));
  const direction = directions.join("、") || profile.researchDirections[0]?.name || "新能源电力系统";
  return {
    isUniversityResearch: true,
    university: profile.name,
    region: profile.region,
    department: profile.department,
    direction,
    researchDirection: direction,
    keywords,
    technologyKeywords: keywords,
    researchType: researchType(text),
    graduationPossible: keywords.length >= 1,
    graduationScore: score,
    score,
    difficulty: topics[0]?.difficulty ?? "medium",
    graduationTopics: topics,
  };
}
