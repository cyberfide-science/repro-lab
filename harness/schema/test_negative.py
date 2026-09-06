"""Two reports that must fail validation: a reproduced claim whose cause is not
'n/a', and a claim with a numeric tolerance type and no tolerance. Run from the
repo root after a run: py -3 harness/schema/test_negative.py reports/<slug>/report.json"""
import json, sys, jsonschema
V = jsonschema.Draft202012Validator
schema = json.load(open("harness/schema/report.schema.json", encoding="utf-8"))
v = V(schema, format_checker=V.FORMAT_CHECKER)
path = sys.argv[1]
for field, value in [("cause_category", "undiagnosed"), ("tolerance", None)]:
    r = json.load(open(path, encoding="utf-8"))
    r["claims"][0][field] = value        # claim 1 is reproduced, with a numeric tolerance
    errs = list(v.iter_errors(r))
    print(f"{field}={value!r}: {len(errs)} error(s):", "; ".join(e.message for e in errs))
