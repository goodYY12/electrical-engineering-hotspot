import { matchResearchDirections, matchedKeywords } from "./keywords.ts";
import { generateGraduationTopics, type GraduationTopic } from "./topic-generator.ts";
import { matchUniversity, type UniversityProfile } from "./universities.ts";

export interface UniversityRadarMetadata {
  isUniversityResearch: true;
  university: string;
  department: string;
  researchDirection: string;
  keywords: string[];
  researchType: "论文" | "项目" | "成果" | "新闻";
  graduationPossible: boolean;
  graduationScore: number;
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
  const university = matchUniversity(text);
  const configured = input.sourceConfig?.universityRadar === true || input.sourceConfig?.category === "university";
  if (!university && !configured) return null;
  const profile = university;
  if (!profile) return null;
  const directions = matchResearchDirections(text, profile);
  const keywords = matchedKeywords(text, profile);
  const topics = generateGraduationTopics(profile, directions);
  const score = Math.min(100, 45 + directions.length * 12 + Math.min(20, keywords.length * 3));
  return {
    isUniversityResearch: true,
    university: profile.name,
    department: profile.department,
    researchDirection: directions.join("、") || profile.researchDirections[0]?.name || "电气工程",
    keywords,
    researchType: researchType(text),
    graduationPossible: keywords.length >= 1,
    graduationScore: score,
    difficulty: topics[0]?.difficulty ?? "medium",
    graduationTopics: topics,
  };
}
