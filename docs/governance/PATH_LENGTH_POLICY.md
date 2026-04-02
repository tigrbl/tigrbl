# Path Length Policy

The repository enforces conservative path-length limits so the tree stays portable across developer workstations, CI runners, and packaging workflows.

## Limits

- maximum file name length: `64`
- maximum directory name length: `48`
- maximum repository-relative path length: `160`

## Scope

These limits apply to the governed repository tree, including archived notes kept inside `docs/`.

## Enforcement

The policy is enforced by:

- `tools/ci/validate_path_lengths.py`
- `.github/workflows/policy-governance.yml`
- repo-level pytest coverage in `tools/ci/tests/test_path_length_policy.py`

## Change rule

If a future change would exceed these limits, the change must shorten the path or rename the affected file/directory before merge.
