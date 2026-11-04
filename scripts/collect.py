"""Collect public RSS metadata; no full-text scraping, invented summaries or credentials."""
import datetime as dt
import email.utils
import hashlib
import html
import json
import os
from pathlib import Path
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SOURCES = [
    {"name": "PV magazine", "url": "https://www.pv-magazine.com/feed/"},
    {"name": "PV Tech", "url": "https://www.pv-tech.org/feed/"},
]
MARKETS = {"日本": r"\bjapan(?:ese)?\b|日本", "韩国": r"\bkorea(?:n)?\b|韩国|韓国", "台湾": r"\btaiwan(?:ese)?\b|台湾|臺灣"}
TECH = {"N型TOPCon": r"topcon", "BC": r"back.contact|\bbc\b", "HJT": r"heterojunction|\bhjt\b", "钙钛矿叠层": r"perovskite|tandem", "住宅屋顶组件": r"residential|rooftop", "轻量化组件": r"lightweight", "防眩光组件": r"anti.glare", "数据中心光伏应用": r"data.cent(?:er|re)"}

def clean(text):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]*>", " ", text or ""))).strip()

def canonical(url):
    p = urllib.parse.urlsplit(url)
    if p.scheme != "https" or not p.hostname or p.username or p.password:
        raise ValueError("invalid article URL")
    query = [(k, v) for k, v in urllib.parse.parse_qsl(p.query) if not k.lower().startswith("utm_") and k.lower() not in {"fbclid", "gclid"}]
    return urllib.parse.urlunsplit((p.scheme, p.netloc.lower(), p.path or "/", urllib.parse.urlencode(sorted(query)), ""))

def parse_feed(xml, source, now):
    if b"<!DOCTYPE" in xml.upper() or b"<!ENTITY" in xml.upper():
        raise ValueError("XML declarations not supported")
    root = ET.fromstring(xml)
    entries = root.findall("./channel/item")
    if root.tag != "rss" or root.find("channel") is None:
        raise ValueError("expected RSS channel")
    rows = []
    for item in entries:
        title = clean(item.findtext("title"))[:600]
        excerpt = clean(item.findtext("description"))[:1200]
        # Country must occur in the headline: do not assign a country from a passing mention.
        matched = [market for market, pattern in MARKETS.items() if re.search(pattern, title, re.I)]
        if not title or not matched:
            continue
        try:
            url = canonical(item.findtext("link") or "")
            published = email.utils.parsedate_to_datetime(item.findtext("pubDate") or "")
            if published.tzinfo is None:
                continue
            published = published.astimezone(dt.timezone.utc)
            if published > now + dt.timedelta(hours=24) or published < now - dt.timedelta(days=90):
                continue
        except (ValueError, TypeError, OverflowError):
            continue
        text = title + " " + excerpt
        topic = "市场趋势"
        if re.search(r"policy|subsid|tariff|auction|government|regulat", title, re.I):
            topic = "政策与补贴"
        elif re.search(r"longi|trina|ja solar|canadian solar|qcells|hanwha", title, re.I):
            topic = "竞争动态"
        elif re.search(r"efficiency|cell|perovskite|topcon|hjt|back.contact", title, re.I):
            topic = "技术创新"
        tech = next((name for name, pattern in TECH.items() if re.search(pattern, text, re.I)), "未分类")
        for market in matched:
            rows.append({"id": hashlib.sha256((market+url).encode()).hexdigest()[:24], "market": market, "title": title,
                "date": published.astimezone(dt.timezone(dt.timedelta(hours=8))).date().isoformat(), "publishedAt": published.isoformat(),
                "topic": topic, "priority": "高" if topic == "政策与补贴" else "中", "source": source["name"], "url": url,
                "summary": "原始 RSS 摘录（未翻译）：" + (excerpt or "来源未提供摘要，请阅读原文。"),
                "importance": "待核实：主题和优先级由关键词规则标记，不代表已确认的商业重要性。",
                "impact": "尚未生成晶科业务影响分析，请结合原文及当地业务情况判断。",
                "watch": "核对原文、发布日期、政策适用范围与实施时间。", "tech": tech,
                "dataKind": "live", "analysisKind": "rules", "collectedAt": now.isoformat()})
    return rows

def merge(previous, incoming):
    by_url = {}
    for row in previous + incoming:
        by_url[(row["market"], canonical(row["url"]))] = row
    result = []
    titles = set()
    for row in sorted(by_url.values(), key=lambda n: (n["publishedAt"], n["id"]), reverse=True):
        key = (row["market"], clean(row["title"]).casefold())
        if key not in titles:
            result.append(row)
            titles.add(key)
    return result[:3000]

def fetch(source):
    req = urllib.request.Request(source["url"], headers={"User-Agent": "NorthAsiaSolarIntelligence/0.2 RSS-reader", "Accept": "application/rss+xml, application/xml, text/xml"})
    with urllib.request.urlopen(req, timeout=30) as response:
        # Redirects must remain HTTPS. urllib uses platform trust and existing proxies.
        if not response.url.startswith("https://"):
            raise ValueError("non-HTTPS redirect")
        data = response.read(2_000_001)
        if len(data) > 2_000_000:
            raise ValueError("feed exceeds size limit")
        return data

def run(path):
    now = dt.datetime.now(dt.timezone.utc)
    previous = json.loads(path.read_text()) if path.exists() else {"items": [], "lastSuccessAt": None}
    incoming, status = [], []
    for source in SOURCES:
        try:
            rows = parse_feed(fetch(source), source, now)
            incoming.extend(rows)
            status.append({"name": source["name"], "url": source["url"], "state": "ok", "matched": len(rows)})
        except Exception as error:
            # Never include raw request/response bodies or credential-bearing URLs in logs.
            print(f'{source["name"]}: {type(error).__name__}', file=sys.stderr)
            status.append({"name": source["name"], "url": source["url"], "state": "error", "error": type(error).__name__})
    success = all(s["state"] == "ok" for s in status)
    payload = {"schemaVersion": 1, "mode": "live", "attemptedAt": now.isoformat(),
        "lastSuccessAt": now.isoformat() if success else previous.get("lastSuccessAt"),
        "status": "ok" if success else "partial" if incoming else "error", "sources": status,
        "items": merge(previous["items"], incoming)}
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2)+"\n")
    os.replace(temporary, path)
    print(f'Archive contains {len(payload["items"])} items; source status: {payload["status"]}')
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(run(Path(os.environ.get("FEED_OUTPUT", ROOT / "public/data/feed.json"))))
