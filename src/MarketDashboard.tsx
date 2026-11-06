import { useState } from 'react';
import { ArrowDownToLine, ExternalLink } from 'lucide-react';
import type { Market } from './data/mock';
import { checkedAt, evidence, japanSummary, jpQuarters, marketNotes, seasonalForecast, sources, type Dimension } from './data/marketEvidence';
const gw=(kw:number)=>(kw/1e6).toFixed(3);
function exportEvidence(market:Market,dimension:Dimension){const set=evidence[market][dimension];const body=JSON.stringify({checkedAt,market,dimension,...set},null,2);const url=URL.createObjectURL(new Blob([body],{type:'application/json;charset=utf-8'}));const a=document.createElement('a');a.href=url;a.download=`${market}-${dimension}-证据-${checkedAt}.json`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
export default function MarketDashboard({market}:{market:Market}){
 const [dimension,setDimension]=useState<Dimension>('绿电买家');const [domestic,setDomestic]=useState(true);const [adjustment,setAdjustment]=useState(0);const [historical,setHistorical]=useState(false);
 const note=marketNotes[market];const summary=japanSummary(domestic);const data=evidence[market][dimension];const isHistorical=market==='台湾'&&dimension==='绿电买家';const rows=isHistorical&&!historical?[]:data.rows;
 return <div className="market-evidence">
  <div className="section-heading"><div><div className="eyebrow">OFFICIAL DATA & CUSTOMER INTELLIGENCE</div><h2>市场规模与重点客户</h2></div><span>人工核验快照 · {checkedAt}</span></div>
  <div className="evidence-intro"><strong>{note.status}</strong><p>{note.detail}</p><a href={note.url} target="_blank" rel="noreferrer">{note.association} <ExternalLink size={12}/></a><a href={note.backup} target="_blank" rel="noreferrer">查看统计 / 核验依据 <ExternalLink size={12}/></a><small>此模块独立于每日新闻采集更新；“检查最新数据”不会重新核验这些统计。</small></div>
  {market==='日本'?<>
   <div className="evidence-controls"><label>出货口径 <select value={domestic?'domestic':'total'} onChange={e=>setDomestic(e.target.value==='domestic')}><option value="domestic">日本国内出货（需求观察）</option><option value="total">调查总出货（含海外出货）</option></select></label><span>组件额定功率 · DC · 非并网装机</span></div>
   <div className="stats evidence-stats">{[
    ['2026自然年已披露累计',`${gw(summary.current)} GW`,'2026年1—6月，跨两个日本财年汇总'],
    ['累计同比（计算值）',`${summary.yoy>=0?'+':''}${summary.yoy.toFixed(1)}%`,'相较2025年1—6月，同口径原表计算'],
    ['最新季度出货',`${gw(jpQuarters[3][domestic?'domestic':'total'])} GW`,'2026年4—6月；官方同比指数95%（约−5%）'],
    ['2026全年官方预测','尚未核实','下方模型仅为2026财年情景测算']
   ].map(([label,value,description])=><section className="panel stat" key={label}><div className="stat-label">{label}</div><div className="stat-value date-stat">{value}</div><p className="stat-note">{description}</p></section>)}</div>
   <div className="evidence-grid"><section className="panel evidence-card"><h3>季度实绩对照</h3><p>两组同期分别比较；柱长以本表最大值为基准。</p>{jpQuarters.map(q=><div className="shipment-bar" key={q.period}><span>{q.period}</span><div><i style={{width:`${q[domestic?'domestic':'total']/1600000*100}%`}}/></div><a href={q.source} target="_blank" rel="noreferrer">{gw(q[domestic?'domestic':'total'])} GW ↗</a></div>)}<small>累计值计算：2026年1—3月 + 4—6月。7月以后尚无已核实公开季度值。</small></section>
   <section className="panel evidence-card"><div className="eyebrow">模型测算 · 非官方预测</div><h3>2026财年出货情景</h3><p>2026年4月—2027年3月，保留上年季度季节性，以最新Q1同比缩放全年。</p><div className="forecast-value">{gw(seasonalForecast(domestic,adjustment))} <small>GW</small></div><label className="scenario-label">全年基准调整 {adjustment>0?'+':''}{adjustment}%<input aria-label="出货情景调整百分比" type="range" min="-20" max="20" step="1" value={adjustment} onChange={e=>setAdjustment(Number(e.target.value))}/></label><p>公式：2025财年全年 ×（2026财年Q1 ÷ 2025财年Q1）×（1 + 调整比例）。单季度外推，不构成统计置信区间；政策、库存、调查样本变化均未建模。</p><a href={sources.jp25} target="_blank" rel="noreferrer">查看全年基期 <ExternalLink size={12}/></a></section></div>
  </>:<div className="stats evidence-stats">{['2026年组件累计出货','同期同比','2026全年官方预测'].map(label=><section className="panel stat" key={label}><div className="stat-label">{label}</div><div className="stat-value date-stat">待取得</div><p className="stat-note">未核实同口径原始数据；不以装机量或旧年份代填</p></section>)}</div>}
  <section className="panel evidence-card customer-panel"><div className="panel-title"><div><h2>客户地图 · 三个维度</h2><p>目标：各地区EPC、绿电买家、投资商前十。当前完成度按各表披露。</p></div><button className="secondary" onClick={()=>exportEvidence(market,dimension)}><ArrowDownToLine size={14}/>导出证据</button></div>
   <div className="customer-tabs" role="group" aria-label="客户维度">{(['EPC','绿电买家','投资商'] as Dimension[]).map(d=><button className={dimension===d?'chosen':''} key={d} onClick={()=>setDimension(d)}>{d}</button>)}</div>
   <h3>{data.title}</h3><p>{data.basis}</p><div className="rank-coverage">{data.coverage}</div>
   {isHistorical&&<label className="history-toggle"><input type="checkbox" checked={historical} onChange={e=>setHistorical(e.target.checked)}/>显示截至2023年9月的官方历史榜（非今年排名）</label>}
   {rows.length>0?<div className="evidence-table-wrap"><table className="evidence-table"><thead><tr><th>{data.ranked?'样本/历史名次':'地区名次'}</th><th>企业 / 平台</th><th>披露规模</th><th>统计期与范围</th><th>证据与局限</th></tr></thead><tbody>{rows.map((r,i)=><tr key={r.name}><td>{data.ranked?String(i+1).padStart(2,'0'):'未排名'}</td><td><strong>{r.name}</strong><small>{r.status}</small></td><td className="numeric">{r.value.toLocaleString('zh-CN')} {r.unit}</td><td>{r.period}<small>{r.scope}</small></td><td>{r.note}<a href={r.url} target="_blank" rel="noreferrer">原始出处 <ExternalLink size={12}/></a></td></tr>)}</tbody></table></div>:<p className="rank-empty">尚无已核实的2026年榜单。缺失不表示没有买家或业务机会。{isHistorical?'可主动展开历史榜，查看可追溯的客户线索。':''}</p>}
   <details className="ranking-method"><summary>排名规则与下一步核验</summary><p>EPC：按地区年度光伏完工MW排序，在建与订单另列。绿电买家：优先年度已交付GWh，其次单列已签PPA容量；可再生能源总量与光伏分开。投资商：按当地年度新增权益容量或已投资金额；币种、权益比例、时间必须一致。</p><p>项目开发商不自动等于EPC，买电企业不自动等于组件采购方。集团合并口径需要逐家确认；东急与东急不动产暂按报告主体分列。没有全国覆盖的表只称“已披露样本”，历史排名不作为今年结论。MOU、计划和已签合同不计作已完成实绩。</p><p>仍待完成：韩国/台湾2026出货统计及预测、三地2026年九份同口径前十榜。需要可公开核实的协会/政府表、招标结果、企业年报与项目权益数据，逐项补证。</p></details>
  </section>
 </div>;
}
