export const UNIVERSITY_DIRECTIONS = ["新能源电力系统", "储能", "电力电子", "电机驱动", "智能电网", "控制"] as const;

export interface UniversityProfile {
  name: string;
  englishName: string;
  aliases: string[];
  region: string;
  department: string;
  researchDirections: Array<{ name: string; keywords: string[] }>;
  graduationTopics: string[];
}

const commonKeywords: Record<(typeof UNIVERSITY_DIRECTIONS)[number], string[]> = {
  新能源电力系统: ["新能源", "光伏", "风电", "微电网", "综合能源"],
  储能: ["储能", "电池", "能量管理", "SOC"],
  电力电子: ["电力电子", "逆变器", "变流器", "PWM", "SiC", "GaN"],
  电机驱动: ["电机驱动", "电气传动", "永磁电机", "电机控制"],
  智能电网: ["智能电网", "能源互联网", "配电网", "优化调度"],
  控制: ["控制", "预测控制", "优化控制", "智能控制"],
};

const profile = (name: string, englishName: string, region: string, department: string, aliases: string[] = [], directions: readonly (typeof UNIVERSITY_DIRECTIONS)[number][] = UNIVERSITY_DIRECTIONS, graduationTopics?: string[]): UniversityProfile => ({
  name,
  englishName,
  aliases: [...new Set([name, englishName, ...aliases])],
  region,
  department,
  researchDirections: directions.map((direction) => ({ name: direction, keywords: commonKeywords[direction] })),
  graduationTopics: graduationTopics ?? [
    `基于MATLAB/Simulink的${name}新能源系统仿真研究`,
    `基于Python的${name}智能电网运行数据分析`,
  ],
});

export const UNIVERSITY_PROFILES: readonly UniversityProfile[] = [
  profile("南京师范大学", "Nanjing Normal University", "江苏", "电气与自动化工程学院", ["南师大", "NNU"], ["新能源电力系统", "储能", "电力电子", "智能电网", "控制"], ["基于MATLAB的光伏储能系统能量管理策略研究", "基于Simulink的微电网并离网控制策略仿真", "基于Python的配电网优化调度方法研究", "基于MATLAB的逆变器电能质量控制研究"]),
  profile("清华大学", "Tsinghua University", "北京", "电机工程与应用电子技术系", ["清华", "Tsinghua"], ["新能源电力系统", "储能", "电力电子", "电机驱动", "智能电网"], ["基于MATLAB/Simulink的新型电力系统储能协同控制研究", "基于Python的配电网灵活性评估与优化调度"]),
  profile("西安交通大学", "Xi'an Jiaotong University", "陕西", "电气工程学院", ["西安交大", "XJTU"]),
  profile("华中科技大学", "Huazhong University of Science and Technology", "湖北", "电气与电子工程学院", ["华中科大", "HUST"]),
  profile("浙江大学", "Zhejiang University", "浙江", "电气工程学院", ["浙大", "ZJU"]),
  profile("上海交通大学", "Shanghai Jiao Tong University", "上海", "电子信息与电气工程学院", ["上交", "SJTU"]),
  profile("华北电力大学", "North China Electric Power University", "北京", "电气与电子工程学院", ["华电", "NCEPU"]),
  profile("重庆大学", "Chongqing University", "重庆", "电气工程学院", ["重大", "CQU"], ["新能源电力系统", "储能", "智能电网", "控制"], ["基于Simulink的风光储微电网协调控制研究", "基于Python的配电网故障诊断方法研究"]),
  profile("山东大学", "Shandong University", "山东", "电气工程学院", ["山大", "SDU"]),
  profile("天津大学", "Tianjin University", "天津", "电气自动化与信息工程学院", ["天大", "TJU"]),
  profile("东南大学", "Southeast University", "江苏", "电气工程学院", ["东大", "SEU"]),
  profile("哈尔滨工业大学", "Harbin Institute of Technology", "黑龙江", "电气工程及自动化学院", ["哈工大", "HIT"]),
  profile("四川大学", "Sichuan University", "四川", "电气工程学院", ["川大", "SCU"]),
  profile("武汉大学", "Wuhan University", "湖北", "电气与自动化学院", ["武大", "WHU"]),
  profile("湖南大学", "Hunan University", "湖南", "电气与信息工程学院", ["湖大", "HNU"]),
  profile("电子科技大学", "University of Electronic Science and Technology of China", "四川", "机械与电气工程学院", ["电子科大", "UESTC"]),
  profile("合肥工业大学", "Hefei University of Technology", "安徽", "电气与自动化工程学院", ["合工大", "HFUT"]),
  profile("河海大学", "Hohai University", "江苏", "能源与电气学院", ["河海", "HHU"]),
  profile("南京航空航天大学", "Nanjing University of Aeronautics and Astronautics", "江苏", "自动化学院", ["南航", "NUAA"], ["新能源电力系统", "储能", "电力电子", "电机驱动", "控制"], ["基于Simulink的航空电源变换器控制策略研究", "基于MATLAB的无人机电机驱动系统建模与仿真"]),
  profile("南京理工大学", "Nanjing University of Science and Technology", "江苏", "自动化学院", ["南理工", "NJUST"], ["储能", "电力电子", "电机驱动", "智能电网", "控制"], ["基于MATLAB的永磁电机驱动控制策略研究", "基于Python的储能微电网能量管理优化研究"]),
  profile("南京大学", "Nanjing University", "江苏", "现代工程与应用科学学院", ["南大", "NJU"]),
  profile("苏州大学", "Soochow University", "江苏", "机电工程学院", ["苏大", "SZU"], ["新能源电力系统", "储能", "电力电子", "控制"]),
  profile("江苏大学", "Jiangsu University", "江苏", "电气信息工程学院", ["江大", "UJS"], ["新能源电力系统", "储能", "电力电子", "电机驱动", "控制"]),
  profile("南京工业大学", "Nanjing Tech University", "江苏", "电气工程与控制科学学院", ["南工大", "NJTech"], ["新能源电力系统", "储能", "电力电子", "智能电网", "控制"]),
  profile("中国矿业大学", "China University of Mining and Technology", "江苏", "信息与控制工程学院", ["矿大", "CUMT"], ["新能源电力系统", "储能", "智能电网", "控制"]),
  profile("南京邮电大学", "Nanjing University of Posts and Telecommunications", "江苏", "自动化学院", ["南邮", "NJUPT"], ["电力电子", "智能电网", "控制"]),
  profile("江苏科技大学", "Jiangsu University of Science and Technology", "江苏", "电子信息学院", ["江苏科大", "JUST"], ["新能源电力系统", "电力电子", "电机驱动", "控制"]),
  profile("常州大学", "Changzhou University", "江苏", "电气信息工程学院", ["常大", "CCZU"], ["新能源电力系统", "储能", "电力电子", "控制"]),
  profile("扬州大学", "Yangzhou University", "江苏", "电气与能源动力工程学院", ["扬大", "YZU"], ["新能源电力系统", "储能", "智能电网", "控制"]),
];

export const UNIVERSITY_BY_ALIAS = new Map(UNIVERSITY_PROFILES.flatMap((university) => university.aliases.map((alias) => [alias.toLowerCase(), university] as const)));

export function matchUniversity(text: string): UniversityProfile | null {
  const lower = text.toLowerCase();
  return UNIVERSITY_PROFILES.find((university) => university.aliases.some((alias) => lower.includes(alias.toLowerCase()))) ?? null;
}
