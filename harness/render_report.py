#!/usr/bin/env python3
"""Stage 6: render reports/<slug>/report.json to reports/<slug>/report.md.
Formatting only, with one exception the report template requires: the summary
line's two integers (claims reproduced, claims total) are counted from
report.json's claims[]. Every other value in the Markdown is copied from
report.json; nothing else is computed here."""
import json, os, sys

if len(sys.argv) != 2:
    print("usage: py -3 harness/render_report.py <slug>", file=sys.stderr)
    sys.exit(2)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SLUG = sys.argv[1]
os.chdir(ROOT)

r = json.load(open(f"reports/{SLUG}/report.json", encoding="utf-8"))
L = [f"# Reproducibility report: {r['paper']['title']}", "",
     f"- DOI: {r['paper']['doi']}", f"- Code: `{r['paper']['code_sha']}`",
     f"- Generated: {r['generated_at']}", "", f"## Summary verdict: **{r['verdict']}**", ""]
n_ok = sum(c["verdict"] == "reproduced" for c in r["claims"])
L += [f"{n_ok} of {len(r['claims'])} claims within tolerance.", "", "## Per-claim table", "",
      "| id | figure | metric | claimed | obtained | tolerance | verdict | cause | extraction | evidence |",
      "|---|---|---|---|---|---|---|---|---|---|"]
for c in r["claims"]:
    fig = c["figure"] + (f" ({c['panel']})" if c["panel"] else "")
    tol = c["tolerance_type"] + (f" {c['tolerance']}" if c["tolerance"] is not None else "")
    L.append(f"| {c['id']} | {fig} | {c['metric']} | {c['claimed']} | {c['obtained']} | {tol} | "
             f"{c['verdict']} | {c['cause_category']} | {c['extraction']} | `{c['evidence_path']}` |")
L += ["", "## Environment delta", ""]
L += ["None: every pinned component matched." if not r["environment_delta"] else
      "\n".join(f"- {d['component']}: pinned {d['pinned']}, actual {d['actual']}" for d in r["environment_delta"])]
L += ["", "## Data provenance", "", "| id | uri | bytes | sha256 verified | fetched |", "|---|---|---|---|---|"]
L += [f"| {p['id']} | {p['uri']} | {p['bytes']} | {p['verified']} | {p['fetched_at']} |" for p in r["data_provenance"]]
L += ["", "## Deviations log", ""]
L += ["None." if not r["deviations"] else
      "\n".join(f"- {d['what']} (why: {d['why']}; approved by {d['approved_by']}, {d['date']})" for d in r["deviations"])]
L += ["", "## Time and cost", "",
      f"- Wall time: {r['cost']['wall_minutes']} min", f"- Agent tokens: {r['cost']['agent_tokens']}",
      f"- Estimated cost: USD {r['cost']['usd_estimate']}", ""]
flagged = [c for c in r["claims"] if c["verdict"] != "reproduced"]
if flagged:
    L += ["## Human review required", ""] + [
        f"- {c['id']}: we could not obtain {c['claimed']} for {c['metric']} under the manifest's conditions; "
        f"the closest we reached was {c['obtained']}. Cause: {c['cause_category']}." for c in flagged] + [""]
open(f"reports/{SLUG}/report.md", "w", encoding="utf-8", newline="\n").write("\n".join(L))
print(f"[render_report] wrote reports/{SLUG}/report.md")
