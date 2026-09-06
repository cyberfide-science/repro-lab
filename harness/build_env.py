#!/usr/bin/env python3
"""Stage 1: build the target's image and compare the environment inside it with
the record committed for it. Writes work/<slug>/env_actual.json. Every
difference between targets/<slug>/env-resolved.txt and `pip freeze` inside the
image is one environment_delta entry; a package missing from the image is a
hard stop. The base image is pinned by digest and is recorded as a fact.
It never silently upgrades anything."""
import json, os, subprocess, sys
import yaml

if len(sys.argv) != 2:
    print("usage: py -3 harness/build_env.py <slug>", file=sys.stderr)
    sys.exit(2)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SLUG = sys.argv[1]
M = yaml.safe_load(open(os.path.join(ROOT, "targets", SLUG, "repro-target.yaml"), encoding="utf-8"))
WORK = os.path.join(ROOT, "work", SLUG)
os.makedirs(WORK, exist_ok=True)
os.chdir(ROOT)

image = M["harness"]["image"]
target_dir = os.path.join("targets", SLUG)
resolved = f"targets/{SLUG}/env-resolved.txt"


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        print(r.stderr, file=sys.stderr)
        sys.exit(1)
    return r.stdout


def pins(lines):  # "name==ver" -> (name, ver); anything else is keyed by the whole line
    out = {}
    for line in lines:
        line = line.strip()
        if not line:
            continue
        name, sep, ver = line.partition("==")
        out[name if sep else line] = ver if sep else line
    return out


print(f"[build_env] docker build -t {image} {target_dir}")
run(["docker", "build", "-t", image, target_dir])
image_id = run(["docker", "image", "inspect", "-f", "{{.Id}}", image]).strip()
print(f"[build_env] image {image} id {image_id}")

base = next(l.split()[1] for l in open(os.path.join(target_dir, "Dockerfile"), encoding="utf-8")
            if l.startswith("FROM "))
py = run(["docker", "run", "--rm", "--entrypoint", "python", image, "--version"]).split()[-1]
print(f"[build_env] base {base}; container python {py}")

delta = []
floor = str(M["environment"]["python"])
if tuple(int(x) for x in py.split(".")[:2]) < tuple(int(x) for x in floor.split(".")[:2]):
    delta.append({"component": "python", "pinned": f">={floor}", "actual": py})
want = pins(open(resolved, encoding="utf-8"))
have = pins(run(["docker", "run", "--rm", "--entrypoint", "pip", image, "freeze"]).splitlines())
for name, v in want.items():
    if name not in have:
        delta.append({"component": name, "pinned": v, "actual": "missing"})
    elif have[name] != v:
        delta.append({"component": name, "pinned": v, "actual": have[name]})
for name, v in have.items():
    if name not in want:
        delta.append({"component": name, "pinned": "absent", "actual": v})

json.dump({"image": image, "image_id": image_id, "base_image": base, "python": py,
           "pip_freeze_compared_with": resolved, "delta": delta},
          open(os.path.join(WORK, "env_actual.json"), "w", encoding="utf-8", newline="\n"), indent=2)
print(f"[build_env] {len(delta)} difference(s) vs {resolved}")
for d in delta:
    print(f"[build_env]   {d['component']}: pinned {d['pinned']}, actual {d['actual']}")
sys.exit(1 if any(d["actual"] == "missing" for d in delta) else 0)
