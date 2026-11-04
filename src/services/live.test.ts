import { describe, expect, it } from 'vitest';
import { news } from '../data/mock';
import { emptyFeed, liveReport, parseFeed, recentWeek } from './live';
describe('live feed safety and reporting',()=>{
 it('accepts a pending empty feed without substituting demo content',()=>{expect(parseFeed(emptyFeed).items).toEqual([])});
 it('rejects broken data and unsafe source URLs',()=>{expect(()=>parseFeed({...emptyFeed,items:[{...news[0],url:'javascript:alert(1)'}]})).toThrow();expect(()=>parseFeed({...emptyFeed,lastSuccessAt:'yesterday'})).toThrow();expect(()=>parseFeed({items:news})).toThrow()});
 it('uses Shanghai day boundaries and seven inclusive dates',()=>{const week=recentWeek(news,new Date('2026-11-03T17:00:00Z'));expect(week.start).toBe('2026-10-29');expect(week.end).toBe('2026-11-04');expect(week.items).toHaveLength(12)});
 it('does not fabricate a report for empty collection',()=>{const text=liveReport([],'日本','2026-10-29','2026-11-04');expect(text).toContain('暂无已采集情报');expect(text).toContain('未生成 AI 业务分析');expect(text).not.toContain('演示周报')});
});
