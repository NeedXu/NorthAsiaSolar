export type Market = '日本' | '韩国' | '台湾';
export type Topic = '政策与补贴' | '市场趋势' | '竞争动态' | '技术创新';
export interface Intelligence { id:string; market:Market; title:string; date:string; topic:Topic; priority:'高'|'中'; source:string; url:string; summary:string; importance:string; impact:string; watch:string; tech:string }
export const markets:Market[]=['日本','韩国','台湾'];
export const topics:Topic[]=['政策与补贴','市场趋势','竞争动态','技术创新'];
export const marketInfo = {
 日本:{english:'JAPAN',code:'JP',capacity:'7.2',growth:'+12.5%',total:'98.4',focus:'住宅屋顶 · 高效组件',outlook:'分布式需求持续释放，高效率与轻量化产品迎来结构性机会。',values:[35,47,40,58,63,72,81],flag:'🇯🇵'},
 韩国:{english:'SOUTH KOREA',code:'KR',capacity:'3.8',growth:'+8.6%',total:'32.6',focus:'工商业屋顶 · 本地渠道',outlook:'企业绿电采购驱动工商业需求，本地合作与项目经济性成为关键。',values:[29,38,35,49,58,64,72],flag:'🇰🇷'},
 台湾:{english:'TAIWAN',code:'TW',capacity:'2.6',growth:'+10.2%',total:'18.9',focus:'屋顶项目 · 高可靠性',outlook:'屋顶场景与企业绿电需求并进，耐候性和系统价值更受关注。',values:[22,31,43,39,52,65,76],flag:'🇹🇼'}
};
const seeds:{market:Market; titles:string[]; sources:string[]; urls:string[]}[]=[
 {market:'日本',titles:['日本住宅屋顶需求升温，高效组件应用加速','东京建筑光伏政策进入实施观察窗口','LONGi 加码日本 BC 组件渠道布局','轻量化组件拓展低承重商业屋顶场景'],sources:['PV magazine','东京都政府','LONGi','PV Tech'],urls:['https://www.pv-magazine.com/','https://www.metro.tokyo.lg.jp/','https://www.longi.com/','https://www.pv-tech.org/']},
 {market:'韩国',titles:['韩国企业绿电采购带动工商业屋顶机会','韩国可再生能源支持机制进入调整观察期','Hanwha Qcells 聚焦高效组件与本地渠道','HJT 与叠层技术的商业化路径受到关注'],sources:['PV magazine','韩国能源公团','Hanwha Qcells','PV Tech'],urls:['https://www.pv-magazine.com/','https://www.energy.or.kr/','https://www.qcells.com/','https://www.pv-tech.org/']},
 {market:'台湾',titles:['台湾企业绿电需求推动屋顶光伏项目储备','屋顶光伏补贴与并网条件成为项目焦点','本土厂商强化高可靠性组件定位','防眩光组件探索交通与城市屋顶场景'],sources:['PV magazine','台湾经济部能源署','PV Tech','PV magazine'],urls:['https://www.pv-magazine.com/','https://www.moeaea.gov.tw/','https://www.pv-tech.org/','https://www.pv-magazine.com/']}
];
export const news:Intelligence[]=seeds.flatMap((s,m)=>s.titles.map((title,i)=>({id:`${m}-${i}`,market:s.market,title,date:`2026-11-0${4-i}`,topic:topics[[1,0,2,3][i]],priority:i===0||i===1?'高':'中',source:s.sources[i],url:s.urls[i],summary:['模拟场景：终端客户更关注单位屋顶发电量，渠道对高效产品的咨询增加。','模拟场景：地方支持政策与项目准入条件变化，需要持续核对官方文件。','模拟场景：竞争品牌加强产品培训及渠道覆盖，推动差异化销售。','模拟场景：新技术在特定屋顶场景中获得关注，商业化仍需验证。'][i],importance:'可能改变项目投资回报与客户选型逻辑，值得纳入区域销售观察。',impact:`晶科${s.market}团队可评估 N 型产品的系统价值，结合渠道反馈校准产品组合。`,watch:'核对官方原文、落地时间及渠道实际订单；在证据充分前不调整业务预测。',tech:['N型TOPCon','住宅屋顶组件','BC','轻量化组件'][i]})));
export const competitors=[
 {name:'LONGi',sub:'隆基绿能',tech:'BC',market:'日本',action:'高效率产品与渠道能力建设',trend:'产品布局',color:'#6f7ee8'},
 {name:'Trina Solar',sub:'天合光能',tech:'N型TOPCon',market:'日本',action:'工商业屋顶系统价值推广',trend:'渠道合作',color:'#22a58c'},
 {name:'JA Solar',sub:'晶澳科技',tech:'N型TOPCon',market:'韩国',action:'区域分销与高效产品组合',trend:'市场战略',color:'#e7a450'},
 {name:'Canadian Solar',sub:'阿特斯',tech:'N型TOPCon',market:'台湾',action:'组件与储能协同方案观察',trend:'产品布局',color:'#d56a79'},
 {name:'Hanwha Qcells',sub:'韩华',tech:'BC / 叠层',market:'韩国',action:'本地市场与高端产品定位',trend:'技术路线',color:'#638fe4'},
 {name:'本土厂商观察池',sub:'日本 · 韩国 · 台湾',tech:'高可靠性',market:'台湾',action:'本地认证、售后与渠道优势',trend:'市场战略',color:'#9d7bd5'}
];
export const technologies=['N型TOPCon','BC','HJT','钙钛矿叠层','住宅屋顶组件','轻量化组件','防眩光组件','数据中心光伏应用'];
