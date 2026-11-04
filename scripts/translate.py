"""Free, local machine translation. Never invent summaries or silently present original text as Chinese."""
import datetime as dt
import json
import os
from pathlib import Path
import re
import time
import urllib.request
import urllib.parse
import urllib.error
from opencc import OpenCC
ROOT=Path(__file__).resolve().parents[1]
MODEL='facebook/m2m100_418M'
CC=OpenCC('t2s')

def numeric_tokens(text):return set(re.findall(r'\d+(?:[.,]\d+)*',text.replace(',','')))
def checked_translation(original,translated):
 translated=CC.convert(translated.strip())
 if not re.search(r'[\u4e00-\u9fff]',translated):raise ValueError('no Chinese translation returned')
 if not numeric_tokens(original).issubset(numeric_tokens(translated)):raise ValueError('translation changed or omitted numbers')
 return translated

def apply(row,translate,provider_name=None):
 language=row.get('language','en')
 original=row.get('originalTitle',row['title']);excerpt=row.get('originalSummary') or row['summary'].replace('原始 RSS 摘录（未翻译）：','')
 row['originalTitle']=original;row['originalSummary']=excerpt
 if language.startswith('zh'):
  title=CC.convert(original);summary=CC.convert(excerpt[:600])
  evidences=[CC.convert(e['original']) for e in row.get('evidence',[])]
  provider='繁体转简体（保留原文）'
 else:
  title=checked_translation(original[:220],translate(original[:220],language))
  excerpt=excerpt[:{'ko':100,'ja':140,'en':220}.get(language,140)]
  summary=checked_translation(excerpt,translate(excerpt,language)) if excerpt else '原始来源未提供可整理的摘录，请阅读原文。'
  evidences=[]
  for evidence in row.get('evidence',[]):
   source=evidence['original'][:{'ko':100,'ja':140,'en':220}.get(language,140)]
   try:evidences.append(checked_translation(source,translate(source,language)))
   except ValueError:evidences.append('该段中文节译未通过校验，请核对下方原文。')
  provider=provider_name or 'M2M100-418M 本地开源机译'
 row['title']=title;row['summary']=summary
 for e,value in zip(row.get('evidence',[]),evidences):e['chinese']=value
 row.pop('translationError',None)
 row.update(translationStatus='translated',translationProvider=provider,translatedAt=dt.datetime.now(dt.timezone.utc).isoformat())
 return row

WEB_CACHE={}
WEB_LAST=0.0
WEB_DISABLED=False
def web_translate(text,language):
 global WEB_LAST,WEB_DISABLED
 key=(text,language)
 if key in WEB_CACHE:return WEB_CACHE[key]
 if WEB_DISABLED:raise ValueError('public translation temporarily unavailable')
 time.sleep(max(0,0.6-(time.monotonic()-WEB_LAST)))
 query=urllib.parse.urlencode({'client':'gtx','sl':language,'tl':'zh-CN','dt':'t','q':text})
 req=urllib.request.Request('https://translate.googleapis.com/translate_a/single?'+query,headers={'User-Agent':'NorthAsiaSolarIntelligence/0.3 public-news-translation','Accept':'application/json'})
 try:
  with urllib.request.urlopen(req,timeout=20) as response:payload=json.loads(response.read(100000))
 except urllib.error.HTTPError as e:
  if e.code in (403,429):WEB_DISABLED=True
  raise
 finally:WEB_LAST=time.monotonic()
 if not isinstance(payload,list) or not isinstance(payload[0],list):raise ValueError('invalid translation response')
 result=''.join(segment[0] for segment in payload[0] if isinstance(segment,list) and isinstance(segment[0],str))
 WEB_CACHE[key]=result
 return result

def run(path):
 feed=json.loads(path.read_text());now=dt.datetime.now(dt.timezone.utc).isoformat();failures=0;translated=0
 pending=[r for r in feed['items'] if r.get('translationStatus')!='translated' or r.get('translationProvider')=='M2M100-418M 本地开源机译']
 for row in pending:
  if row.get('language','').startswith('zh'):
   apply(row,None);translated+=1
 foreign=[r for r in pending if not r.get('language','').startswith('zh')]
 queues={m:sorted([r for r in foreign if r['market']==m],key=lambda r:(r.get('sourceType')!='government',-dt.date.fromisoformat(r['date']).toordinal())) for m in ['日本','韩国','台湾']}
 candidates=[]
 while any(queues.values()):
  for queue in queues.values():
   if queue:candidates.append(queue.pop(0))
 error=None;license_name=None;phase='web-translate';fallback=[]
 for row in candidates[:30]:
  try:apply(row,web_translate,'Google 网页机译（未经人工校核）');translated+=1
  except Exception as e:
   row['translationStatus']='pending';row['translationError']=type(e).__name__;fallback.append(row)
 if fallback:
  try:
   phase='load-runtime'
   import torch
   from huggingface_hub import HfApi
   from transformers import M2M100ForConditionalGeneration,M2M100Tokenizer
   phase='model-metadata';info=HfApi().model_info(MODEL)
   card=info.card_data.to_dict() if hasattr(info.card_data,'to_dict') else info.card_data or {}
   license_name=card.get('license')
   if license_name!='mit':raise ValueError('model license not confirmed as MIT')
   revision=feed.get('translationModel',{}).get('revision') or info.sha
   if not re.fullmatch(r'[a-f0-9]{40}',revision):raise ValueError('invalid model revision')
   phase='download-model';tokenizer=M2M100Tokenizer.from_pretrained(MODEL,revision=revision,trust_remote_code=False)
   model=M2M100ForConditionalGeneration.from_pretrained(MODEL,revision=revision,trust_remote_code=False).eval()
   torch.set_num_threads(min(4,os.cpu_count() or 2));feed['translationModel']={'name':MODEL,'revision':revision,'license':'mit'}
   def translate(text,language):
    tokenizer.src_lang={'ja':'ja','ko':'ko','en':'en'}.get(language,'en')
    encoded=tokenizer(text,return_tensors='pt',max_length=256,truncation=True)
    with torch.inference_mode():output=model.generate(**encoded,forced_bos_token_id=tokenizer.get_lang_id('zh'),max_new_tokens=192,num_beams=2)
    return tokenizer.batch_decode(output,skip_special_tokens=True)[0]
   phase='local-fallback';start=time.monotonic()
   for row in fallback:
    if time.monotonic()-start>480:break
    try:apply(row,translate);translated+=1
    except Exception as e:failures+=1;row['translationStatus']='pending';row['translationError']=type(e).__name__
  except Exception as e:error=type(e).__name__
 remaining=sum(r.get('translationStatus')!='translated' for r in feed['items'])
 feed['translation']={'status':'ok' if not remaining else 'partial' if translated else 'error','at':now,'translatedThisRun':translated,'remaining':remaining,'validationFailures':failures,'error':error,'phase':phase,'modelLicense':license_name,'note':'机译/节译未人工复核；公开网页翻译非正式商业API，可能限流；失败时本地开源模型补充，数字校验不通过仍保留原文。'}
 temporary=path.with_suffix('.tmp');temporary.write_text(json.dumps(feed,ensure_ascii=False,indent=2)+'\n');os.replace(temporary,path)
 print(json.dumps(feed['translation'],ensure_ascii=False));return 0 if not remaining else 1
if __name__=='__main__':raise SystemExit(run(Path(os.environ.get('FEED_OUTPUT',ROOT/'public/data/feed.json'))))
