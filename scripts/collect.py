"""Original-language PV intelligence. Classifications are evidence cues, not legal conclusions."""
import concurrent.futures
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
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]
SOURCES=json.loads((ROOT/'scripts/sources.json').read_text())
MARKETS={'日本':r'\bjapan(?:ese)?\b|日本|일본|東京|東京都|千葉|大阪|北海道|九州','韩国':r'\bkorea(?:n)?\b|韩国|韓国|한국|국내|서울|경기도','台湾':r'\btaiwan(?:ese)?\b|台湾|臺灣|台灣|대만|台北|臺北|台南|高雄'}
PV=r'太陽光|太陽能|太阳能|光伏|ソーラー|太陽電池|(?:光電|光电).{0,14}(?:發電|发电|屋頂|屋顶|系統|系统|案場|案场|設置|政策|補助|補貼|併網|開發)|(?:屋頂|屋顶|地面|農地|漁電).{0,10}(?:光電|光电)|태양광|태양전지|solar|photovoltaic|perovskite|ペロブスカイト|페로브스카이트|TOPCon|HJT'
BRANDS=r'longi|隆基|ロンジ|trina|天合|トリナ|ja solar|晶澳|canadian solar|阿特斯|カナディアン|qcells|큐셀|한화|ハンファ|シャープ|sharp|カネカ|kaneka|聯合再生|聯合再生|元晶|茂迪|현대에너지솔루션'
POLICY=r'政策|制度|補助|補貼|补贴|助成|法案|法律|規制|規則|入札|買取|FIT|FIP|지원|정책|보조금|규제|법안|입찰|policy|subsid|tariff|regulat'
TECH={'N型TOPCon':r'topcon','BC':r'back.contact|\bbc\b|バックコンタクト','HJT':r'heterojunction|\bhjt\b','钙钛矿叠层':r'perovskite|tandem|ペロブスカイト|페로브스카이트','住宅屋顶组件':r'residential|rooftop|屋根|屋頂|屋顶|지붕','轻量化组件':r'lightweight|軽量|輕量|경량','防眩光组件':r'anti.glare|防眩|반사','数据中心光伏应用':r'data.cent(?:er|re)|データセンター|데이터센터|資料中心'}
EVENTS=[('合作意向/MOU',r'\bmou\b|memorandum|覚書|業務提携|업무협약|合作备忘录|合作備忘錄'),('购电协议/PPA',r'\bppa\b|電力購入|전력구매|购电协议|購電協議'),('项目竣工/投运',r'竣工|投運|投运|運転開始|稼働開始|준공|상업운전|commissioned|completed'),('项目签约/建设',r'着工|建設|签约|簽約|기공|착공|construction'),('合作/供货',r'合作|提携|締結|협력|공급|partner|collaborat|supply|供給'),('产品/技术发布',r'新製品|新商品|発表|発売|製品|신제품|출시|제품|新产品|新產品|推出|launch|unveil|product')]

def clean(text):return re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]*>',' ',text or ''))).strip()
def canonical(url):
 p=urllib.parse.urlsplit(html.unescape(url))
 if p.scheme!='https' or not p.hostname or p.username or p.password:raise ValueError('invalid article URL')
 query=[(k,v) for k,v in urllib.parse.parse_qsl(p.query) if not k.lower().startswith('utm_') and k.lower() not in {'fbclid','gclid','pwise','pwisesub','pwisemain'}]
 return urllib.parse.urlunsplit((p.scheme,p.netloc.lower(),p.path or '/',urllib.parse.urlencode(sorted(query)),''))
def date_value(value,source):
 value=clean(value)
 try:date=email.utils.parsedate_to_datetime(value)
 except (ValueError,TypeError):
  try:date=dt.datetime.fromisoformat(value.replace('Z','+00:00'))
  except ValueError:
   m=re.search(r'(\d{3,4})[年년./-]\s*(\d{1,2})[月월./-]\s*(\d{1,2})',value)
   if not m:raise ValueError('missing publication date')
   y,mth,day=map(int,m.groups());date=dt.datetime(y+1911 if y<1911 else y,mth,day)
 if date.tzinfo is None:
  if 'timezone' not in source:raise ValueError('ambiguous publication timezone')
  date=date.replace(tzinfo=dt.timezone(dt.timedelta(hours=source['timezone'])))
 return date.astimezone(dt.timezone.utc)
