#!/usr/bin/env python3
import json
from pathlib import Path
from jsonschema import Draft202012Validator
root=Path(__file__).resolve().parents[1]
for schema_path in sorted((root/'contracts').glob('*.schema.json')):
    schema=json.loads(schema_path.read_text()); Draft202012Validator.check_schema(schema)
    example=root/'contracts'/'examples'/schema_path.name.replace('.schema.json','.json')
    Draft202012Validator(schema).validate(json.loads(example.read_text()))
    print(f'OK {schema_path.name}')
