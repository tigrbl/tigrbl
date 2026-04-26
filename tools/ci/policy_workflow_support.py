from __future__ import annotations

from common import repo_root

ROOT = repo_root()
WORKFLOW = ROOT / ".github" / "workflows" / "policy-governance.yml"
FIX_SCRIPT = ROOT / "tools" / "ci" / "fix_policy_governance.py"


def policy_workflow_runs_validator(script_name: str) -> bool:
    workflow_text = WORKFLOW.read_text(encoding="utf-8")
    fix_script_text = FIX_SCRIPT.read_text(encoding="utf-8")
    return (
        "fix_policy_governance.py --mode check" in workflow_text
        and script_name in fix_script_text
    )
