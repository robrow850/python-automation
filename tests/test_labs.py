import asyncio
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "api-automation")]
import labtools as lab
import clients

class Labs(unittest.TestCase):
    def test_inventory(self): self.assertIn("system", lab.inventory())
    def test_logs(self):
        result=lab.parse_logs((ROOT/"samples/events.jsonl").read_text())
        self.assertEqual(result["counts"], {"INFO":1,"WARN":1,"ERROR":1})
        self.assertEqual(result["malformedLines"], [4])
    def test_csv(self):
        self.assertEqual(lab.csv_to_json('name,value\n"a,b",2\n')[0]['name'], 'a,b')
        for bad in ['a,a\n1,2', 'a,b\n1,2,3', 'a,b\n1']:
            with self.assertRaises(ValueError): lab.csv_to_json(bad)
    def test_html(self):
        report=lab.html_report([{'<script>':'<img onerror=x>'}])
        self.assertNotIn('<img', report); self.assertIn('&lt;script&gt;',report)
    def test_sql(self):
        self.assertEqual(lab.sql_report([{'name':"'; DROP TABLE assets;--",'bytes':4}],3)[0]['bytes'],4)
    def test_drift(self):
        d=lab.drift({'a':None,'b':{'x':1}}, {'b':{'x':2},'c':3})
        self.assertEqual([r['kind'] for r in d],['missing','changed','extra'])
    def test_migration(self):
        with tempfile.TemporaryDirectory() as t:
            a=Path(t)/'a'; b=Path(t)/'b'; a.mkdir(); b.mkdir()
            (a/'file').write_text('first'); (b/'file').write_text('first')
            self.assertEqual(lab.verify_migration(a,b),[])
            (b/'file').write_text('other')
            self.assertEqual(lab.verify_migration(a,b)[0]['kind'],'changed')
            (a/'link').symlink_to(a/'file')
            with self.assertRaises(ValueError): lab.manifest(a)
    def test_graph_pages(self):
        replies=iter([{'value':[1],'@odata.nextLink':'https://graph.microsoft.com/v1.0/users?page=2'}, {'value':[2]}])
        self.assertEqual(clients.graph_users('test',lambda _:next(replies)),[1,2])
    def test_graph_host_and_loops(self):
        for next_url in ['https://example.com/v1.0/users','https://graph.microsoft.com/v1.0/users?$select=id,displayName,userPrincipalName']:
            with self.assertRaises(ValueError): clients.graph_users('test',lambda _:{'value':[], '@odata.nextLink':next_url})
    def test_rest_retry(self):
        class Response:
            headers={}
            def __init__(self,code): self.status_code=code
            def json(self): return {'ok':True}
            def close(self): pass
        class Session:
            def __init__(self): self.calls=0
            def get(self,*a,**k):
                self.calls+=1; return Response(429 if self.calls==1 else 200)
        session=Session()
        with patch('clients.time.sleep'):
            self.assertEqual(clients.get_json('https://example.com',session),{'ok':True})
        self.assertEqual(session.calls,2)
    def test_url_validation(self):
        for url in ['http://example.com','https://user:pass@example.com']:
            with self.assertRaises(ValueError): clients.validate_url(url)
    def test_async_input_validation(self):
        with self.assertRaises(ValueError): asyncio.run(clients.async_json([],0))
    def test_fixture(self): self.assertEqual(len(clients.fixture_pages(ROOT/'samples/pages.json')),2)
if __name__=='__main__': unittest.main()
