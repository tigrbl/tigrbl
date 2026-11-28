uv run --no-project --python 3.13 python tools/checkout_trace_lab_sources.py
pnpm install --frozen-lockfile
pnpm --filter @tigrbl/trace-lab-ui build
uv run --locked --package tigrbl-trace-lab-demo tigrbl-trace-lab-demo --port 0 --smoke
