import type { Intelligence } from '../data/mock';
export interface Feed { schemaVersion:1;mode:'live';attemptedAt:string|null;lastSuccessAt:string|null;status:'pending'|'ok'|'partial'|'error';sources:{name:string;url:string;state:'ok'|'error';matched?:number;error?:string}[];items:Intelligence[] }
export const emptyFeed:Feed={schemaVersion:1,mode:'live',attemptedAt:null,lastSuccessAt:null,status:'pending',sources:[],items:[]};
export function parseFeed(value:unknown):Feed{
 const v=value as Feed;
 const date=(x:unknown)=>x===null||(typeof x==='string'&&Number.isFinite(Date.parse(x)));
 const safeURL=(url:unknown)=>{try{const u=new URL(String(url));return u.protocol==='https:'&&!u.username&&!u.password}catch{return false}};
 if(!v||v.schemaVersion!==1||v.mode!=='live'||!['pending','ok','partial','error'].includes(v.status)||!date(v.lastSuccessAt)||!date(v.attemptedAt)||!Array.isArray(v.sources)||!Array.isArray(v.items))throw Error('数据格式不兼容');
 if(v.items.some(n=>!n||!['日本','韩国','台湾'].includes(n.market)||!['政策与补贴','市场趋势','竞争动态','技术创新'].includes(n.topic)||!['高','中'].includes(n.priority)||!['id','title','date','source','summary','importance','impact','watch','tech'].every(k=>typeof n[k as keyof Intelligence]==='string')||!/^\d{4}-\d{2}-\d{2}$/.test(n.date)||!safeURL(n.url)))throw Error('新闻数据校验失败');
 if(v.sources.some(s=>!s||typeof s.name!=='string'||!['ok','error'].includes(s.state)||!safeURL(s.url)))throw Error('来源数据校验失败');
 return v;
}
export function dateInShanghai(now:Date){return new Intl.DateTimeFormat('en-CA',{timeZone:'Asia/Shanghai',year:'numeric',month:'2-digit',day:'2-digit'}).format(now)}
export function recentWeek(items:Intelligence[],now=new Date()){
 const end=dateInShanghai(now);const start=dateInShanghai(new Date(now.getTime()-6*86400000));
 return {start,end,items:items.filter(n=>n.date>=start&&n.date<=end)};
}
export function liveReport(items:Intelligence[],scope:string,start:string,end:string){
 return `# 北亚光伏市场周报\n\n周期：${start} — ${end}（北京时间）\n市场：${scope}\n\n数据来自公开 RSS；摘要保留来源语言。规则分类未经人工复核；未生成 AI 业务分析。\n\n${items.length?items.map(n=>`## ${n.market}｜${n.title}\n\n- 日期：${n.date}\n- 来源：${n.source}\n- 摘录：${n.summary}\n- 核实建议：${n.watch}\n- 原文：${n.url}\n`).join('\n'):'本周期暂无已采集情报，不代表市场没有事件。'}\n`;
}
