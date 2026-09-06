#!/usr/bin/env python3
"""Stage 5: compare every manifest claim with work/<slug>/results.json, assign
a per-claim verdict and an overall verdict, and write
reports/<slug>/report.json validated against harness/schema/report.schema.json.
No arithmetic on the values: the container's results file already holds every
number in the form the claim states it. An out-of-tolerance claim is a human
checkpoint: it is recorded as 'undiagnosed' and flagged, never explained away
here."""
import json, os, sys
from datetime import datetime, timezone
import yaml, jsonschema

if len(sys.argv) != 2:
    print("usage: py -3 harness/diff_claims.py <slug>", file=sys.stderr)
    sys.exit(2)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SLUG = sys.argv[1]
M = yaml.safe_load(open(os.path.join(ROOT, "targets", SLUG, "repro-target.yaml"), encoding="utf-8"))
WORK = os.path.join(ROOT, "work", SLUG)
os.makedirs(WORK, exist_ok=True)
os.chdir(ROOT)

res = json.load(open(os.path.join(WORK, "results.json"), encoding="utf-8"))["metrics"]
env = json.load(open(os.path.join(WORK, "env_actual.json"), encoding="utf-8"))
prov = json.load(open(os.path.join(WORK, "provenance.json"), encoding="utf-8"))
run = json.load(open(os.path.join(WORK, "run_log.json"), encoding="utf-8"))
keys = M["harness"]["claim_keys"]


def as_list(v):  # "B,A,C", "B;A;C" and ["B", "A", "C"] compare equal
    return [str(s).strip() for s in (v if isinstance(v, list) else str(v).replace(";", ",").split(","))]


def tol_type(c):
    t = {"rank-order": "rank_order"}.get(c["tolerance_type"], c["tolerance_type"])
    if t not in ("absolute", "relative", "rank_order", "same_conclusion"):
        sys.exit(f"[diff_claims] claim {c['id']}: unknown tolerance_type {c['tolerance_type']!r}")
    if t == "rank_order" and c["tolerance"] != 0:
        sys.exit(f"[diff_claims] claim {c['id']}: this harness only implements exact ordering (tolerance 0)")
    return t


def compare(c, got):
    t, tol, want = tol_type(c), c["tolerance"], c["value"]
    if t in ("absolute", "relative"):
        if not isinstance(got, (int, float)) or isinstance(got, bool):
            return False  # "NA", "nan", a string: not reproduced, not a crash
        if t == "absolute":
            return abs(got - want) <= tol
        return abs(got - want) <= tol * abs(want)
    if t == "rank_order":
        return as_list(got) == as_list(want)
    if t == "same_conclusion":
        return str(got) == str(want)
    raise ValueError(t)


claims = []
for c in M["claims"]:
    k = keys[c["id"]]
    got = res.get(k)
    ok = got is not None and compare(c, got)
    claims.append({"id": c["id"], "figure": c["figure"], "panel": c["panel"],
                   "metric": k, "claimed": c["value"], "obtained": got,
                   "tolerance": c["tolerance"], "tolerance_type": tol_type(c),
                   "extraction": c["extraction"],
                   "verdict": "reproduced" if ok else "not_reproduced",
                   "cause_category": "n/a" if ok else "undiagnosed",
                   "evidence_path": f"work/{SLUG}/results.json" if got is not None else run["stages"][-1]["log"]})
n_ok = sum(cl["verdict"] == "reproduced" for cl in claims)
overall = "reproduced" if n_ok == len(claims) else ("not_reproduced" if n_ok == 0 else "partially")

# The code that ran is the one the container reported; a pin that differs is a finding.
delta = list(env["delta"])
codes = [c for c in M["code"] if c["role"] in ("package", "pipeline")]
if not codes:
    sys.exit("[diff_claims] manifest code[] has no entry with role 'package' or 'pipeline'; "
             "cannot compare the run's code_sha against a pinned commit, stopping")
code = codes[0]
if run["code_sha"] != code["commit"]:
    delta.append({"component": f"code:{code['repo']}", "pinned": code["commit"], "actual": run["code_sha"]})

t0 = datetime.fromisoformat(run["started_at"])
t1 = datetime.fromisoformat(run["finished_at"])
report = {
    "paper": {"doi": M["paper"]["doi"], "title": M["paper"]["title"], "code_sha": run["code_sha"]},
    "verdict": overall,
    "claims": claims,
    "environment_delta": delta,
    "data_provenance": prov,
    "deviations": [{"what": d["what"], "why": d["why"], "approved_by": d["approved_by"],
                    "date": str(d["date"])} for d in (M.get("deviations") or [])],
    "cost": {"wall_minutes": round((t1 - t0).total_seconds() / 60, 3),
             "agent_tokens": 0, "usd_estimate": 0.0},  # filled in by the agent wrapper when one is used
    "generated_at": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
}
schema = json.load(open("harness/schema/report.schema.json", encoding="utf-8"))
jsonschema.Draft202012Validator(schema, format_checker=jsonschema.Draft202012Validator.FORMAT_CHECKER).validate(report)
os.makedirs(os.path.join("reports", SLUG), exist_ok=True)
json.dump(report, open(f"reports/{SLUG}/report.json", "w", encoding="utf-8", newline="\n"), indent=2)
print(f"[diff_claims] {n_ok}/{len(claims)} claims within tolerance -> verdict: {overall}")
for cl in claims:
    if cl["verdict"] != "reproduced":
        print(f"[checkpoint] {cl['id']} ({cl['metric']}): claimed {cl['claimed']}, obtained {cl['obtained']} "
              f"[{cl['tolerance_type']} {cl['tolerance']}] -- needs human review before any outreach")
print("[diff_claims] report.json validated against harness/schema/report.schema.json")
print(f"[diff_claims] wrote reports/{SLUG}/report.json")
