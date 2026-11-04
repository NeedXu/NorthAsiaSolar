import datetime as dt
import importlib.util
import unittest
from pathlib import Path
spec = importlib.util.spec_from_file_location('collector', Path(__file__).resolve().parents[1] / 'scripts/collect.py')
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)
NOW = dt.datetime(2026, 11, 4, tzinfo=dt.timezone.utc)
SOURCE = {'name': 'Test publisher', 'url': 'https://example.com/feed'}
def feed(title='Japan solar rooftop policy', date='Tue, 03 Nov 2026 12:00:00 +0000', link='https://example.com/news?utm_source=rss'):
    return f'<rss><channel><item><title>{title}</title><description>Solar market &amp; rooftop news</description><pubDate>{date}</pubDate><link>{link}</link></item></channel></rss>'.encode()
class CollectorTests(unittest.TestCase):
    def test_real_metadata_and_no_fabricated_analysis(self):
        row = c.parse_feed(feed(), SOURCE, NOW)[0]
        self.assertEqual(row['market'], '日本')
        self.assertEqual(row['url'], 'https://example.com/news')
        self.assertEqual(row['dataKind'], 'live')
        self.assertIn('尚未生成', row['impact'])
        self.assertEqual(row['topic'], '政策与补贴')
    def test_ignore_unrelated_old_invalid_and_future(self):
        for data in [feed(title='European solar rooftop'), feed(date='invalid'), feed(date='Mon, 03 Nov 2025 00:00:00 +0000'), feed(date='Tue, 03 Nov 2027 00:00:00 +0000'), feed(link='javascript:alert(1)')]:
            self.assertEqual(c.parse_feed(data, SOURCE, NOW), [])
    def test_url_and_title_deduplication(self):
        rows = c.parse_feed(feed(), SOURCE, NOW)
        self.assertEqual(len(c.merge(rows, rows)), 1)
        other = dict(rows[0], url='https://other.example/article', id='other')
        self.assertEqual(len(c.merge(rows, [other])), 1)
    def test_reject_nonfeed_and_entities(self):
        for data in [b'<html>blocked</html>', b'<!DOCTYPE rss><rss><channel/></rss>']:
            with self.assertRaises(ValueError): c.parse_feed(data, SOURCE, NOW)
    def test_failure_preserves_archive_and_success_timestamp(self):
        import tempfile, json
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'feed.json'
            rows = c.parse_feed(feed(), SOURCE, NOW)
            path.write_text(json.dumps({'items': rows, 'lastSuccessAt': '2026-11-01T00:00:00+00:00'}))
            with patch.object(c, 'fetch', side_effect=TimeoutError): self.assertEqual(c.run(path), 1)
            saved = json.loads(path.read_text())
            self.assertEqual(saved['items'], rows)
            self.assertEqual(saved['lastSuccessAt'], '2026-11-01T00:00:00+00:00')
            self.assertEqual(saved['status'], 'error')
if __name__ == '__main__': unittest.main()
