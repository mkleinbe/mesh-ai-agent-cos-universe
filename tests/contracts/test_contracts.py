import json
from pathlib import Path
import pytest
from jsonschema import Draft202012Validator,ValidationError
ROOT=Path(__file__).resolve().parents[2]
@pytest.mark.parametrize('schema_path',sorted((ROOT/'contracts').glob('*.schema.json')))
def test_positive_and_negative_contract_fixture(schema_path):
    schema=json.loads(schema_path.read_text()); validator=Draft202012Validator(schema)
    example=json.loads((ROOT/'contracts'/'examples'/schema_path.name.replace('.schema.json','.json')).read_text())
    validator.validate(example)
    bad=dict(example); bad.pop(next(k for k in schema['required'] if k!='version'))
    with pytest.raises(ValidationError): validator.validate(bad)
