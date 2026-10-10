export interface UniversityRadarSource {
  id: string;
  name: string;
  category: "university";
  kind: "rss" | "web_list" | "json_list";
  config: Record<string, unknown>;
  tier: "T1" | "T1_5" | "T2";
  tags: string[];
}

/** The source is kept as a normal source definition; the generic collector owns fetching and retries. */
export const UNIVERSITY_RADAR_SOURCES: readonly UniversityRadarSource[] = [{
  id: "university-njnu-electrical",
  name: "南京师范大学电气科研动态",
  category: "university",
  kind: "web_list",
  config: {
    url: "https://www.nnu.edu.cn/",
    universityRadar: true,
    category: "university",
    adapter: "mimo_home",
    _aihot: { initialBackfillLimit: 12 },
  },
  tier: "T1",
  tags: ["高校", "南京师范大学", "新能源", "储能", "智能电网", "电力电子"],
}];
