import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('verify',Path(__file__).resolve().parents[1]/'scripts/verify-site.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
class SiteVerificationTests(unittest.TestCase):
 def test_open_requires_html_and_actual_feed(self):
  with patch.object(v,'read',side_effect=[(200,'North Asia Solar Intelligence'),(200,'{"schemaVersion":1,"mode":"live","items":[{}]}')]):self.assertEqual(v.check('https://example.github.io/project'),1)
  with patch.object(v,'read',side_effect=[(200,'North Asia Solar Intelligence'),(404,'')]):
   with self.assertRaises(ValueError):v.check('https://example.github.io/project')
 def test_close_requires_both_homepage_and_feed_gone(self):
  with patch.object(v,'read',side_effect=[(404,''),(404,'')]):self.assertEqual(v.check('https://example.github.io/project',True),0)
  for codes in [(404,200),(403,403),(500,500)]:
   with patch.object(v,'read',side_effect=[(codes[0],''),(codes[1],'')]):
    with self.assertRaises(ValueError):v.check('https://example.github.io/project',True)