def valid_date(value,source,now):
 date=date_value(value,source)
 if date>now+dt.timedelta(hours=24) or date<now-dt.timedelta(days=90):raise ValueError('outside archive window')
 return date

def fetch(source):
 url=source['url'] if isinstance(source,dict) else source
 req=urllib.request.Request(url,headers={'User-Agent':'NorthAsiaSolarIntelligence/0.3 public-news-reader','Accept':'application/rss+xml,application/xml,text/html'})
 with urllib.request.urlopen(req,timeout=25) as response:
  if not response.url.startswith('https://'):raise ValueError('non-HTTPS redirect')
  data=response.read(2_000_001)
  if len(data)>2_000_000:raise ValueError('response exceeds size limit')
  return data

def article_document(data):
 soup=BeautifulSoup(data,'html.parser')
 dates=[]
 for tag in soup.select('meta[property="article:published_time"],meta[name="date"],meta[name="pubdate"],meta[name="publishdate"],meta[name="DC.date.issued"],meta[name="DC.date"],time[datetime],.article-date,.view-date,.view_date,.view_info .date,p.date,span.date'):
  dates.append(tag.get('content') or tag.get('datetime') or tag.get_text(' ',strip=True))
 # JSON-LD publication time is metadata, never executed as code.
 for script in soup.select('script[type="application/ld+json"]'):
  for match in re.findall(r'"datePublished"\s*:\s*"([^"]+)"',script.get_text()):dates.append(match)
 for bad in soup.select('script,style,nav,header,footer,noscript,form,iframe'):bad.decompose()
 title=clean(soup.h1.get_text(' ',strip=True)) if soup.h1 else ''
 body=soup.select_one('article') or soup.select_one('#contentBody') or soup.select_one('.view_cont') or soup.select_one('.article-view-content-div') or soup.select_one('main') or soup.body or soup
 text=clean(body.get_text(' ',strip=True))[:18000]
 if not dates:dates=[text[:900]]
 return title,text,dates

def cue(text,pattern):
 for sentence in re.split(r'(?<=[。！？!?])|\n',text):
  match=re.search(pattern,sentence,re.I)
  if match:
   start=max(0,match.start()-120);return sentence[start:match.end()+220][:380].strip()
 return ''
def signals(text,source):
 event='政策公告' if source.get('sourceType')=='government' and re.search(POLICY,text,re.I) else '市场/企业动态'
 evidence=''
 for name,pattern in EVENTS:
  found=cue(text,pattern)
  if found:
   event=name;evidence=found;break
 if source.get('sourceType')=='government' and re.search(POLICY,text,re.I):event='政策公告'
 if event=='项目竣工/投运' and re.search(r'予定|計画|계획|예정|计划|計畫|预计|預計|planned|expected|will',evidence,re.I):event='项目计划（待核实）'
 direction='未判定';policy_quote=''
 if source.get('sourceType')=='government':
  for sentence in re.split(r'(?<=[。！？!?])',text):
   if not re.search(PV,sentence,re.I):continue
   support=bool(re.search(r'補助|補貼|补贴|助成|지원|보조금|subsid|grant',sentence,re.I))
   restrict=bool(re.search(r'廃止|終了|縮小|停止|禁止|対象外|しない|行わない|不予|不再|제한|폐지|축소|중단|지원하지|제외|하지 않|取消|撤銷|下修|end of|terminate|ban\b|phase.out',sentence,re.I))
   if support or restrict:
    direction='混合线索' if support and restrict else '支持线索' if support else '限制线索'
    policy_quote=cue(sentence,PV);break
 return event,evidence,direction,policy_quote

