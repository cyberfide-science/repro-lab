# Executor brief

Run the plan one step at a time, using the harness scripts only. When a script
prints a [checkpoint] line, stop and show it to the human; do not set
HARNESS_APPROVE yourself. If a stage fails, report the log path and stop.
Never edit files under upstream/. Never edit repro-target.yaml; if the manifest
is wrong, stop and tell the human. Never retype a number: every value in
results.json comes from the pipeline's output file named in the manifest.
