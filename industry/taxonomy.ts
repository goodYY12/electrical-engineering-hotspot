// ElectroRadar 的稳定行业词表。category key 会进入 URL 和公开 API，上线后不再改名。

export const CATEGORIES = [
  { key: "power-system", label: "电力系统", section: "电网与系统", guide: "电力系统规划、运行、稳定、调度、保护、电力市场与新型电力系统工程。" },
  { key: "smart-grid", label: "智能电网", section: "电网与系统", guide: "数字电网、配电自动化、微电网、虚拟电厂、需求响应、能源互联网与电网数字化。" },
  { key: "renewable-energy", label: "新能源", section: "新能源与储能", guide: "光伏、风电、氢能、可再生能源并网、预测、消纳和场站工程。" },
  { key: "energy-storage", label: "储能", section: "新能源与储能", guide: "电化学、机械、热储能、储能系统集成、BMS、EMS、安全、寿命与商业模式。" },
  { key: "power-electronics", label: "电力电子", section: "装备与器件", guide: "变流器、逆变器、整流器、固态变压器、柔性直流、SiC/GaN 器件及其控制和工程应用。" },
  { key: "motor-drive", label: "电机驱动", section: "装备与器件", guide: "电机本体、驱动器、伺服、牵引、电动汽车驱动、状态监测与高效设计。" },
  { key: "high-voltage", label: "高压输电", section: "装备与器件", guide: "高电压绝缘、交直流输电、变压器、开关设备、电缆、局放、雷电与试验技术。" },
  { key: "control-automation", label: "控制系统", section: "控制与软件", guide: "自动控制、工业控制、保护控制、优化、模型预测控制、数字孪生和电气软件工具。" },
  { key: "policy-standards", label: "标准政策", section: "政策与标准", guide: "IEC/IEEE/国家及行业标准更新，能源政策、电网规划、市场规则和监管变化。" },
  { key: "industry-business", label: "产业动态", section: "产业与公司", guide: "电气企业的新产品、技术路线、项目投资、产能建设、合作并购、专利和供应链变化。" },
] as const satisfies ReadonlyArray<{ key: string; label: string; feedLabel?: string; section: string; guide: string; commentary?: true }>;

export const RELEASE: { category: string; tag: string; unit: string } | null = {
  category: "industry-business", tag: "产品发布", unit: "项新产品",
};

export const PLAIN_TERMS: readonly string[] = [
  "ac", "dc", "hvac", "hvdc", "bms", "ems", "vpp", "sic", "gan", "iec", "ieee", "der", "microgrid",
];

export const ITEM_TYPES = [
  "technical_breakthrough", "product_launch", "research_paper", "standard_policy",
  "engineering_project", "business_event", "expert_analysis",
] as const;

export const CATEGORY_TAGS = [
  "技术突破", "产品发布", "论文/研究", "政策/标准", "工程项目", "企业动态",
  "专利趋势", "事故/安全", "观点/分析", "教程/实践", "行业新闻", "其他",
] as const;

export const TOPIC_TAGS = [
  "新型电力系统", "电网稳定", "继电保护", "电力市场", "微电网", "虚拟电厂", "智能电网",
  "电化学储能", "长时储能", "储能安全", "光伏", "风电", "氢能", "新能源并网",
  "构网型变流器", "电力电子", "SiC/GaN", "固态变压器", "柔性直流",
  "电机", "电机驱动", "工业控制", "数字孪生", "状态监测", "特高压", "高压绝缘", "变压器",
] as const;

export const ENTITY_TAGS = [
  "IEEE", "IEC", "EPRI", "DOE", "国家能源局", "国家电网", "南方电网", "中国电科院",
  "Siemens Energy", "ABB", "Schneider Electric", "GE Vernova", "Hitachi Energy",
  "华为数字能源", "阳光电源", "宁德时代",
] as const;

export const TAG_SYNONYMS: Readonly<Record<string, string>> = {
  论文: "论文/研究", 研究: "论文/研究", paper: "论文/研究",
  标准: "政策/标准", 政策: "政策/标准", 监管: "政策/标准", 法规: "政策/标准",
  产品: "产品发布", 新品: "产品发布", 发布: "产品发布",
  企业: "企业动态", 公司动态: "企业动态", 融资: "企业动态", 并购: "企业动态", 投资: "企业动态",
  工程: "工程项目", 项目: "工程项目", 示范项目: "工程项目",
  安全: "事故/安全", 事故: "事故/安全", 专利: "专利趋势", 趋势: "观点/分析", 解读: "观点/分析",
  教程: "教程/实践", 实践: "教程/实践", 指南: "教程/实践", 新闻: "行业新闻",
  碳化硅: "SiC/GaN", 氮化镓: "SiC/GaN", 构网型: "构网型变流器", 虚拟同步机: "构网型变流器",
};

