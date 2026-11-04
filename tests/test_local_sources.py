import datetime as dt
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('local_collect',Path(__file__).resolve().parents[1]/'scripts/collect.py')
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
NOW=dt.datetime(2026,11,4,tzinfo=dt.timezone.utc)
class LocalSourcesTests(unittest.TestCase):
 def test_korean_local_timezone_and_original_title_are_preserved(self):
  xml='<rss><channel><item><title>한국 태양광 신제품 출시</title><link>https://example.com/article</link><pubDate>2026-11-03 18:00:00</pubDate><description>태양광 제품</description></item></channel></rss>'.encode()
  source={'name':'한국 기업','market':'韩国','language':'ko','sourceType':'company','timezone':9}
  row=c.parse_feed(xml,source,NOW)[0]
  self.assertEqual(row['market'],'韩国');self.assertEqual(row['language'],'ko');self.assertEqual(row['originalTitle'],'한국 태양광 신제품 출시');self.assertEqual(row['publishedAt'],'2026-11-03T09:00:00+00:00')
 def test_media_never_becomes_official_policy_evidence(self):
  text='太陽光発電の補助金を支援します。'
  self.assertEqual(c.signals(text,{'sourceType':'media'})[2],'未判定')
  self.assertEqual(c.signals(text,{'sourceType':'government'})[2],'支持线索')
 def test_negative_and_mixed_support_not_misclassified_as_positive(self):
  for text in ['太陽光の補助金を廃止します。','太陽光を補助しない。','태양광 보조금 지원하지 않습니다.']:
   self.assertNotEqual(c.signals(text,{'sourceType':'government'})[2],'支持线索')
 def test_planned_completion_and_mou_are_not_completed_project_or_binding_order(self):
  self.assertEqual(c.signals('太陽光発電所は来年に運転開始予定です。',{'sourceType':'company'})[0],'项目计划（待核实）')
  self.assertEqual(c.signals('태양광 업무협약 MOU 체결',{'sourceType':'company'})[0],'合作意向/MOU')
 def test_policy_cues_require_reading_body(self):
  source={'name':'政府','market':'日本','sourceType':'government','language':'ja'}
  row=list(c.make_rows('太陽光の補助金','太陽光を補助する。','https://example.com/news',NOW,source,NOW))[0]
  self.assertEqual(row['policyDirection'],'未判定');self.assertEqual(row['policyStage'],'法规效力/执行阶段待核实')
 def test_optical_semiconductors_are_not_photovoltaics(self):
  self.assertFalse(c.re.search(c.PV,'光電半導體晶片營收創新高',c.re.I))
 def test_html_listing_reads_actual_article_date_and_link(self):
  source={'name':'정부','url':'https://example.com/news/list','linkPattern':'/news/view','market':'韩国','language':'ko','sourceType':'government','timezone':9}
  page=b'<a href="/news/view?id=1">announcement</a>'
  body='<html><meta property="article:published_time" content="2026-11-03T10:00:00+09:00"><main><h1>태양광 지원 정책</h1><p>태양광 보조금 지원 정책을 시행합니다.</p></main></html>'.encode()
  with patch.object(c,'fetch',return_value=body):rows=c.parse_listing(page,source,NOW)
  self.assertEqual(rows[0]['url'],'https://example.com/news/view?id=1');self.assertTrue(rows[0]['articleRead']);self.assertEqual(rows[0]['sourceType'],'government')
 def test_incidental_solar_mention_in_general_investment_release_is_not_core_news(self):
  self.assertFalse(c.relevant('7家企业扩大投资台湾','7家企业扩大投资台湾。某工厂计划在厂区设置太阳能。',{'sourceType':'government'}))
 def test_headline_completion_is_not_replaced_by_an_old_mou_in_body(self):
  text='太陽光発電所が竣工。太陽光について去年MOUを締結。'
  self.assertEqual(c.signals(text,{'sourceType':'company'},'太陽光発電所が竣工')[0],'项目竣工/投运')
 def test_official_tariff_drafts_are_policy_but_not_marked_in_force(self):
  source={'name':'能源署','sourceType':'government','market':'台湾','language':'zh-Hant'}
  row=list(c.make_rows('太陽光電躉購費率草案','太陽光電躉購費率草案公開徵求意見。','https://example.com/policy',NOW,source,NOW,'太陽光電躉購費率草案公開徵求意見。',True))[0]
  self.assertEqual(row['topic'],'政策与补贴');self.assertIn('未确认生效',row['policyStage'])
 def test_policy_abbreviations_do_not_match_record_or_benefits(self):
  self.assertFalse(c.re.search(c.POLICY,'Solar cell record efficiency benefits customers',c.re.I))
  self.assertTrue(c.re.search(c.POLICY,'FIT制度の改定',c.re.I))
 def test_statutory_inspection_change_is_not_classified_as_mou(self):
  title='학교 태양광 설비 법정검사 주기 4년→1년 단축'
  event,quote,_,_=c.signals(title+'。태양광 업무협약을 체결한다.',{'sourceType':'government'},title)
  self.assertEqual(event,'政策公告');self.assertEqual(quote,title)
 def test_pv_storage_competitive_tender_is_identified(self):
  title='公告太陽光電發電設備結合儲能系統競標容量及截止期限'
  self.assertEqual(c.signals(title,{'sourceType':'government'},title)[0],'政府招标/采购')
 def test_announcing_a_rating_is_not_a_product_launch(self):
  title='PV ModuleTechでAAA格付けを獲得'
  self.assertNotEqual(c.signals(title+'。太陽光企業の格付けを発表。',{'sourceType':'company'},title)[0],'产品/技术发布')
 def test_generic_corporate_og_title_does_not_replace_news_or_date(self):
  source={'name':'隆基日本','url':'https://example.com/jp/news/','linkPattern':'/jp/news/.+/','market':'日本','language':'ja','sourceType':'company','timezone':9}
  listing='<a href="/jp/news/a/"><h3>太陽電池の効率28.29％を達成</h3><span>2026.9.30</span></a><a href="/jp/news/b/"><h3>太陽光パネル出荷量29.93GW</h3><span>2026.10.31</span></a>'.encode()
  shell='<html><meta property="og:title" content="LONGi Solar"><main>Solar corporate shell 2026.10.31</main></html>'.encode()
  with patch.object(c,'fetch',return_value=shell):rows=c.parse_listing(listing,source,NOW)
  self.assertEqual(len(rows),2);self.assertEqual(rows[0]['originalTitle'],'太陽電池の効率28.29％を達成');self.assertEqual(rows[0]['date'],'2026-09-30');self.assertFalse(rows[0]['articleRead']);self.assertNotEqual(rows[0]['id'],rows[1]['id'])
