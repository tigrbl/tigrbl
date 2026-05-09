# Agent Operating Guide: `ssot-registry`

All agents working in this repository **must use the `ssot-registry` CLI** as the system of record for:

- feature tracking
- feature-testing tracking
- release management
- claims
- evidence
- related issue/risk/boundary records

## Why this is required

Per the PyPI package (`ssot-registry`), the tool is a portable single-source-of-truth registry whose canonical artifact is:

- `.ssot/registry.json`

Everything else (reports/exports) is derived from that canonical registry.

## Install and verify

```bash
python -m pip install ssot-registry
ssot-registry -h
```

For this repo, prefer the local workspace bootstrap over a global-only install:

```bash
python ./.codex/scripts/setup_workspace.py
uv sync --all-packages --all-groups --all-extras --python-preference only-system
```

## Core command surface

Use these top-level commands:

```bash
ssot-registry {init,validate,upgrade,adr,spec,feature,test,issue,claim,evidence,risk,boundary,release,graph,registry}
```

Useful global flags:

- `--output-format {json,csv,df,yaml,toml}`
- `--output-file <path>`

## Required operating workflow

### 1) Initialize or upgrade registry

For a new repo:

```bash
ssot-registry init . --repo-id <repo_id> --repo-name <repo_name> --version <initial_version>
```

For an existing repo already on older schema/package versions:

```bash
ssot-registry upgrade . --sync-docs --write-report
```

### 2) Feature tracking (source of scope)

Create and maintain features as the base planning unit.

```bash
ssot-registry feature create -h
ssot-registry feature list .
ssot-registry feature get . --id <feature_id>
ssot-registry feature update . --id <feature_id> [...fields...]
```

Plan lifecycle/horizon/tier intent:

```bash
ssot-registry feature plan -h
ssot-registry feature lifecycle -h
```

Link dependencies and traceability edges:

```bash
ssot-registry feature link -h
ssot-registry feature unlink -h
```

### 3) Feature-testing tracking (verification mapping)

Tests must be represented in the registry and linked to covered features and/or claims.

```bash
ssot-registry test create -h
ssot-registry test link -h
ssot-registry test list .
```

Minimum expectation for each implementation change:

1. Feature exists (or is updated).
2. Test record exists (or is updated).
3. Test is linked to the target feature and relevant claim(s).

### 4) Claims management (what is asserted)

Use claims to represent assertions about behavior, quality, compliance, or guarantees.

```bash
ssot-registry claim create -h
ssot-registry claim link -h
ssot-registry claim evaluate -h
ssot-registry claim set-status -h
ssot-registry claim set-tier -h
```

Recommended claim flow:

1. Create claim.
2. Link claim to feature(s).
3. Link supporting test(s).
4. Link evidence rows.
5. Evaluate and update status/tier as evidence matures.

### 5) Evidence management (proof artifacts)

Track objective proof records and verify integrity.

```bash
ssot-registry evidence create -h
ssot-registry evidence link -h
ssot-registry evidence verify -h
ssot-registry evidence list .
```

Evidence should reference durable artifacts (CI runs, signed attestations, reports, logs, snapshots) and be linked to both claims and tests whenever possible.

### 6) Release management (certification -> promotion -> publication)

Manage releases as explicit registry entities.

```bash
ssot-registry release create -h
ssot-registry release add-claim -h
ssot-registry release add-evidence -h
ssot-registry release certify -h
ssot-registry release promote -h
ssot-registry release publish -h
ssot-registry release revoke -h
```

Recommended sequence:

1. Create release record.
2. Add claims/evidence to release.
3. Certify release after guard checks pass.
4. Promote certified release (snapshot emitted).
5. Publish promoted release (published snapshot emitted).
6. Revoke if post-release invalidation is required.

### 7) Governance and blockers

Track blockers that can affect readiness:

```bash
ssot-registry issue -h
ssot-registry risk -h
ssot-registry boundary -h
```

Use boundaries to freeze scope and ensure release contents match approved feature sets.

### 8) Validate before and after changes

Always validate registry consistency after updates:

```bash
ssot-registry validate . --write-report
ssot-registry sync-statuses . --dry-run
```

## Practical checklist (every feature delivery)

- [ ] Feature created/updated in registry.
- [ ] Claim(s) created/updated and linked to feature.
- [ ] Test record(s) created/updated and linked to feature/claim.
- [ ] Evidence created/updated and linked to claim/test.
- [ ] `claim evaluate` run for impacted claims.
- [ ] `evidence verify` run for impacted evidence.
- [ ] Release record updated (if change is part of a release train).
- [ ] `ssot-registry validate . --write-report` passes.

## Reporting and exports

For audits, handoffs, and machine-consumable snapshots:

```bash
ssot-registry registry export . --output-format json
ssot-registry graph export . --output-format json
```

## Repo workflow entry points

Current repo workflows that agents should recognize and reuse:

- `.github/workflows/policy-governance.yml`
- `.github/workflows/operator-surface.yml`
- `.github/workflows/cli-smoke.yml`
- `.github/workflows/evidence-lanes.yml`
- `.github/workflows/gate-b-surface-closure.yml`
- `.github/workflows/gate-c-conformance-security.yml`
- `.github/workflows/gate-d-reproducibility.yml`
- `.github/workflows/gate-e-promotion.yml`
- `.github/workflows/post-promotion-handoff.yml`
- `.github/workflows/release-certification-automation.yml`
- `.github/workflows/next-target-datatypes.yml`
- `.github/workflows/publish.yml`

## Repo validation commands

The current governance/gate workflows call these repo-local validators:

```bash
uv run --no-sync python tools/ci/fix_policy_governance.py --mode check
uv run --no-sync python tools/ci/validate_ssot_authority_model.py
uv run --no-sync python tools/ci/validate_declared_surface.py
uv run --no-sync python tools/ci/validate_gate_b_surface_closure.py
uv run --no-sync python tools/ci/validate_gate_c_conformance_security.py
uv run --no-sync python tools/ci/validate_gate_d_reproducibility.py
uv run --no-sync python tools/ci/validate_gate_e_promotion.py
uv run --no-sync python tools/ci/validate_post_promotion_handoff.py
uv run --no-sync python tools/ci/validate_transport_dispatch_track.py
```

When reproducing `cli-smoke`, gate, or evidence-lane jobs locally, preserve the workspace `PYTHONPATH` shape used in CI so package discovery matches the workflows.

## Non-negotiable policy

Agents **must not** track implementation status only in ad-hoc notes/issues/PR text when registry updates are required. The canonical state must be captured with `ssot-registry` first, then referenced elsewhere.
