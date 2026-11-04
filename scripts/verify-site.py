"""Verify the deployed origin in GitHub's runner; publish a non-secret health record."""
import datetime as dt
import json
import os
from pathlib import Path
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
ROOT=Path(__file__).resolve().parents[1]
STATUS=ROOT/'.deploy/site-status.json'
def read(url):
    try:
        with urllib.request.urlopen(urllib.request.Request(url,headers={'Cache-Control':'no-cache'}),timeout=20) as response:
            return response.status,response.read(2_000_000).decode()
    except urllib.error.HTTPError as error:
        return error.code,''
def check(url,closed=False,prior_assets=()):
    code,body=read(url)
    data_code,data=read(url.rstrip('/')+'/data/feed.json')
    if closed:
        if not (code in (404,410) or (code==200 and 'NORTH_ASIA_ACCESS_CLOSED' in body)) or data_code not in (404,410): raise ValueError('Application or feed still accessible, or closure not confirmed')
        for asset in prior_assets:
            if read(asset)[0] not in (404,410): raise ValueError('Prior application asset still accessible')
        return 0
    if code!=200 or 'North Asia Solar Intelligence' not in body:raise ValueError('Homepage not ready')
    if data_code!=200:raise ValueError('Published feed not accessible')
    feed=json.loads(data)
    if feed.get('schemaVersion')!=1 or feed.get('mode')!='live' or not isinstance(feed.get('items'),list):raise ValueError('Invalid published feed')
    return len(feed['items'])
def run():
    closed='--closed' in sys.argv
    previous=json.loads(STATUS.read_text()) if STATUS.exists() else {}
    url=os.environ.get('SITE_URL') or previous.get('url')
    parsed=urllib.parse.urlsplit(url or '')
    if parsed.scheme!='https' or not parsed.hostname or not parsed.hostname.endswith('.github.io') or parsed.username or parsed.password:raise ValueError('Missing or unsupported deployment URL')
    url=url.rstrip('/')+'/'
    for attempt in range(8):
        try:
            prior_path=ROOT/'.deploy/prior-assets.json'
            prior=json.loads(prior_path.read_text()) if closed and prior_path.exists() else []
            count=check(url,closed,prior)
            record={'url':url,'state':'closed' if closed else 'open','verifiedAt':dt.datetime.now(dt.timezone.utc).isoformat(),'articleCount':count,'closureMode':'maintenance-page' if closed else None,'removedAssetsChecked':len(prior)}
            STATUS.parent.mkdir(parents=True,exist_ok=True)
            STATUS.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
            print(json.dumps(record,ensure_ascii=False))
            return
        except (ValueError,urllib.error.URLError,TimeoutError):
            if attempt==7:raise
            time.sleep(10)
if __name__=='__main__':run()
