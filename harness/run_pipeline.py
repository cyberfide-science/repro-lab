#!/usr/bin/env python3
"""Stages 3 and 4: run the manifest's host-level stages (harness.stages[], here
one `docker run` per target), then extract results.json from the file the
manifest names. Writes work/<slug>/logs/<id>.log, work/<slug>/run_log.json and
work/<slug>/results.json. The code SHA is read from the run's own output
(`== git HEAD:` line), never from the manifest. Human checkpoints: any stage
expected to exceed checkpoints.max_stage_minutes, and any deviation from the
paper's method that lacks an approved_by entry in the manifest."""
import csv, json, os, re, subprocess, sys, time
from datetime import datetime, timezone
import yaml

if len(sys.argv) != 2:
    print("usage: py -3 harness/run_pipeline.py <slug>", file=sys.stderr)
    sys.exit(2)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SLUG = sys.argv[1]
M = yaml.safe_load(open(os.path.join(ROOT, "targets", SLUG, "repro-target.yaml"), encoding="utf-8"))
WORK = os.path.join(ROOT, "work", SLUG)
os.makedirs(WORK, exist_ok=True)
os.chdir(ROOT)

limit = M["checkpoints"]["max_stage_minutes"]
repo_root = os.path.abspath(ROOT).replace(os.sep, "/")
run_log_path = os.path.join(WORK, "run_log.json")


def approve(msg):
    if os.environ.get("HARNESS_APPROVE") == "1":
        print(f"[checkpoint] {msg} -- approved via HARNESS_APPROVE=1")
        return
    if input(f"[checkpoint] {msg} Proceed? [y/N] ").strip().lower() != "y":
        sys.exit("[run_pipeline] stopped at human checkpoint")


log = {"started_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "code_sha": None,
       "aborted": None, "stages": []}
os.makedirs(os.path.join(WORK, "logs"), exist_ok=True)
results_path = os.path.join(WORK, "results.json")
if os.path.exists(results_path):
    os.remove(results_path)  # an earlier run's metrics never survive into this run's work/<slug>/


def run():
    """Stages 3 and 4. Every stop is a sys.exit whose message becomes run_log.json's `aborted`."""
    for dev in M.get("deviations") or []:
        if not dev.get("approved_by"):
            sys.exit(f"[run_pipeline] deviation '{dev.get('what')}' has no approved_by; stopping")
    t_start = time.time()  # the results file must be written after this instant (a committed out/ copy is never scored)
    for st in M["harness"]["stages"]:
        if st["expected_minutes"] > limit:
            approve(f"stage '{st['id']}' expected {st['expected_minutes']} min (> {limit} min limit).")
        cmd = [c.replace("{repo_root}", repo_root) for c in st["cmd"]]
        print(f"[run_pipeline] stage {st['id']}: {' '.join(cmd)}")
        t0 = time.time()
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        # The run log keeps the argv as the manifest writes it ({repo_root} unsubstituted): no host path in any evidence file.
        entry = {"id": st["id"], "cmd": list(st["cmd"]), "returncode": r.returncode,
                 "seconds": round(time.time() - t0, 2), "log": f"work/{SLUG}/logs/{st['id']}.log"}
        open(entry["log"], "w", encoding="utf-8", newline="\n").write(r.stdout + r.stderr)
        log["stages"].append(entry)
        print(f"[run_pipeline]   exit {r.returncode} in {entry['seconds']} s; log at {entry['log']}")
        if r.returncode != 0:
            sys.exit(f"[run_pipeline] stage {st['id']} failed; see {entry['log']}")

    # The code SHA that actually ran, from the container's own first line.
    first = log["stages"][0]["log"]
    sha = re.search(r"^== git HEAD: ([0-9a-f]{7,40})\s*$",
                    open(first, encoding="utf-8", errors="replace").read(), re.M)
    if not sha:  # code_sha stays null
        sys.exit(f"[run_pipeline] no '== git HEAD:' line in {first}; cannot record code_sha, stopping")
    log["code_sha"] = sha.group(1)
    print(f"[run_pipeline] code_sha from the run's own output: {log['code_sha']}")

    # Stage 4: extract results.json from the pipeline's own output; never retype numbers.
    results_file = M["harness"]["results_file"]
    if not os.path.exists(results_file) or os.path.getmtime(results_file) <= t_start:
        sys.exit(f"[run_pipeline] {results_file} was not written by this run (missing or older than the stage start); "
                 "a results file left over from an earlier run is never scored, stopping")
    metrics = {}
    rows = csv.reader(open(results_file, newline="", encoding="utf-8"))
    next(rows)  # header row (key,value)
    for row in rows:
        v = row[1]
        if v.lstrip("-").isdigit():
            v = int(v)
        else:
            try:
                v = float(v)
            except ValueError:
                pass
        metrics[row[0]] = v
    log["finished_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    return results_file, metrics


# run_log.json is written exactly once, whatever happens above: on a stop it carries the reason and
# the stage logs already written, and results.json is absent, so work/<slug>/ describes this run only.
try:
    results_file, metrics = run()
except BaseException as e:
    log["aborted"] = str(e.code) if isinstance(e, SystemExit) else repr(e)
    raise
finally:
    json.dump(log, open(run_log_path, "w", encoding="utf-8", newline="\n"), indent=2)
json.dump({"source": results_file, "metrics": metrics},
          open(results_path, "w", encoding="utf-8", newline="\n"), indent=2)
print(f"[run_pipeline] extracted {len(metrics)} metrics -> work/{SLUG}/results.json")
