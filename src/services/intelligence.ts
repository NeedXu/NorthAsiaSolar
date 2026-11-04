import { news, type Intelligence, type Market } from '../data/mock';
export interface NewsFilter { market?:Market; topic?:string; search?:string; priority?:string; from?:string; to?:string }
// Replace this adapter with an authenticated API client when a backend is available.
export interface IntelligenceRepository { list(filter:NewsFilter):Promise<Intelligence[]> }
export function filterNews(items:Intelligence[], f:NewsFilter) {
 return items.filter(n=>(!f.market||n.market===f.market)&&(!f.topic||n.topic===f.topic)&&(!f.priority||n.priority===f.priority)&&(!f.from||n.date>=f.from)&&(!f.to||n.date<=f.to)&&(!f.search||`${n.title} ${n.summary} ${n.source} ${n.tech}`.toLowerCase().includes(f.search.toLowerCase())));
}
export function deduplicate(items:Intelligence[]) { return [...new Map(items.map(n=>[`${n.market}:${n.title.trim().toLowerCase()}`,n])).values()]; }
export const mockRepository:IntelligenceRepository={async list(filter){return filterNews(deduplicate(news),filter)}};
export function weeklyReport(items:Intelligence[], market:string) {
 return `# 北亚光伏市场周报\n\n> 演示周报 · 本地模拟数据，非实时新闻或市场预测\n\n周期：2026-10-29 — 2026-11-04\n市场：${market}\n\n${items.map(n=>`## ${n.market}｜${n.title}\n\n- 发生了什么：${n.summary}\n- 为什么重要：${n.importance}\n- 对晶科业务的影响：${n.impact}\n- 建议关注：${n.watch}\n- 参考机构主页（非新闻原文）：${n.url}\n`).join('\n')}\n## 下周关注\n\n核实政策原文、渠道需求与竞争产品认证进度。所有示例结论须经真实数据验证。`;
}
