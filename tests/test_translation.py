import importlib.util
from pathlib import Path
import unittest
spec=importlib.util.spec_from_file_location('translation',Path(__file__).resolve().parents[1]/'scripts/translate.py')
t=importlib.util.module_from_spec(spec);spec.loader.exec_module(t)
class TranslationTests(unittest.TestCase):
 def test_numeric_changes_fail_instead_of_inventing_capacity(self):
  with self.assertRaises(ValueError):t.checked_translation('100 MW solar project','200 MW 光伏项目')
 def test_traditional_chinese_preserves_original_and_capacity(self):
  row={'title':'太陽能100MW案場合作','summary':'供應100MW太陽能組件','language':'zh-Hant','evidence':[{'label':'合作','original':'簽訂100MW太陽能供應協議'}]}
  result=t.apply(row,None)
  self.assertEqual(result['originalTitle'],'太陽能100MW案場合作');self.assertIn('太阳能100MW',result['title']);self.assertEqual(result['translationStatus'],'translated');self.assertIn('签订100MW',result['evidence'][0]['chinese'])
 def test_foreign_original_retained_after_chinese_translation(self):
  row={'title':'태양광 100MW','summary':'태양광 100MW 공급','language':'ko','evidence':[]}
  result=t.apply(row,lambda text,lang:'100MW 光伏供应')
  self.assertEqual(result['originalTitle'],'태양광 100MW');self.assertEqual(result['title'],'100MW 光伏供应');self.assertEqual(result['translationStatus'],'translated')
