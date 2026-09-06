"""Equivalent of `make report TARGET=<slug>` for machines without make.
Same scripts, same order, stop on the first non-zero exit.
Usage: py -3 run_all.py <slug>"""
import os, subprocess, sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))
if len(sys.argv) != 2:
    sys.exit("usage: py -3 run_all.py <slug>")
slug = sys.argv[1]
for step in ["build_env", "fetch_verify", "run_pipeline", "diff_claims", "render_report"]:
    rc = subprocess.call([sys.executable, f"harness/{step}.py", slug])
    if rc != 0:
        sys.exit(f"[run_all] {step} exited {rc}; stopping")
print(f"[run_all] done: reports/{slug}/report.json, reports/{slug}/report.md")
