export interface UniversityProfile {
  name: string;
  englishName: string;
  aliases: string[];
  department: string;
  researchDirections: Array<{ name: string; keywords: string[] }>;
  graduationTopics: string[];
}

const commonDirections = ["新能源电力系统", "智能电网", "电力电子", "自动控制"];

const profile = (name: string, englishName: string, department: string, aliases: string[] = [name]): UniversityProfile => ({
  name, englishName, aliases, department,
  researchDirections: commonDirections.map((direction) => ({ name: direction, keywords: [direction, "新能源", "储能", "智能电网", "电力电子", "控制"] })),
  graduationTopics: [
    `基于MATLAB/Simulink的${name}新能源系统仿真研究`,
    `基于Python的${name}智能电网运行数据分析`,
  ],
});

export const UNIVERSITY_PROFILES: readonly UniversityProfile[] = [
  {
    name: "南京师范大学", englishName: "Nanjing Normal University", aliases: ["南京师范大学", "南师大", "NNU"], department: "电气与自动化工程学院",
    researchDirections: [
      { name: "新能源电力系统", keywords: ["新能源", "光伏", "风电", "储能", "微电网", "综合能源"] },
      { name: "智能电网", keywords: ["智能电网", "能源互联网", "配电网", "优化调度"] },
      { name: "电力电子", keywords: ["逆变器", "变流器", "PWM", "电能质量"] },
      { name: "自动控制", keywords: ["预测控制", "优化控制", "人工智能"] },
    ],
    graduationTopics: [
      "基于MATLAB的光伏储能系统能量管理策略研究",
      "基于Simulink的微电网并离网控制策略仿真",
      "基于Python的配电网优化调度方法研究",
      "基于MATLAB的逆变器电能质量控制研究",
    ],
  },
  profile("清华大学", "Tsinghua University", "电机工程与应用电子技术系", ["清华大学", "清华", "Tsinghua"]),
  profile("西安交通大学", "Xi'an Jiaotong University", "电气工程学院", ["西安交通大学", "西安交大", "XJTU"]),
  profile("华中科技大学", "Huazhong University of Science and Technology", "电气与电子工程学院", ["华中科技大学", "华中科大", "HUST"]),
  profile("浙江大学", "Zhejiang University", "电气工程学院", ["浙江大学", "浙大", "ZJU"]),
  profile("上海交通大学", "Shanghai Jiao Tong University", "电子信息与电气工程学院", ["上海交通大学", "上交", "SJTU"]),
  profile("华北电力大学", "North China Electric Power University", "电气与电子工程学院", ["华北电力大学", "华电", "NCEPU"]),
  profile("重庆大学", "Chongqing University", "电气工程学院", ["重庆大学", "重大", "CQU"]),
  profile("山东大学", "Shandong University", "电气工程学院", ["山东大学", "山大", "SDU"]),
  profile("天津大学", "Tianjin University", "电气自动化与信息工程学院", ["天津大学", "天大", "TJU"]),
  profile("东南大学", "Southeast University", "电气工程学院", ["东南大学", "东大", "SEU"]),
  profile("哈尔滨工业大学", "Harbin Institute of Technology", "电气工程及自动化学院", ["哈尔滨工业大学", "哈工大", "HIT"]),
  profile("四川大学", "Sichuan University", "电气工程学院", ["四川大学", "川大", "SCU"]),
  profile("武汉大学", "Wuhan University", "电气与自动化学院", ["武汉大学", "武大", "WHU"]),
  profile("湖南大学", "Hunan University", "电气与信息工程学院", ["湖南大学", "湖大", "HNU"]),
  profile("电子科技大学", "University of Electronic Science and Technology of China", "机械与电气工程学院", ["电子科技大学", "电子科大", "UESTC"]),
  profile("合肥工业大学", "Hefei University of Technology", "电气与自动化工程学院", ["合肥工业大学", "合工大", "HFUT"]),
  profile("河海大学", "Hohai University", "能源与电气学院", ["河海大学", "河海", "HHU"]),
  profile("南京航空航天大学", "Nanjing University of Aeronautics and Astronautics", "自动化学院", ["南京航空航天大学", "南航", "NUAA"]),
  profile("南京理工大学", "Nanjing University of Science and Technology", "自动化学院", ["南京理工大学", "南理工", "NJUST"]),
];

export const UNIVERSITY_BY_ALIAS = new Map(UNIVERSITY_PROFILES.flatMap((university) => university.aliases.map((alias) => [alias.toLowerCase(), university] as const)));

export function matchUniversity(text: string): UniversityProfile | null {
  const lower = text.toLowerCase();
  return UNIVERSITY_PROFILES.find((university) => university.aliases.some((alias) => lower.includes(alias.toLowerCase()))) ?? null;
}
