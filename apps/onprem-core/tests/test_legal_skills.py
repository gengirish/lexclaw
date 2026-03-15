from pathlib import Path

import pytest

from legal_skills import SkillExecutionRequest, SkillRegistry


def _load_registry() -> SkillRegistry:
    registry = SkillRegistry()
    package_dir = Path(__file__).resolve().parent.parent / "skill-packages"
    for manifest in registry.load_manifests(str(package_dir)):
        registry.install_skill(manifest)
    return registry


def test_loads_all_skill_packages():
    registry = _load_registry()
    assert len(registry.manifests) == 5
    assert "deposition-summarizer" in registry.manifests
    assert "pacer-search-adapter" in registry.manifests


def test_executes_production_skill_with_approval_and_entitlement():
    registry = _load_registry()
    result = registry.execute(
        SkillExecutionRequest(
            org_id="org-1",
            node_id="node-1",
            skill_id="deposition-summarizer",
            input_text="Testimony occurred on 2026-05-10. Counsel objected.",
            approved_by="reviewer@example.com",
        ),
        entitlement_codes={"deposition-summarizer"},
        policy_require_human_approval=True,
    )
    assert result.skill_id == "deposition-summarizer"
    assert result.output_json["case_overview"].startswith("deposition-")
    assert result.audit_metadata["action"] == "skill.execute"
    assert "input_digest" in result.audit_metadata


def test_blocks_execution_without_entitlement():
    registry = _load_registry()
    with pytest.raises(ValueError, match="missing entitlement"):
        registry.execute(
            SkillExecutionRequest(
                org_id="org-1",
                node_id="node-1",
                skill_id="contract-clause-risk-flagger",
                input_text="Liability and indemnify clauses are present.",
                approved_by="reviewer@example.com",
            ),
            entitlement_codes=set(),
            policy_require_human_approval=True,
        )


def test_blocks_execution_without_required_approval():
    registry = _load_registry()
    with pytest.raises(ValueError, match="human approval required"):
        registry.execute(
            SkillExecutionRequest(
                org_id="org-1",
                node_id="node-1",
                skill_id="deposition-summarizer",
                input_text="Witness statement text.",
                approved_by=None,
            ),
            entitlement_codes={"deposition-summarizer"},
            policy_require_human_approval=True,
        )


def test_audit_chain_hash_links_events():
    registry = _load_registry()
    req = SkillExecutionRequest(
        org_id="org-1",
        node_id="node-1",
        skill_id="deadline-extractor",
        input_text="Hearing date 2026-08-10 and filing due 2026-08-01.",
        approved_by="operator@example.com",
    )
    one = registry.execute(req, entitlement_codes={"deadline-extractor"}, policy_require_human_approval=False)
    two = registry.execute(req, entitlement_codes={"deadline-extractor"}, policy_require_human_approval=False)
    assert one.audit_metadata["event_hash"] != two.audit_metadata["event_hash"]
    assert two.audit_metadata["previous_hash"] == one.audit_metadata["event_hash"]
