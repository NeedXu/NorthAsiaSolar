import { describe, expect, it } from 'vitest';
import { news } from '../data/mock';
import { deduplicate, filterNews, mockRepository, weeklyReport } from './intelligence';
describe('local intelligence workflow',()=>{
 it('isolates all three markets',async()=>{for(const market of ['日本','韩国','台湾'] as const){const rows=await mockRepository.list({market});expect(rows).toHaveLength(4);expect(rows.every(n=>n.market===market)).toBe(true)}});
 it('combines topic, keyword, date and priority filters',()=>{const rows=filterNews(news,{market:'日本',topic:'市场趋势',search:'屋顶',priority:'高',from:'2026-11-04',to:'2026-11-04'});expect(rows.map(n=>n.id)).toEqual(['0-0']);expect(filterNews(news,{from:'2027-01-01'})).toEqual([])});
 it('deduplicates repeated articles within a market',()=>{expect(deduplicate([...news,news[0]])).toHaveLength(12)});
 it('exports business analysis with explicit mock and source labels',()=>{const rows=filterNews(news,{market:'韩国'});const report=weeklyReport(rows,'韩国');expect(report).toContain('本地模拟数据');expect(report).toContain('对晶科业务的影响');expect(report).toContain('https://www.qcells.com/');expect(report).not.toContain('日本｜');expect(report.match(/^## 韩国/gm)).toHaveLength(4)});
});
