import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import MagicMock, patch
spec=importlib.util.spec_from_file_location('closed',Path(__file__).resolve().parents[1]/'scripts/build-closed.py')
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
class ClosedArtifactTests(unittest.TestCase):
 def exercise(self,root):
  (root/'.deploy').mkdir()
  (root/'.deploy/site-status.json').write_text(json.dumps({'url':'https://owner.github.io/project/'}))
  response=MagicMock();response.__enter__.return_value.read.return_value=b'<script src="./assets/app.js"></script><link href="./assets/app.css" rel="stylesheet">'
  return patch.object(c,'ROOT',root),patch.object(c.urllib.request,'urlopen',return_value=response)
 def test_shutdown_artifact_contains_no_news_or_application_assets(self):
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);p1,p2=self.exercise(root)
   with p1,p2:c.build()
   self.assertEqual({p.name for p in (root/'dist').iterdir()},{'index.html','404.html'})
   text=(root/'dist/index.html').read_text();self.assertIn('NORTH_ASIA_ACCESS_CLOSED',text);self.assertNotIn('<script',text)
   self.assertEqual(json.loads((root/'.deploy/prior-assets.json').read_text()),['https://owner.github.io/project/assets/app.js','https://owner.github.io/project/assets/app.css'])
 def test_refuses_to_upload_an_artifact_contaminated_with_old_data(self):
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);p1,p2=self.exercise(root);(root/'dist').mkdir();(root/'dist/leaked.json').write_text('{}')
   with p1,p2:
    with self.assertRaises(ValueError):c.build()
