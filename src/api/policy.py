"""Policy REST API — per D-48 (internal modules)."""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from pydantic import BaseModel, Field
from typing import Any

from src.db.session import get_db
from src.db.models.policy import PolicyRule as DBPolicyRule
from src.core.policy.service import PolicyService
from src.core.policy.models import PolicyRequest, PolicyRule, PolicyOutcome
from src.core.policy.enums import CapabilityAction, CapabilityGroup, Domain

router = APIRouter(prefix="/policy", tags=["policy"])


class CreatePolicyRuleRequest(BaseModel):
    """Request to create a policy rule."""
    name: str
    description: str | None = None
    capability_group: str
    action: str
    actor: str | None = None
    domain: str | None = None
    note_type: str | None = None
    path_pattern: str | None = None
    sensitivity_min: int = 0
    outcome: str = "deny"
    priority: int = 0


class UpdatePolicyRuleRequest(BaseModel):
    """Request to update a policy rule."""
    name: str | None = None
    description: str | None = None
    outcome: str | None = None
    priority: int | None = None


class EvaluatePolicyRequest(BaseModel):
    """Request to evaluate a policy."""
    actor: str
    capability_group: str
    action: str
    domain: str | None = None
    note_type: str | None = None
    path: str | None = None


@router.get("/rules")
async def list_policy_rules(
    capability_group: str | None = Query(None),
    domain: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """List all policy rules with optional filters."""
    from src.core.policy.rules import PolicyRulesService
    from src.core.policy.defaults import get_default_rules

    rules_svc = PolicyRulesService()
    rules = rules_svc.list_rules()

    if capability_group:
        rules = [r for r in rules if r.capability_group.value == capability_group]
    if domain:
        rules = [r for r in rules if r.domain and r.domain.value == domain]

    return {
        "rules": [
            {
                "id": str(i),
                "name": r.name,
                "description": r.description,
                "capability_group": r.capability_group.value,
                "action": r.action.value if r.action else None,
                "domain": r.domain.value if r.domain else None,
                "outcome": r.outcome.value,
                "priority": r.priority,
            }
            for i, r in enumerate(rules)
        ],
        "total": len(rules),
    }


@router.post("/rules")
async def create_policy_rule(
    request: CreatePolicyRuleRequest,
    db: AsyncSession = Depends(get_db),
):
    """Create a new policy rule.

    Rules are persisted to _system/policy/rules.yaml.
    """
    from src.core.policy.rules import PolicyRulesService

    try:
        cap_group = CapabilityGroup(request.capability_group)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid capability_group: {request.capability_group}. "
                   f"Valid values: {[c.value for c in CapabilityGroup]}"
        )

    try:
        action = CapabilityAction(request.action)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid action: {request.action}. "
                   f"Valid values: {[a.value for a in CapabilityAction]}"
        )

    domain = None
    if request.domain:
        try:
            domain = Domain(request.domain)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid domain: {request.domain}. "
                       f"Valid values: {[d.value for d in Domain]}"
            )

    rule = PolicyRule(
        name=request.name,
        description=request.description,
        capability_group=cap_group,
        action=action,
        domain=domain,
        outcome=PolicyOutcome(request.outcome),
        priority=request.priority,
    )

    rules_svc = PolicyRulesService()
    rules_svc.add_rule(rule)

    return {
        "success": True,
        "message": f"Rule '{request.name}' created",
        "rule": {
            "name": rule.name,
            "capability_group": rule.capability_group.value,
            "action": rule.action.value,
            "outcome": rule.outcome.value,
        }
    }


@router.get("/rules/{rule_idx}")
async def get_policy_rule(
    rule_idx: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a policy rule by index."""
    from src.core.policy.rules import PolicyRulesService

    rules_svc = PolicyRulesService()
    rules = rules_svc.list_rules()

    if rule_idx < 0 or rule_idx >= len(rules):
        raise HTTPException(status_code=404, detail="Rule not found")

    r = rules[rule_idx]
    return {
        "id": rule_idx,
        "name": r.name,
        "description": r.description,
        "capability_group": r.capability_group.value,
        "action": r.action.value if r.action else None,
        "domain": r.domain.value if r.domain else None,
        "outcome": r.outcome.value,
        "priority": r.priority,
    }


@router.put("/rules/{rule_idx}")
async def update_policy_rule(
    rule_idx: int,
    request: UpdatePolicyRuleRequest,
    db: AsyncSession = Depends(get_db),
):
    """Update a policy rule by index."""
    from src.core.policy.rules import PolicyRulesService

    rules_svc = PolicyRulesService()
    rules = rules_svc.list_rules()

    if rule_idx < 0 or rule_idx >= len(rules):
        raise HTTPException(status_code=404, detail="Rule not found")

    rule = rules[rule_idx]

    if request.name is not None:
        rule.name = request.name
    if request.description is not None:
        rule.description = request.description
    if request.outcome is not None:
        rule.outcome = PolicyOutcome(request.outcome)
    if request.priority is not None:
        rule.priority = request.priority

    rules_svc.save_rules(rules)

    return {"success": True, "message": f"Rule {rule_idx} updated"}


@router.delete("/rules/{rule_idx}")
async def delete_policy_rule(
    rule_idx: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete a policy rule by index."""
    from src.core.policy.rules import PolicyRulesService

    rules_svc = PolicyRulesService()
    rules = rules_svc.list_rules()

    if rule_idx < 0 or rule_idx >= len(rules):
        raise HTTPException(status_code=404, detail="Rule not found")

    deleted_rule = rules.pop(rule_idx)
    rules_svc.save_rules(rules)

    return {"success": True, "message": f"Rule '{deleted_rule.name}' deleted"}


@router.post("/evaluate")
async def evaluate_policy(
    request: EvaluatePolicyRequest,
    db: AsyncSession = Depends(get_db),
):
    """Evaluate a policy request (for debugging).

    Useful for testing policy rules before applying them.
    """
    try:
        cap_group = CapabilityGroup(request.capability_group)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid capability_group: {request.capability_group}"
        )

    try:
        action = CapabilityAction(request.action)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid action: {request.action}"
        )

    domain = None
    if request.domain:
        try:
            domain = Domain(request.domain)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid domain: {request.domain}"
            )

    policy_svc = PolicyService()
    policy_request = PolicyRequest(
        actor=request.actor,
        capability_group=cap_group,
        action=action,
        domain=domain,
        note_type=request.note_type,
        path=request.path,
    )

    result = policy_svc.check(policy_request)

    return {
        "actor": request.actor,
        "capability_group": request.capability_group,
        "action": request.action,
        "domain": request.domain,
        "outcome": result.outcome.value,
        "reason": result.reason,
        "matched_rule": result.matched_rule,
    }