export const ENTITIES: Record<string, { name: string; displayTag: string | null; aliases: string[]; otherNames?: string[] }> = {
  ieee: { name: "IEEE", displayTag: "IEEE", aliases: ["IEEE", "Institute of Electrical and Electronics Engineers"] },
  iec: { name: "IEC", displayTag: "IEC", aliases: ["IEC", "International Electrotechnical Commission"] },
  epri: { name: "EPRI", displayTag: "EPRI", aliases: ["EPRI", "Electric Power Research Institute"] },
  doe: { name: "U.S. Department of Energy", displayTag: "DOE", aliases: ["DOE", "U.S. Department of Energy", "Department of Energy"] },
  nea: { name: "国家能源局", displayTag: "国家能源局", aliases: ["国家能源局", "National Energy Administration"] },
  sgcc: { name: "国家电网", displayTag: "国家电网", aliases: ["国家电网", "State Grid", "SGCC"] },
  csg: { name: "南方电网", displayTag: "南方电网", aliases: ["南方电网", "China Southern Power Grid", "CSG"] },
  cepri: { name: "中国电科院", displayTag: "中国电科院", aliases: ["中国电科院", "中国电力科学研究院", "CEPRI"] },
  siemens: { name: "Siemens Energy", displayTag: "Siemens Energy", aliases: ["Siemens Energy", "西门子能源"] },
  abb: { name: "ABB", displayTag: "ABB", aliases: ["ABB", "ABB Group"] },
  schneider: { name: "Schneider Electric", displayTag: "Schneider Electric", aliases: ["Schneider Electric", "施耐德电气"] },
  gevernova: { name: "GE Vernova", displayTag: "GE Vernova", aliases: ["GE Vernova", "GE Grid Solutions"] },
  hitachi: { name: "Hitachi Energy", displayTag: "Hitachi Energy", aliases: ["Hitachi Energy", "日立能源"] },
  huawei: { name: "华为数字能源", displayTag: "华为数字能源", aliases: ["华为数字能源", "Huawei Digital Power"] },
  sungrow: { name: "阳光电源", displayTag: "阳光电源", aliases: ["阳光电源", "Sungrow"] },
  catl: { name: "宁德时代", displayTag: "宁德时代", aliases: ["宁德时代", "CATL"] },
};

export const IDENTITY_LEXICON: ReadonlyArray<{ id: string; name: string; patterns: RegExp[] }> = [
  { id: "ieee", name: "IEEE", patterns: [/\bIEEE\b/i] },
  { id: "iec", name: "IEC", patterns: [/\bIEC\b|国际电工委员会/i] },
  { id: "epri", name: "EPRI", patterns: [/\bEPRI\b|Electric Power Research Institute/i] },
  { id: "doe", name: "DOE", patterns: [/U\.S\. Department of Energy|美国能源部|\bDOE\b/i] },
  { id: "nea", name: "国家能源局", patterns: [/国家能源局|National Energy Administration/i] },
  { id: "sgcc", name: "国家电网", patterns: [/国家电网|State Grid|\bSGCC\b/i] },
  { id: "csg", name: "南方电网", patterns: [/南方电网|China Southern Power Grid|\bCSG\b/i] },
  { id: "cepri", name: "中国电科院", patterns: [/中国电科院|中国电力科学研究院|\bCEPRI\b/i] },
  { id: "siemens", name: "Siemens Energy", patterns: [/Siemens Energy|西门子能源/i] },
  { id: "abb", name: "ABB", patterns: [/\bABB\b/] },
  { id: "schneider", name: "Schneider Electric", patterns: [/Schneider Electric|施耐德电气/i] },
  { id: "gevernova", name: "GE Vernova", patterns: [/GE Vernova|GE Grid Solutions/i] },
  { id: "hitachi", name: "Hitachi Energy", patterns: [/Hitachi Energy|日立能源/i] },
  { id: "huawei", name: "华为数字能源", patterns: [/华为数字能源|Huawei Digital Power/i] },
  { id: "sungrow", name: "阳光电源", patterns: [/阳光电源|\bSungrow\b/i] },
  { id: "catl", name: "宁德时代", patterns: [/宁德时代|\bCATL\b/i] },
];

export const PUBLISHER_DOMAINS: ReadonlyArray<{ entityId: string; domains: readonly string[] }> = [
  { entityId: "ieee", domains: ["ieee.org", "ieee-pes.org", "spectrum.ieee.org"] },
  { entityId: "iec", domains: ["iec.ch"] },
  { entityId: "epri", domains: ["epri.com"] },
  { entityId: "doe", domains: ["energy.gov"] },
  { entityId: "nea", domains: ["nea.gov.cn"] },
  { entityId: "sgcc", domains: ["sgcc.com.cn"] },
  { entityId: "csg", domains: ["csg.cn"] },
  { entityId: "cepri", domains: ["epri.sgcc.com.cn"] },
  { entityId: "siemens", domains: ["siemens-energy.com"] },
  { entityId: "abb", domains: ["abb.com"] },
  { entityId: "schneider", domains: ["se.com"] },
  { entityId: "gevernova", domains: ["gevernova.com"] },
  { entityId: "hitachi", domains: ["hitachienergy.com"] },
  { entityId: "huawei", domains: ["digitalpower.huawei.com"] },
  { entityId: "sungrow", domains: ["sungrowpower.com"] },
  { entityId: "catl", domains: ["catl.com"] },
];

export const IDENTITY_CONTEXT_ALIASES: ReadonlyArray<{ entityId: string; pattern: RegExp }> = [];
