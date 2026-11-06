import React from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { describe, it, expect } from 'vitest';
import ManufacturerShipments from '../ManufacturerShipments';
import { shipmentDisclosures, shipmentRows, estimatedMw, annualCoverage } from '../data/manufacturerShipments';
describe('shipment disclosure scope and uncertainty',()=>{
 it('keeps implied Jinko volume separate from directly disclosed quantities',()=>{const r=shipmentDisclosures.find(x=>x.id==='jp-jinko-2025')!;expect(r.mw).toBeNull();expect(estimatedMw(r)).toBe(1311);const html=renderToStaticMarkup(<ManufacturerShipments market="日本"/>);expect(html).not.toContain('1.31 GW');expect(html).toContain('未经独立核实，可能不准确');});
 it('never fills current-year ranking with historical or cumulative records',()=>{for(const market of ['日本','韩国','台湾'] as const){expect(shipmentRows(market,'2026')).toEqual([]);expect(annualCoverage(market,'2026')).toEqual({companies:0,quantified:0});}});
 it('preserves Korean foreign-brand claim without a fabricated period or volume',()=>{const [r]=shipmentRows('韩国');expect(r.scope).toBe('统计期未明确');expect(r.mw).toBeNull();expect(r.rankScope).toContain('非全市场');});
 it('does not merge TSEC worldwide sales into Taiwan shipment ranking',()=>{const ranking=shipmentRows('台湾','2024').filter(r=>r.scope==='地区年度');expect(ranking).toHaveLength(5);expect(ranking.every(r=>r.mw===null)).toBe(true);const tsec=shipmentDisclosures.find(r=>r.id==='tw-tsec-2024-all')!;expect(tsec.mw).toBe(389);expect(tsec.rank).toBeNull();});
 it('does not treat the order of Taiwan leaders as a ranking',()=>{const rows=shipmentRows('台湾','2025');expect(rows).toHaveLength(4);expect(rows.every(r=>r.rank===null&&r.mw===null)).toBe(true);});
 it('exports only usable provenance, with unique records and source type filters',()=>{expect(new Set(shipmentDisclosures.map(r=>r.id)).size).toBe(shipmentDisclosures.length);for(const r of shipmentDisclosures){expect(r.url).toMatch(/^https:\/\//);expect(r.publisher).toBeTruthy();expect(r.note).toBeTruthy();}expect(shipmentRows('日本','all','行业媒体').map(r=>r.id)).toEqual(['jp-jinko-2024']);});
});
