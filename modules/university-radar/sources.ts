import { UNIVERSITY_PROFILES } from "./universities.ts";

export interface UniversityRadarSource {
  id: string;
  name: string;
  category: "university";
  kind: "web_list" | "json_list";
  config: Record<string, unknown>;
  tier: "T1" | "T1_5";
  owner_entity_id: null;
  participation_mode: "editorial";
  interval_minutes: number;
  tags: string[];
  site_fulltext: false;
  syndicate_fulltext: false;
}

const ids: Record<string, string> = {
  南京师范大学: "njnu", 清华大学: "tsinghua", 西安交通大学: "xjtu", 华中科技大学: "hust", 浙江大学: "zju",
  上海交通大学: "sjtu", 华北电力大学: "ncepu", 重庆大学: "cqu", 山东大学: "sdu", 天津大学: "tju",
  东南大学: "seu", 哈尔滨工业大学: "hit", 四川大学: "scu", 武汉大学: "whu", 湖南大学: "hnu",
  电子科技大学: "uestc", 合肥工业大学: "hfut", 河海大学: "hohai", 南京航空航天大学: "nuaa", 南京理工大学: "njust",
};

const affiliationPaths = ["author.0.affiliation", "author.1.affiliation", "author.2.affiliation", "author.3.affiliation", "author.4.affiliation"];
const researchQuery = "renewable energy energy storage power electronics motor drive smart grid control";

export const UNIVERSITY_CROSSREF_SOURCES: readonly UniversityRadarSource[] = UNIVERSITY_PROFILES.map((university) => ({
  id: `json-crossref-${ids[university.name]}-electrical`,
  name: `Crossref · ${university.name}电气论文`,
  category: "university",
  kind: "json_list",
  config: {
    url: `https://api.crossref.org/works?query.affiliation=${encodeURIComponent(university.englishName)}&query.bibliographic=${encodeURIComponent(researchQuery)}&filter=type:journal-article&sort=published&order=desc&rows=20&select=DOI,title,abstract,created,URL,author`,
    mode: "json_api",
    itemsPath: "message.items",
    titlePaths: ["title.0"],
    summaryPaths: ["abstract"],
    authorPaths: ["author.0.family"],
    affiliationPaths,
    affiliationIncludes: [university.englishName, university.name],
    urlTemplate: "{raw:URL}",
    summaryIsBody: true,
    publishedAtPath: "created.date-time",
    externalIdPath: "DOI",
    universityRadar: true,
    university: university.name,
    category: "university",
    _aihot: { initialBackfillLimit: 12 },
  },
  tier: "T1_5",
  owner_entity_id: null,
  participation_mode: "editorial",
  interval_minutes: 60,
  tags: ["高校", "论文", university.name, ...university.researchDirections.map((direction) => direction.name)],
  site_fulltext: false,
  syndicate_fulltext: false,
}));

const official = (id: string, university: string, name: string, url: string): UniversityRadarSource => ({
  id, name, category: "university", kind: "web_list",
  config: { url, allowUrlPrefixes: [url], detail: { maxFetches: 8 }, universityRadar: true, university, category: "university", _aihot: { initialBackfillLimit: 12 } },
  tier: "T1", owner_entity_id: null, participation_mode: "editorial", interval_minutes: 60,
  tags: ["高校", "官方", university, "科研", "电气"], site_fulltext: false, syndicate_fulltext: false,
});

export const UNIVERSITY_OFFICIAL_SOURCES: readonly UniversityRadarSource[] = [
  official("web-njnu-electrical", "南京师范大学", "南京师范大学电气与自动化工程学院", "https://eae.njnu.edu.cn/"),
  official("web-tsinghua-electrical", "清华大学", "清华大学电机系科研动态", "https://www.eea.tsinghua.edu.cn/"),
  official("web-cqu-electrical", "重庆大学", "重庆大学电气工程学院科研动态", "https://www.cee.cqu.edu.cn/"),
  official("web-nuaa-automation", "南京航空航天大学", "南京航空航天大学自动化学院科研动态", "https://cae.nuaa.edu.cn/"),
  official("web-njust-automation", "南京理工大学", "南京理工大学自动化学院科研动态", "https://au.njust.edu.cn/"),
];

export const UNIVERSITY_RADAR_SOURCES: readonly UniversityRadarSource[] = [...UNIVERSITY_CROSSREF_SOURCES, ...UNIVERSITY_OFFICIAL_SOURCES];
