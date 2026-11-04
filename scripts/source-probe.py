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
('韩国政府政策检索表单','https://www.korea.kr/news/policyNewsList.do'),
('台湾能源署业务公告RSS','https://www.moeaea.gov.tw/ECW/populace/news/NewsRSSdetail.aspx?Kind=2'),
('台湾能源署招标/补助RSS','https://www.moeaea.gov.tw/ECW/populace/news/NewsRSSdetail.aspx?Kind=3'),
]

def inspect(entry):
 name,url=entry;result={'name':name,'url':url}
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'NorthAsiaSolarIntelligence/0.3 source-validation','Accept':'application/rss+xml,application/xml,text/html'})
  with urllib.request.urlopen(req,timeout=18) as r:
   data=r.read(2_000_000);result.update(status=r.status,finalURL=r.url)
  if name=='公开网页翻译响应验证':result['translationResponse']=data.decode('utf-8','replace')[:1500]
  try:
   root=ET.fromstring(data);result['xmlRoot']=root.tag;
   if root.tag.endswith('html'):raise ET.ParseError()
   entries=root.findall('.//item') or root.findall('{http://www.w3.org/2005/Atom}entry')
   result['entries']=len(entries);result['examples']=[{'title':e.findtext('title') or e.findtext('{http://www.w3.org/2005/Atom}title'),'date':e.findtext('pubDate') or e.findtext('{http://purl.org/dc/elements/1.1/}date')} for e in entries[:3]]
  except ET.ParseError:
   text=data.decode('utf-8','replace');result['title']=re.findall(r'<title[^>]*>(.*?)</title>',text,re.S)[:1]
   links=re.findall(r'href=[\"\']([^\"\']+)[\"\']',text,re.I)
   from html.parser import HTMLParser
   class Forms(HTMLParser):
    def __init__(self):super().__init__();self.fields=[]
    def handle_starttag(self,tag,attrs):
     d=dict(attrs)
     if tag=='form':self.fields.append({'formAction':d.get('action')})
     if tag in ('input','select') and d.get('name'):self.fields.append({'name':d['name'],'type':d.get('type','select')})
   forms=Forms();forms.feed(text);result['formFields']=forms.fields
   result['feedLinks']=[l for l in links if re.search('rss|rdf|atom|feed',l,re.I)][:12]
   result['newsLinks']=[l for l in links if re.search('press|news|article|view|idxno',l,re.I)][:20]
   result['articleExamples']=[{'url':m.group(1),'context':re.sub('<[^>]+>',' ',text[max(0,m.start()-150):m.end()+400])} for m in re.finditer(r'href=[\"\']([^\"\']*(?:policyNewsView|press_[0-9]|news_id)[^\"\']*)[\"\']',text,re.I)][:4]
 except Exception as e:result.update(error=type(e).__name__,status=getattr(e,'code',None))
 return result
results=list(concurrent.futures.ThreadPoolExecutor(max_workers=6).map(inspect,CANDIDATES))
model={'configured':False,'note':'Use local MIT-licensed model; do not call the nonfunctional model API'}
Path('.deploy/source-probe.json').write_text(json.dumps({'sources':results,'model':model},ensure_ascii=False,indent=2)+'\n')
print('Source probes complete. Safe results saved; credential values never logged.')
