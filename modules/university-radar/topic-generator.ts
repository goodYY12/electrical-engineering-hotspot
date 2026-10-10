import type { UniversityProfile } from "./universities.ts";

export type GraduationDifficulty = "easy" | "medium" | "hard";

export interface GraduationTopic {
  title: string;
  direction: string;
  tools: string[];
  innovationScore: number;
  materialScore: number;
  feasibilityScore: number;
  engineeringValueScore: number;
  score: number;
  difficulty: GraduationDifficulty;
}

export function generateGraduationTopics(university: UniversityProfile, directions: string[]): GraduationTopic[] {
  const selected = university.graduationTopics.filter((topic) => directions.length === 0 || directions.some((direction) => topic.includes(direction) || topic.includes("光伏") || topic.includes("微电网") || topic.includes("配电网") || topic.includes("逆变器")));
  return (selected.length ? selected : university.graduationTopics).map((title, index) => {
    const difficulty: GraduationDifficulty = index === 0 ? "medium" : index > 2 ? "hard" : "easy";
    const scores = { innovationScore: 78 - index * 3, materialScore: 88 - index * 2, feasibilityScore: difficulty === "hard" ? 68 : 84, engineeringValueScore: 82 - index };
    return { title, direction: directions[index % Math.max(1, directions.length)] ?? university.researchDirections[0]?.name ?? "电气工程", tools: title.includes("Python") ? ["Python"] : ["MATLAB", "Simulink"], ...scores, score: Math.round((scores.innovationScore + scores.materialScore + scores.feasibilityScore + scores.engineeringValueScore) / 4), difficulty };
  });
}
