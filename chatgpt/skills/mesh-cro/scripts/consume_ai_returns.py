"""Consume only a host-verified AI Returns specialist result for this existing owner."""
from pathlib import Path
import hashlib
import json
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
OWNER = 'mesh-cro'

def load(path):
    with Path(path).open('rb') as stream: raw=stream.read(4*1024*1024+1)
    if len(raw)>4*1024*1024: raise ValueError('Input exceeds 4 MiB')
    def pairs(items):
        result={}
        for k,v in items:
            if k in result: raise ValueError('Duplicate JSON key')
            result[k]=v
        return result
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _: (_ for _ in ()).throw(ValueError('Nonfinite JSON')))

def main():
    if len(sys.argv)!=3:
        print(json.dumps({'status':'INPUT_REQUIRED','usage':'python scripts/consume_ai_returns.py RESULT.json HOST_EXPECTED.json'}));return 2
    try:
        root=Path(__file__).resolve().parents[1]
        lock=load(root/'references/ai-returns-compatibility.json')
        actual=hashlib.sha256((root/'scripts/ai_returns_handoff.py').read_bytes()).hexdigest()
        if actual!=lock['helper_sha256']: raise ValueError('Canonical AI Returns adapter drift')
        from ai_returns_handoff import consume
        result=consume(load(sys.argv[1]),load(sys.argv[2]),OWNER)
        print(json.dumps(result,sort_keys=True,allow_nan=False));return 0
    except (ValueError,TypeError,KeyError,OSError,RecursionError) as exc:
        print(json.dumps({'status':'INPUT_REJECTED','reason':str(exc)}));return 2
if __name__=='__main__':raise SystemExit(main())
