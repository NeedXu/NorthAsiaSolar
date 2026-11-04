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
('台湾経済部公式RSS','https://www.moea.gov.tw/Mns/populace/news/NewsRSSdetail.aspx?Kind=1'),
('台湾能源署公式RSS','https://www.moeaea.gov.tw/ECW/populace/news/NewsRSSdetail.aspx?Kind=1'),
('韓国政府政策一覧','https://www.korea.kr/news/policyNewsList.do'),
('Trina日本RSS','https://www.trinasolar.com/jp/feed/'),
('日本環境省発表','https://www.env.go.jp/press/'),
('無料翻訳モデルライセンス','https://huggingface.co/facebook/m2m100_418M/raw/main/README.md'),
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
   result['newsLinks']=[l for l in links if re.search('press|news|article|view|idxno',l,re.I)][:20]
   result['articleExamples']=[{'url':m.group(1),'context':re.sub('<[^>]+>',' ',text[max(0,m.start()-150):m.end()+400])} for m in re.finditer(r'href=[\"\']([^\"\']*(?:policyNewsView|press_[0-9]|news_id)[^\"\']*)[\"\']',text,re.I)][:4]
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
   else:
    preview=body.decode('utf-8','replace')[:800].replace(os.environ['GITHUB_TOKEN'],'[redacted]');model['responsePreview']=preview
 except Exception as e:model.update(error=type(e).__name__,status=getattr(e,'code',None))
Path('.deploy/source-probe.json').write_text(json.dumps({'sources':results,'model':model},ensure_ascii=False,indent=2)+'\n')
print('Source probes complete. Safe results saved; credential values never logged.')
