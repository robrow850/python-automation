import asyncio
import json
from pathlib import Path
import shutil
import subprocess
import sys
import types
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'api-automation'))
import clients

class CliAndPairs(unittest.TestCase):
    def run_cli(self,*args):
        r=subprocess.run([sys.executable,str(ROOT/'lab_cli.py'),*args],capture_output=True,text=True)
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertEqual(json.loads(r.stderr)['event'],'completed')
        return r.stdout
    def test_all_cli_commands(self):
        for command,path in [('logs','events.jsonl'),('transform','assets.csv'),('html','assets.json'),('sql','assets.json')]:
            self.assertTrue(self.run_cli(command,str(ROOT/'samples'/path)))
        self.assertIn('system',json.loads(self.run_cli('inventory')))
        self.assertEqual(len(json.loads(self.run_cli('drift',str(ROOT/'samples/expected.json'),str(ROOT/'samples/actual.json')))),3)
        self.assertEqual(json.loads(self.run_cli('verify',str(ROOT/'samples'),str(ROOT/'samples'))),[])
        for command in ['rest','async','graph']:
            self.assertEqual(len(json.loads(self.run_cli(command,'--fixture',str(ROOT/'samples/pages.json')))),2)
    def test_cli_error_is_nonzero(self):
        r=subprocess.run([sys.executable,str(ROOT/'lab_cli.py'),'logs','/missing-fixture'],capture_output=True,text=True)
        self.assertNotEqual(r.returncode,0)
        self.assertEqual(json.loads(r.stderr)['event'],'failed')
    @unittest.skipUnless(shutil.which('pwsh'),'PowerShell unavailable')
    def test_paired_logs(self):
        path=str(ROOT/'samples/events.jsonl')
        ps=subprocess.check_output(['pwsh','-NoProfile','-File',str(ROOT/'powershell-to-python/log_parser/parser.ps1'),'-InputPath',path],text=True)
        py=subprocess.check_output([sys.executable,str(ROOT/'powershell-to-python/log_parser/parser.py'),path],text=True)
        self.assertEqual(json.loads(ps),json.loads(py))
    @unittest.skipUnless(shutil.which('pwsh'),'PowerShell unavailable')
    def test_paired_rest_fixtures(self):
        path=str(ROOT/'samples/pages.json')
        ps=subprocess.check_output(['pwsh','-NoProfile','-File',str(ROOT/'powershell-to-python/rest_api/api-client.ps1'),'-FixturePath',path],text=True)
        py=subprocess.check_output([sys.executable,str(ROOT/'powershell-to-python/rest_api/api_client.py'),'--fixture',path],text=True)
        self.assertEqual(json.loads(ps),json.loads(py))
    def test_async_client_mocked_transport(self):
        stats={'active':0,'maximum':0}
        class Response:
            status=200
            async def __aenter__(self):
                stats['active']+=1;stats['maximum']=max(stats['maximum'],stats['active']);return self
            async def __aexit__(self,*args):stats['active']-=1
            async def json(self):await asyncio.sleep(0);return {'ok':True}
        class Session:
            def __init__(self,**kwargs):pass
            async def __aenter__(self):return self
            async def __aexit__(self,*args):pass
            def get(self,*args,**kwargs):return Response()
        fake=types.SimpleNamespace(ClientSession=Session,ClientTimeout=lambda **k:None)
        with patch.dict(sys.modules,{'aiohttp':fake}):
            result=asyncio.run(clients.async_json(['https://example.com']*8,2))
        self.assertEqual(len(result),8);self.assertLessEqual(stats['maximum'],2)
if __name__=='__main__':unittest.main()