def make_rows(title,excerpt,url,published,source,now,body='',body_ok=False):
 text=title+' '+(body or excerpt)
 if not re.search(PV,text,re.I):return []
 matched=[m for m,p in MARKETS.items() if re.search(p,title+' '+excerpt,re.I)]
 basis='正文明确提及市场'
 if source.get('sourceType')=='government':matched=[source['market']];basis='官方发布机构辖区，公告适用范围待核实'
 elif not matched and source.get('market'):
  if re.search(r'米国|中国|中國|미국|중국|유럽|欧州|欧洲|europe|united states|germany|ドイツ|ブラジル|독일',title,re.I):return []
  matched=[source['market']];basis='本地语言来源定位，地域适用性待复核'
 if not matched:return []
 event,event_quote,direction,policy_quote=signals(text,source)
 topic='政策与补贴' if event=='政策公告' or re.search(POLICY,title,re.I) else '竞争动态' if event!='市场/企业动态' or re.search(BRANDS,title,re.I) else '技术创新' if re.search(r'効率|효율|efficiency|钙钛矿|ペロブスカイト|HJT|TOPCon',title,re.I) else '市场趋势'
 # No legal/policy stance from a media report or title alone.
 if not body_ok:direction='未判定';policy_quote=''
 evidence=[]
 if policy_quote:evidence.append({'label':'政策方向原文线索','original':policy_quote})
 if event_quote:evidence.append({'label':'项目/合作/产品原文线索','original':event_quote})
 for market in matched:
  yield {'id':hashlib.sha256((market+url).encode()).hexdigest()[:24],'market':market,'title':title,'originalTitle':title,'date':published.astimezone(dt.timezone(dt.timedelta(hours=8))).date().isoformat(),'publishedAt':published.isoformat(),'topic':topic,'priority':'高' if source.get('sourceType')=='government' and topic=='政策与补贴' else '中','source':source['name'],'url':url,
   'summary':'中文整理待生成；请核对原文。','originalSummary':excerpt[:1200],
   'importance':'该条目由原文关键词归类，不代表政策已生效或商业重要性已确认。',
   'impact':'尚未生成经人工复核的晶科业务影响分析；请结合原文适用地区、项目阶段、产品认证及客户渠道评估。',
   'watch':('先核对政府原文的适用地区、对象、金额、申请期限和施行日期；不能将补助线索视为已生效支持政策。' if topic=='政策与补贴' else '核对合作对象、MOU与正式合同的区别、项目容量、供货方和实际投运日期；产品发布另查功率、认证、质保与本地准入。'),'tech':next((name for name,pattern in TECH.items() if re.search(pattern,text,re.I)),'未分类'),
   'dataKind':'live','analysisKind':'evidence-cues','language':source.get('language','en'),'sourceType':source.get('sourceType','media'),'jurisdiction':source.get('jurisdiction','地域适用性待复核'),'marketBasis':basis,
   'eventType':event,'policyDirection':direction,'policyStage':'法规效力/执行阶段待核实','evidence':evidence,'articleRead':body_ok,'translationStatus':'pending','collectedAt':now.isoformat()}

def parse_feed(xml,source,now,enrich=False):
 if b'<!DOCTYPE' in xml.upper() or b'<!ENTITY' in xml.upper():raise ValueError('XML declarations not supported')
 root=ET.fromstring(xml);ns={'a':'http://www.w3.org/2005/Atom','dc':'http://purl.org/dc/elements/1.1/'}
 entries=root.findall('./channel/item') or root.findall('{http://purl.org/rss/1.0/}item') or root.findall('a:entry',ns)
 if root.tag not in ('rss','{http://www.w3.org/1999/02/22-rdf-syntax-ns#}RDF','{http://www.w3.org/2005/Atom}feed'):raise ValueError('expected RSS/Atom feed, not an error page')
 candidates=[]
 for item in entries:
  title=clean(item.findtext('title') or item.findtext('a:title',namespaces=ns))
  excerpt=clean(item.findtext('description') or item.findtext('a:summary',namespaces=ns))
  if not re.search(PV,title+' '+excerpt,re.I):continue
  try:
   link=item.findtext('link')
   if not link:
    element=item.find('a:link',ns);link=element.get('href') if element is not None else ''
   url=canonical(link)
   published=valid_date(item.findtext('pubDate') or item.findtext('dc:date',namespaces=ns) or item.findtext('a:published',namespaces=ns) or item.findtext('a:updated',namespaces=ns) or '',source,now)
  except (ValueError,TypeError,OverflowError):continue
  candidates.append((title,excerpt,url,published))
 rows=[]
 for title,excerpt,url,published in candidates[:12]:
  body='';body_ok=False
  if enrich:
   try:_,body,_=article_document(fetch(url));body_ok=len(body)>80
   except Exception:pass
  rows.extend(make_rows(title,excerpt,url,published,source,now,body,body_ok))
 return rows

