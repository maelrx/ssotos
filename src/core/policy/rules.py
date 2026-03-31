"""Policy rules CRUD service with YAML persistence."""
from pathlib import Path

import yaml

from core.policy.defaults import get_default_rules
from core.policy.models import PolicyRule

# Default storage path under _system/ per Phase 1 structure
_DEFAULT_STORAGE_PATH = Path("_system/policy/rules.yaml")


class PolicyRulesService:
    """CRUD service for policy rules with YAML persistence.

    Stores rules in _system/policy/rules.yaml. Loads default rules
    if no rules file exists. All rules are sorted by priority descending.
    """

    def __init__(self, storage_path: Path | None = None) -> None:
        self._storage_path: Path = storage_path or _DEFAULT_STORAGE_PATH
        self._rules: list[PolicyRule] = []
        self._loaded: bool = False

    def _ensure_loaded(self) -> None:
        """Lazy load rules from storage or defaults."""
        if not self._loaded:
            self._rules = self.load_rules()
            self._loaded = True

    def _serialize_rule(self, rule: PolicyRule) -> dict:
        """Serialize a PolicyRule to a dict for YAML output."""
        result: dict = {
            "id": rule.id,
            "outcome": rule.outcome.value,
            "priority": rule.priority,
        }
        if rule.actor is not None:
            result["actor"] = rule.actor
        if rule.capability_group is not None:
            result["capability_group"] = rule.capability_group.value
        if rule.action is not None:
            result["action"] = rule.action.value
        if rule.domain is not None:
            result["domain"] = rule.domain.value
        if rule.path_pattern is not None:
            result["path_pattern"] = rule.path_pattern
        if rule.note_type is not None:
            result["note_type"] = rule.note_type.value
        if rule.sensitivity is not None:
            result["sensitivity"] = rule.sensitivity.value
        return result

    def _deserialize_rule(self, data: dict) -> PolicyRule:
        """Deserialize a dict from YAML to a PolicyRule."""
        # Import here to avoid circular imports at module level
        from core.policy.enums import CapabilityAction, CapabilityGroup, Domain
        from core.policy.models import NoteType, PolicyOutcome, SensitivityLevel

        return PolicyRule(
            id=data["id"],
            actor=data.get("actor"),
            capability_group=CapabilityGroup(data["capability_group"])
            if data.get("capability_group")
            else None,
            action=CapabilityAction(data["action"]) if data.get("action") else None,
            domain=Domain(data["domain"]) if data.get("domain") else None,
            path_pattern=data.get("path_pattern"),
            note_type=NoteType(data["note_type"]) if data.get("note_type") else None,
            sensitivity=SensitivityLevel(data["sensitivity"])
            if data.get("sensitivity")
            else None,
            outcome=PolicyOutcome(data["outcome"]),
            priority=data.get("priority", 0),
        )

    def list_rules(self) -> list[PolicyRule]:
        """Return all rules sorted by priority descending."""
        self._ensure_loaded()
        return sorted(self._rules, key=lambda r: r.priority, reverse=True)

    def get_rule(self, rule_id: str) -> PolicyRule | None:
        """Return a rule by id or None if not found."""
        self._ensure_loaded()
        for rule in self._rules:
            if rule.id == rule_id:
                return rule
        return None

    def create_rule(self, rule: PolicyRule) -> PolicyRule:
        """Add a rule, persist to storage, and return the rule."""
        self._ensure_loaded()
        if rule.id is None:
            import uuid
            rule.id = str(uuid.uuid4())
        self._rules.append(rule)
        self.save_rules(self._rules)
        return rule

    def update_rule(self, rule_id: str, updates: dict) -> PolicyRule | None:
        """Update rule fields, persist, and return updated rule or None."""
        self._ensure_loaded()
        for i, rule in enumerate(self._rules):
            if rule.id == rule_id:
                updated_rule = self._apply_updates(rule, updates)
                self._rules[i] = updated_rule
                self.save_rules(self._rules)
                return updated_rule
        return None

    def _apply_updates(self, rule: PolicyRule, updates: dict) -> PolicyRule:
        """Apply field updates to a rule, returning a new PolicyRule."""
        # Import enums for validation
        from core.policy.enums import CapabilityAction, CapabilityGroup, Domain
        from core.policy.models import NoteType, PolicyOutcome, SensitivityLevel

        return PolicyRule(
            id=rule.id,
            actor=updates.get("actor", rule.actor),
            capability_group=(
                CapabilityGroup(updates["capability_group"])
                if updates.get("capability_group")
                else rule.capability_group
            ),
            action=(
                CapabilityAction(updates["action"])
                if updates.get("action")
                else rule.action
            ),
            domain=(
                Domain(updates["domain"])
                if updates.get("domain")
                else rule.domain
            ),
            path_pattern=updates.get("path_pattern", rule.path_pattern),
            note_type=(
                NoteType(updates["note_type"])
                if updates.get("note_type")
                else rule.note_type
            ),
            sensitivity=(
                SensitivityLevel(updates["sensitivity"])
                if updates.get("sensitivity")
                else rule.sensitivity
            ),
            outcome=(
                PolicyOutcome(updates["outcome"])
                if updates.get("outcome")
                else rule.outcome
            ),
            priority=updates.get("priority", rule.priority),
        )

    def delete_rule(self, rule_id: str) -> bool:
        """Remove a rule by id, persist, and return True if deleted."""
        self._ensure_loaded()
        original_count = len(self._rules)
        self._rules = [r for r in self._rules if r.id != rule_id]
        if len(self._rules) < original_count:
            self.save_rules(self._rules)
            return True
        return False

    def load_rules(self) -> list[PolicyRule]:
        """Load rules from YAML storage, falling back to defaults."""
        if not self._storage_path.exists():
            return get_default_rules()
        try:
            with open(self._storage_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            if not data or not isinstance(data, dict):
                return get_default_rules()
            rules_data = data.get("rules", [])
            return [self._deserialize_rule(r) for r in rules_data]
        except (yaml.YAMLError, OSError):
            return get_default_rules()

    def save_rules(self, rules: list[PolicyRule]) -> None:
        """Write rules to YAML storage, creating parent directories as needed."""
        self._storage_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "rules": [self._serialize_rule(r) for r in rules],
        }
        with open(self._storage_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False)

    def reload_from_defaults(self) -> list[PolicyRule]:
        """Replace all rules with defaults, save, and return the defaults."""
        defaults = get_default_rules()
        self._rules = defaults
        self.save_rules(self._rules)
        self._loaded = True
        return defaults


__all__ = ["PolicyRulesService"]
