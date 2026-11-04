"""Check official/local-language endpoints before enabling them as sources."""
import concurrent.futures
import json
import os
from pathlib import Path
import re
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
CANDIDATES=[
('日本環境省RSS','https://www.env.go.jp/rss/news.xml'),
('日本環境省発表','https://www.env.go.jp/press/'),
('東京都政府RSS','https://www.metro.tokyo.lg.jp/rss/index.rdf'),
('NEDO発表','https://www.nedo.go.jp/news/press/index.html'),
('韓国政府トップ','https://www.korea.kr/main.do'),
('韓国政府RSS案内','https://www.korea.kr/etc/rss.do'),
('韓国政府政策RSS','https://www.korea.kr/rss/policy.xml'),
('台湾経済部RSS案内','https://www.moea.gov.tw/Mns/populace/news/NewsRSS.aspx?menu_id=1430'),
('台湾能源署RSS案内','https://www.moeaea.gov.tw/ECW/populace/news/NewsRSS.aspx?menu_id=819'),
('台湾科技新報全体','https://technews.tw/feed/'),
('Trina日本発表','https://www.trinasolar.com/jp/press-releases/'),
('Qcells韓国ニュース','https://www.qcells.com/kr/stay-in-the-loop/trending-news'),
]

def inspect(entry):
 name,url=entry;result={'name':name,'url':url}
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'NorthAsiaSolarIntelligence/0.3 source-validation','Accept':'application/rss+xml,application/xml,text/html'})
  with urllib.request.urlopen(req,timeout=18) as r:
   data=r.read(2_000_000);result.update(status=r.status,finalURL=r.url)
  try:
   root=ET.fromstring(data);result['xmlRoot']=root.tag;
   if root.tag.endswith('html'):raise ET.ParseError()
   entries=root.findall('.//item') or root.findall('{http://www.w3.org/2005/Atom}entry')
   result['entries']=len(entries);result['examples']=[{'title':e.findtext('title') or e.findtext('{http://www.w3.org/2005/Atom}title'),'date':e.findtext('pubDate') or e.findtext('{http://purl.org/dc/elements/1.1/}date')} for e in entries[:3]]
  except ET.ParseError:
   text=data.decode('utf-8','replace');result['title']=re.findall(r'<title[^>]*>(.*?)</title>',text,re.S)[:1]
   links=re.findall(r'href=[\"\']([^\"\']+)[\"\']',text,re.I)
   result['feedLinks']=[l for l in links if re.search('rss|rdf|atom|feed',l,re.I)][:12]
   result['newsLinks']=[l for l in links if re.search('press|news|article|view|idxno',l,re.I)][:10]
 except Exception as e:result.update(error=type(e).__name__,status=getattr(e,'code',None))
 return result
results=list(concurrent.futures.ThreadPoolExecutor(max_workers=6).map(inspect,CANDIDATES))
model={'configured':bool(os.environ.get('GITHUB_TOKEN'))}
if model['configured']:
 try:
  payload={'model':'openai/gpt-4.1-mini','messages':[{'role':'user','content':'请只用中文回答：太阳能。'}],'max_tokens':30,'temperature':0}
  req=urllib.request.Request('https://models.github.ai/inference/chat/completions',data=json.dumps(payload).encode(),headers={'Authorization':'Bearer '+os.environ['GITHUB_TOKEN'],'Content-Type':'application/json'})
  with urllib.request.urlopen(req,timeout=30) as r:
   body=r.read();model.update(status=r.status,finalURL=r.url,contentType=r.headers.get('Content-Type'));
   if 'json' in r.headers.get('Content-Type',''):
    d=json.loads(body);model['text']=d.get('choices',[{}])[0].get('message',{}).get('content');model['errorCode']=d.get('error',{}).get('code')
   else:model['pageTitle']=re.findall(r'<title[^>]*>(.*?)</title>',body.decode('utf-8','replace'),re.S)[:1]
 except Exception as e:model.update(error=type(e).__name__,status=getattr(e,'code',None))
Path('.deploy/source-probe.json').write_text(json.dumps({'sources':results,'model':model},ensure_ascii=False,indent=2)+'\n')
print('Source probes complete. Safe results saved; credential values never logged.')
