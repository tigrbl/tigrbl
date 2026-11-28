pnpm install --frozen-lockfile
pnpm --filter @tigrbl/trace-lab-ui build
uv run --package tigrbl-transport-trace-lab tigrbl-trace-lab --frontend pkgs/130_frontend/trace-lab-ui/dist
