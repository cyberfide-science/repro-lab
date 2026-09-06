# make report TARGET=<slug>  ->  reports/<slug>/report.json + report.md.
# Each target runs one harness script; nothing else lives here.
# On a machine without make, `py -3 run_all.py <slug>` runs the same sequence.
PY ?= python3          # Windows: make PY="py -3" TARGET=<slug> report
TARGET ?= muzellec-2023-pydeseq2

.PHONY: report env data run diff render clean

report: render

env:
	$(PY) harness/build_env.py $(TARGET)

data: env
	$(PY) harness/fetch_verify.py $(TARGET)

run: data
	$(PY) harness/run_pipeline.py $(TARGET)

diff: run
	$(PY) harness/diff_claims.py $(TARGET)

render: diff
	$(PY) harness/render_report.py $(TARGET)

clean:
	rm -rf work/$(TARGET)
