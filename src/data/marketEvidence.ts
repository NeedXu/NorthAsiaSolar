import type { Market } from './mock';
export const checkedAt='2026-11-06';
export const sources={
 jpea:'https://www.jpea.gr.jp/document/figure/',
 jp26:'https://www.jpea.gr.jp/wp-content/uploads/2026Q1_news_pv_shipment_in_japan.pdf',
 jp25:'https://www.jpea.gr.jp/wp-content/uploads/2025Q4_news_pv_shipment_in_japan.pdf',
 jp24:'https://www.jpea.gr.jp/wp-content/uploads/2024Q4_news_pv_shipment_in_japan.pdf',
 korea:'https://www.knrec.or.kr/biz/pds/statistic/view.do?no=470',
 taiwan:'https://www.tpvia.org.tw/',
 itri:'https://www.tarto.tw/Trend/TrendDetail?id=799213666-zh-tw',
 rei:'https://www.renewable-ei.org/pdfdownload/activities/REI_ENCorporatePPA_2026.pdf',
 twBuyers:'https://www.ey.gov.tw/File/A6B7A3E51F43D079?A=C',
 hdre:'https://www.hdrenewables.com/wp-content/uploads/2025/12/20251223-HDRE-Capital-Markets-Update-en_vf.pdf',
 topsun:'https://www.topsun.kr/board.es?act=view&bid=0012&list_no=3471&mid=a20601000000',
 samsung:'https://semiconductor.samsung.com/sustainability/planet/climate-change/',
 sk:'https://www.skecoplant.com/contents/boardView?contentsNo=lurQ4TJdkD&contentsOrders=1&languageCode=CM030001&menuCode=M6100',
 eternix:'https://esg.sketernix.com/?lv1=Our+ESG+Approach&lv2=Green+Energy+Solutions',
 sojitz:'https://www.sojitz.com/en/discover/project/article/2025102402.html',
 renova:'https://www.renovainc.com/en/business/solar/'
};
export const jpQuarters=[
 {period:'2025年1—3月',total:1283349,domestic:1272739,source:sources.jp24},
 {period:'2025年4—6月',total:1280194,domestic:1273701,source:sources.jp25},
 {period:'2026年1—3月',total:1552515,domestic:1549095,source:sources.jp25},
 {period:'2026年4—6月',total:1222325,domestic:1204233,source:sources.jp26}
];
export function japanSummary(domestic=true){const key=domestic?'domestic':'total';const current=jpQuarters[2][key]+jpQuarters[3][key];const previous=jpQuarters[0][key]+jpQuarters[1][key];return {current,previous,yoy:(current/previous-1)*100};}
export function seasonalForecast(domestic=true,adjustment=0){const base=domestic?6186052:6214558;const prior=jpQuarters[1][domestic?'domestic':'total'];const current=jpQuarters[3][domestic?'domestic':'total'];return base*current/prior*(1+adjustment/100);}
export type Dimension='EPC'|'绿电买家'|'投资商';
export type EvidenceRow={name:string;value:number;unit:string;period:string;scope:string;status:string;url:string;note:string};
export type EvidenceSet={title:string;basis:string;coverage:string;ranked:boolean;rows:EvidenceRow[]};
const row=(name:string,value:number,unit:string,period:string,scope:string,status:string,url:string,note:string):EvidenceRow=>({name,value,unit,period,scope,status,url,note});
const jpBuyers:[string,number][]=[['永旺 Aeon',200],['Microsoft',75],['LINE Yahoo',72],['东急 Tokyu',70],['Amazon',65],['JR East',58.6],['Equinix',30],['东急不动产集团',25],['加贺东芝电子',24],['Seven-Eleven Japan',21]];
const twBuyers:[string,number][]=[['台积电',2508016],['中华电信',70381],['台达电子',59827],['台湾大哥大集团',57758],['采钰科技',37726],['日月光',24987],['南亚科技',23259],['中国钢铁',20740],['乾坤科技',20098],['玉山商业银行',14684]];
const empty=(dimension:Dimension):EvidenceSet=>({title:`${dimension}前十 · 待核实`,basis:dimension==='EPC'?'同地区、同年度光伏承建容量（MW），完工与在建分别统计。':'同地区、同年度光伏新增投资金额或权益容量；不混排全口径资产与权益资产。',coverage:'未取得可比、完整的2026年地区榜单。下列仅为原始披露线索，不赋予地区名次。',ranked:false,rows:[]});
export const evidence:Record<Market,Record<Dimension,EvidenceSet>>={
 日本:{
  EPC:{...empty('EPC'),rows:[row('鸿德能源 HDRE',231,'MW','2026年计划','日本光伏EPC开工','企业计划',sources.hdre,'另计划119MW商业运行；开工、投运不能相加为采购量。')]},
  绿电买家:{title:'光伏PPA买家 · 已披露样本前十',basis:'按自然能源财团2026版报告第28—31页列出的2025年光伏场外PPA容量汇总；同名买家合并，风电、水电、生物质剔除。',coverage:'研究机构样本汇总，非政府或协会全国排名；MW为项目容量，并非实际购电量。2026年年度榜尚未核实。',ranked:true,rows:jpBuyers.map(([name,value])=>row(name,value,'MW','2025年公告样本','日本光伏场外PPA','研究机构汇编',sources.rei,name==='Amazon'?'35+10+10+10MW；仅本报告披露项目。':name==='JR East'?'21+37.6MW；剔除50MW生物质项目。':'样本中的项目容量，未披露交易及场内PPA不在内。'))},
  投资商:{...empty('投资商'),rows:[row('双日 Sojitz',3000,'座','截至2026财年目标','日本分布式光伏开发','企业目标',sources.sojitz,'电站数量目标，未披露同口径年度投资额；不能折算采购容量。'),row('RENOVA',40.8,'MW','2021年10月投运','日本 Karumai Sonbou Solar','历史项目',sources.renova,'单一项目额定容量，非年度投资总量或权益容量。')]}
 },
 韩国:{
  EPC:{...empty('EPC'),rows:[row('TOPSUN',18.112,'MW','2025-10-31签约','韩国济州岛光伏EPC','已签约',sources.topsun,'SK D&D为发包方，合同218亿韩元；预计完成不等于已竣工。')]},
  绿电买家:{title:'绿电买家前十 · 已核实线索',basis:'拟按韩国境内年度实际绿电采购量（GWh）排名；已披露PPA容量单列。',coverage:'未取得2026年全国前十；以下年份及能源范围不同，不排序。PPA合同容量不等于实际年度购电量。',ranked:false,rows:[row('三星半导体',681,'MW','截至2025年','韩国境内累计PPA','企业自述',sources.samsung,'累计11份PPA；2025年新增6份共252MW，含多种能源，不能全部计作光伏。'),row('SK海力士',100,'MW','2024-02-21签约','韩国光伏PPA','历史合同',sources.sk,'SK ecoplant计划供电，利用TOPSUN光伏电站；未确认2026实际交付量。')]},
  投资商:{...empty('投资商'),rows:[row('SK Eternix',180,'MW','2025年新增合同','韩国直接及第三方PPA供给','企业自述',sources.eternix,'供电合同规模，非当年投资额或权益资产；不用于投资商排名。'),row('SK D&D',18.112,'MW','2025-10-31签约','韩国济州岛项目发包方','已签约',sources.topsun,'EPC发包记录，未披露权益比例；投资额不可用EPC合同额替代。')]}
 },
 台湾:{
  EPC:{...empty('EPC'),rows:[row('鸿德能源 HDRE',210,'MW','2026年计划','台湾光伏EPC开工','企业计划',sources.hdre,'2025-12-23投资人简报；计划值尚未确认为2026实际完成量。')]},
  绿电买家:{title:'绿电转供买家 · 官方历史前十',basis:'经济部2023-12-20简报第5页累计转供凭证张数；统计背景截至2023年9月。1张对应1MWh，涵盖太阳能、风力、水力。',coverage:'这是历史官方榜，非2026年排名，也不是单独的光伏买家榜。当前年度T-REC交易记录仍待获取、清洗与核实。',ranked:true,rows:twBuyers.map(([name,value])=>row(name,value,'张','截至2023年9月','台湾累计绿电转供','官方历史榜',sources.twBuyers,'累计凭证口径；不能解释为今年实际购电量或组件采购量。'))},
  投资商:{...empty('投资商'),rows:[row('Star Power Energy',99.1,'MW','2025-12-23披露','台湾在运光伏项目','企业自述',sources.hdre,'另有储能，不计入光伏容量；未取得投资人权益份额。'),row('Aquastar Energy',42,'MW','2025-12-23披露','台湾已并网光伏项目','企业自述',sources.hdre,'另有174MW在建，不与已并网相加作为实绩。')]}
 }
};
export const marketNotes:Record<Market,{association:string;url:string;status:string;detail:string;backup:string}>={
 日本:{association:'日本太陽光発電協会 JPEA',url:sources.jpea,status:'官方季度出货统计已核实',detail:'最新公开季度：2026年4—6月；2026-08-31发布。调查28家、25家回答，属于协会调查覆盖范围。2026年4月起停止公开月次速報。',backup:sources.jp26},
 韩国:{association:'韩国太阳光产业协会 KOPIA',url:'https://www.kopia.asia/',status:'协会官网本次读取超时',detail:'转查韩国能源公团：2025年产业/普及统计计划2026年12月发布；现有2024年报告不能冒充2026年出货实绩。未核实2026年官方出货值、同比及全年预测。',backup:sources.korea},
 台湾:{association:'台湾太阳光电产业协会 TPVIA',url:sources.taiwan,status:'协会官网本次返回403',detail:'工研院2026-03-09公开摘要讨论产业产值及展望，但未提供可直接使用的2026组件出货GW值。装机、产值、进出口重量不能直接替代出货量；未核实官方全年出货预测。',backup:sources.itri}
};
