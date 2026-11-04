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
('日本経産省RSS','https://www.meti.go.jp/information/rss.xml'),
('日本経産省RSS一覧','https://www.meti.go.jp/information/rss/index.html'),
('日本経産省プレス','https://www.meti.go.jp/press/index.html'),
('日本資源エネルギー庁','https://www.enecho.meti.go.jp/rss.xml'),
('日本ソーラージャーナル','https://solarjournal.jp/feed/'),
('韓国政策ブリーフィング政策','https://www.korea.kr/rss/policy.xml'),
('韓国政府プレス','https://www.korea.kr/rss/pressrelease.xml'),
('韓国産業ニュース','https://www.industrynews.co.kr/rss/allArticle.xml'),
('韓国電気新聞','https://www.electimes.com/rss/allArticle.xml'),
('韓国エネルギーデイリー','https://www.energydaily.co.kr/rss/allArticle.xml'),
('台湾経済部RSS','https://www.moea.gov.tw/Mns/populace/news/Rss.aspx?kind=1&menu_id=40'),
('台湾経済部公告','https://www.moea.gov.tw/Mns/populace/news/News.aspx?kind=1&menu_id=40'),
('台湾能源署RSS','https://www.moeaea.gov.tw/ECW/rss/Rss.aspx?kind=1&menu_id=41'),
('台湾能源署公告','https://www.moeaea.gov.tw/ECW/populace/news/News.aspx?kind=1&menu_id=41'),
('台湾科技新報能源','https://technews.tw/category/energy/feed/'),
('LONGi日本','https://www.longi.com/jp/news/'),
('Trina日本','https://www.trinasolar.com/jp/resources/newsroom'),
('Qcells韓国','https://www.qcells.com/kr/'),
]
def inspect(entry):
 name,url=entry;result={'name':name,'url':url}
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'NorthAsiaSolarIntelligence/0.3 source-validation','Accept':'application/rss+xml,application/xml,text/html'})
  with urllib.request.urlopen(req,timeout=18) as r:
   data=r.read(2_000_000);result.update(status=r.status,finalURL=r.url)
  try:
   root=ET.fromstring(data);result['xmlRoot']=root.tag;entries=root.findall('.//item') or root.findall('{http://www.w3.org/2005/Atom}entry')
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
  with urllib.request.urlopen(req,timeout=30) as r:d=json.loads(r.read());model.update(status=r.status,text=d['choices'][0]['message']['content'])
 except Exception as e:model.update(error=type(e).__name__,status=getattr(e,'code',None))
Path('.deploy/source-probe.json').write_text(json.dumps({'sources':results,'model':model},ensure_ascii=False,indent=2)+'\n')
print('Source probes complete. Safe results saved; credential values never logged.')