def parse_listing(data,source,now):
 soup=BeautifulSoup(data,'html.parser');links={}
 host=urllib.parse.urlsplit(source['url']).hostname
 for anchor in soup.find_all('a',href=True):
  url=urllib.parse.urljoin(source['url'],html.unescape(anchor['href']))
  if urllib.parse.urlsplit(url).hostname!=host or not re.search(source['linkPattern'],url):continue
  title=clean(anchor.get('title') or anchor.get_text(' ',strip=True))
  if not title:continue
  links.setdefault(canonical(url),title)
 if not links:raise ValueError('no recognized article links')
 rows=[];errors=0
 for url,title in list(links.items())[:14]:
  try:
   actual,body,dates=article_document(fetch(url));title=actual or title
   if not re.search(PV,title+' '+body,re.I):continue
   published=None
   for value in dates:
    try:published=valid_date(value,source,now);break
    except (ValueError,TypeError,OverflowError):continue
   if not published:continue
   excerpt=cue(body,PV) or body[:500]
   rows.extend(make_rows(title,excerpt,url,published,source,now,body,True))
  except Exception:errors+=1
 if links and errors==min(len(links),14):raise ValueError('all article fetches failed')
 return rows

def merge(previous,incoming):
 by_url={}
 for row in previous+incoming:
  key=(row['market'],canonical(row['url']));old=by_url.get(key)
  if old and old.get('translationStatus')=='translated' and old.get('originalTitle')==row.get('originalTitle') and old.get('originalSummary')==row.get('originalSummary'):
   for field in ('title','summary','translationStatus','translationProvider','translatedAt'):
    if field in old:row[field]=old[field]
   old_evidence={e['original']:e.get('chinese') for e in old.get('evidence',[])}
   for e in row.get('evidence',[]):
    if old_evidence.get(e['original']):e['chinese']=old_evidence[e['original']]
  by_url[key]=row
 result=[];seen=set()
 for row in sorted(by_url.values(),key=lambda n:(n['publishedAt'],n['id']),reverse=True):
  key=(row['market'],clean(row.get('originalTitle') or row['title']).casefold())
  if key not in seen:result.append(row);seen.add(key)
 return result[:3000]

def collect_source(source,now):
 try:
  data=fetch(source)
  rows=parse_feed(data,source,now,True) if source['kind']=='rss' else parse_listing(data,source,now)
  return rows,{'name':source['name'],'url':source['url'],'state':'ok','matched':len(rows),'language':source['language'],'sourceType':source['sourceType']}
 except Exception as e:
  print(source['name']+': '+type(e).__name__,file=sys.stderr)
  return [],{'name':source['name'],'url':source['url'],'state':'error','error':type(e).__name__,'language':source['language'],'sourceType':source['sourceType']}

def run(path):
 now=dt.datetime.now(dt.timezone.utc);previous=json.loads(path.read_text()) if path.exists() else {'items':[],'lastSuccessAt':None}
 incoming=[];status=[]
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
  for rows,health in pool.map(lambda s:collect_source(s,now),SOURCES):incoming.extend(rows);status.append(health)
 success=all(s['state']=='ok' for s in status)
 payload={'schemaVersion':1,'mode':'live','attemptedAt':now.isoformat(),'lastSuccessAt':now.isoformat() if success else previous.get('lastSuccessAt'),'status':'ok' if success else 'partial' if any(s['state']=='ok' for s in status) else 'error','sources':status,'items':merge(previous['items'],incoming),'coverageNotes':['日本经济产业省/资源能源厅目前返回403，未声称已覆盖其政策原文。','政府公告、媒体报道与企业自述分开标记；未覆盖所有地方补助或所有同行动态。','政策方向为保守的原文线索，不是已核实的法律或投资结论。']}
 for key in ('translation','translationModel'):
  if key in previous:payload[key]=previous[key]
 path.parent.mkdir(parents=True,exist_ok=True);temp=path.with_suffix('.tmp');temp.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n');os.replace(temp,path)
 print(f'Archive contains {len(payload["items"])} items; status: {payload["status"]}')
 return 0 if success else 1
if __name__=='__main__':sys.exit(run(Path(os.environ.get('FEED_OUTPUT',ROOT/'public/data/feed.json'))))
