"""Behavioral regressions for canonical existing-Skill AI Returns intake."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[2]
ENTRIES=json.loads((ROOT/'docs/ai-returns-integration.json').read_text())['entries']
class OwnerIntegration(unittest.TestCase):
    def test_each_owner_accepts_bound_result_and_rejects_unsafe_variants(self):
        for entry in ENTRIES:
            with self.subTest(owner=entry['skill_id']):
                skill=ROOT/entry['path'];helper=skill/'scripts/ai_returns_handoff.py'
                self.assertEqual(hashlib.sha256(helper.read_bytes()).hexdigest(),entry['helper_sha256'])
                lock=json.loads((skill/'references/ai-returns-compatibility.json').read_text())
                self.assertEqual(lock['helper_sha256'],entry['helper_sha256'])
                spec=importlib.util.spec_from_file_location('intake_'+entry['skill_id'].replace('-','_'),helper)
                module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
                result={'owner_skill':'mesh-ai-benefits-realization','client_id':'synthetic-client','assessment_id':'synthetic-assessment','value_contract_id':'vc-synthetic','source_digest':'a'*64,'result':{'status':'CAPTURE_REVIEW_REQUIRED','issues':['CAPACITY_IS_NOT_SAVINGS']},'external_action':False,'new_agent':False}
                expected={k:result[k] for k in ('client_id','assessment_id','value_contract_id','source_digest')}
                expected.update(result_digest=module.canonical_hash(result),execution_receipt_ref='fixture://independent-host-receipt')
                output=module.consume(result,expected,entry['skill_id'])
                self.assertEqual(output['owner_skill'],entry['skill_id']);self.assertFalse(output['human_approval_created'])
                self.assertEqual(output['specialist_result']['result']['issues'],['CAPACITY_IS_NOT_SAVINGS'])
                output['specialist_result']['result']['issues'].append('mutated')
                self.assertEqual(result['result']['issues'],['CAPACITY_IS_NOT_SAVINGS'])
                for key,value in (('client_id','other'),('source_digest','b'*64),('external_action',True),('new_agent',True),('owner_skill','mesh-cfo')):
                    invalid=copy.deepcopy(result);invalid[key]=value
                    with self.assertRaises(ValueError):module.consume(invalid,expected,entry['skill_id'])
                with tempfile.TemporaryDirectory() as folder:
                    r=Path(folder)/'result.json';h=Path(folder)/'host.json';r.write_text(json.dumps(result));h.write_text(json.dumps(expected))
                    completed=subprocess.run([sys.executable,'-I','-B',str(skill/'scripts/consume_ai_returns.py'),str(r),str(h)],capture_output=True,text=True,timeout=15)
                    self.assertEqual(completed.returncode,0,completed.stdout+completed.stderr)
                    self.assertEqual(json.loads(completed.stdout)['owner_skill'],entry['skill_id'])
                    r.write_text('{"bad":1,"bad":2}')
                    completed=subprocess.run([sys.executable,'-I','-B',str(skill/'scripts/consume_ai_returns.py'),str(r),str(h)],capture_output=True,text=True,timeout=15)
                    self.assertEqual(completed.returncode,2)
if __name__=='__main__':unittest.main()
