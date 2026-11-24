"""Preserve authoring guidance checks across legacy and standardized READMEs."""

import importlib.util
from pathlib import Path
import sys

import pytest

CI = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CI))
spec = importlib.util.spec_from_file_location(
    "authoring_bcp_layout", CI / "validate_authoring_bcp_docs.py"
)
policy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(policy)

GUIDANCE = "- Do: Use the facade.\n- Why: Preserve operation semantics.\n- Avoid: Bypassing the boundary.\n"


def bounded(body):
    return f"{policy.BCP_BEGIN}\n{policy.BCP_BOLD_TITLE}\n{body}\n{policy.BCP_END}"


def test_standardized_facade_keeps_the_actual_bcp_block():
    section = policy._authoring_bcp_section(policy.FACADE_README.read_text("utf-8"))
    assert "Default CRUD and Operation Semantics" not in section
    assert policy._guidance_groups(section)
    assert not policy._validate_grouped_guidance(policy.FACADE_README, section)


@pytest.mark.parametrize("managed", [False, True])
def test_only_bcp_groups_are_validated(managed):
    text = (
        bounded("**Boundary**\n" + GUIDANCE)
        if managed
        else policy.README_BCP_HEADING + "\n### Boundary\n" + GUIDANCE
    )
    text += "\n## Governance\n### Ownership\nOrdinary README prose.\n"
    section = policy._authoring_bcp_section(text)
    assert "Ordinary README prose" not in section
    assert not policy._validate_grouped_guidance(policy.FACADE_README, section)


def test_missing_rationale_still_fails():
    section = policy._authoring_bcp_section(
        bounded("**Boundary**\n" + GUIDANCE.replace("- Why:", "Rationale:"))
    )
    assert any(
        "missing '- Why:'" in error
        for error in policy._validate_grouped_guidance(policy.FACADE_README, section)
    )


def test_fenced_examples_cannot_supply_policy_bullets():
    section = policy._authoring_bcp_section(
        bounded("**Boundary**\n```text\n" + GUIDANCE + "```\n")
    )
    assert len(policy._validate_grouped_guidance(policy.FACADE_README, section)) == 3


@pytest.mark.parametrize("text", [policy.BCP_BEGIN, policy.BCP_END + policy.BCP_BEGIN])
def test_malformed_bounds_fail(text):
    with pytest.raises(ValueError, match="BCP block"):
        policy._authoring_bcp_section(text)
