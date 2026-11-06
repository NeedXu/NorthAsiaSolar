import React from 'react';
import { describe, it, expect } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';
import MarketDashboard from '../MarketDashboard';
import { japanSummary, seasonalForecast, evidence } from '../data/marketEvidence';
describe('official shipment period calculations',()=>{
 it('combines calendar half-years across Japanese fiscal years with exact kW',()=>{expect(japanSummary().current).toBe(2753328);expect(japanSummary().previous).toBe(2546440);expect(japanSummary().yoy).toBeCloseTo(8.1246,3);expect(japanSummary(false).current).toBe(2774840);});
 it('uses prior fiscal seasonality instead of multiplying Q1 by four',()=>{expect(seasonalForecast()).toBeCloseTo(6186052*1204233/1273701);expect(seasonalForecast(true,10)/seasonalForecast()).toBeCloseTo(1.1);expect(seasonalForecast(false,-20)/seasonalForecast(false)).toBeCloseTo(.8);});
});
describe('ranking provenance and incomplete coverage',()=>{
 it('keeps history out of the default current-year table',()=>{const html=renderToStaticMarkup(<MarketDashboard market="台湾"/>);expect(html).toContain('非今年排名');expect(html).not.toContain('<td><strong>台积电');expect(html).toContain('尚无已核实的2026年榜单');});
 it('never presents noncomparable project clues as national ranks',()=>{for(const market of Object.values(evidence)){for(const dim of ['EPC','投资商'] as const){expect(market[dim].ranked).toBe(false);expect(market[dim].coverage).toContain('不赋予地区名次');}}});
 it('keeps Japanese sample ranking and capacities separate from delivery volumes',()=>{const data=evidence.日本.绿电买家;expect(data.rows).toHaveLength(10);expect(data.coverage).toContain('非政府或协会全国排名');expect(data.rows.find(r=>r.name==='Amazon')?.value).toBe(65);expect(data.rows.find(r=>r.name==='JR East')?.value).toBe(58.6);for(let i=1;i<data.rows.length;i++)expect(data.rows[i-1].value).toBeGreaterThanOrEqual(data.rows[i].value);});
 it('shows missing Korean statistics explicitly rather than Japanese numbers',()=>{const html=renderToStaticMarkup(<MarketDashboard market="韩国"/>);expect(html).toContain('2026年12月');expect(html).not.toContain('2.753');});
});
