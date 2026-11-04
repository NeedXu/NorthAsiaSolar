"""Build a minimal shutdown deployment containing no application or news data."""
import json
from pathlib import Path
import re
import urllib.parse
import urllib.request
ROOT=Path(__file__).resolve().parents[1]
def build():
    state=json.loads((ROOT/'.deploy/site-status.json').read_text())
    url=state['url']
    parsed=urllib.parse.urlsplit(url)
    if parsed.scheme!='https' or not parsed.hostname or not parsed.hostname.endswith('.github.io'):raise ValueError('Invalid site URL')
    with urllib.request.urlopen(url,timeout=20) as response:html=response.read(2_000_000).decode()
    assets=[]
    for path in re.findall(r'(?:src|href)=[\"\']([^\"\']+\.(?:js|css))[\"\']',html):
        absolute=urllib.parse.urljoin(url,path)
        target=urllib.parse.urlsplit(absolute)
        if target.netloc==parsed.netloc and target.path.startswith(parsed.path): assets.append(absolute)
    (ROOT/'.deploy/prior-assets.json').write_text(json.dumps(assets)+'\n')
    out=ROOT/'dist'
    if out.exists() and any(out.iterdir()):raise ValueError('Shutdown artifact directory must be empty')
    out.mkdir(exist_ok=True)
    page='''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex,nofollow,noarchive"><title>访问已关闭</title><style>body{background:#101c2e;color:#e0eee9;font:16px system-ui;display:grid;place-items:center;min-height:95vh;margin:0}main{padding:30px;max-width:500px;text-align:center}h1{font-size:28px}p{color:#a1b7b1;line-height:1.9}</style></head><body><!-- NORTH_ASIA_ACCESS_CLOSED --><main><h1>访问已关闭</h1><p>网站所有者已暂停公开访问。<br>当前不提供情报页面或新闻数据。</p></main></body></html>'''
    (out/'index.html').write_text(page)
    (out/'404.html').write_text(page)
    print(f'Prepared shutdown artifact; {len(assets)} prior assets will be checked for removal.')
if __name__=='__main__':build()
