"""
Rule Loader - Load compliance rules from YAML files

Handles parsing YAML rule definitions and converting them to ComplianceRule objects.
Supports validation and rule merging from multiple sources.
"""

import dataclasses
import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from app.cache_service import CACHE_ENABLED, REDIS_AVAILABLE, redis_client
from app.compliance.models import ComplianceAction, ComplianceFramework, ComplianceRule, Severity

logger = logging.getLogger(__name__)


class RuleLoader:
    """Load compliance rules from YAML files"""

    def __init__(self, rules_dir: Optional[str] = None):
        if rules_dir is None:
            current_dir = Path(__file__).parent
            rules_dir = str(current_dir / "definitions")

        self.rules_dir = Path(rules_dir)

    def load_all_rules(self) -> List[ComplianceRule]:
        rules: List[ComplianceRule] = []

        if not self.rules_dir.exists():
            logger.warning(f"Rules directory not found: {self.rules_dir}")
            return rules

        yaml_files = list(self.rules_dir.glob("*.yaml")) + list(self.rules_dir.glob("*.yml"))

        for yaml_file in sorted(yaml_files):
            try:
                file_rules = self.load_rules_from_file(str(yaml_file))
                rules.extend(file_rules)
            except Exception as e:
                logger.error(f"Error loading rules from {yaml_file.name}: {e}")

        return rules

    def load_rules_from_file(self, filepath: str) -> List[ComplianceRule]:
        with open(filepath, "r") as f:
            data = yaml.safe_load(f)

        if not data or "rules" not in data:
            return []

        rules = []
        for rule_data in data["rules"]:
            try:
                rule = self._parse_rule(rule_data, data.get("framework"))
                if rule:
                    rules.append(rule)
            except Exception as e:
                logger.error(f"Error parsing rule: {e}")
                continue

        return rules

    def _parse_rule(
        self, rule_data: Dict[str, Any], default_framework: Optional[str] = None
    ) -> Optional[ComplianceRule]:
        framework_str = rule_data.get("framework", default_framework)
        if not framework_str:
            raise ValueError("Framework not specified")

        try:
            framework = ComplianceFramework[framework_str.upper()]
        except KeyError:
            raise ValueError(f"Unknown framework: {framework_str}")

        rule_id = rule_data.get("id", f"rule_{hash(str(rule_data))}")
        name = rule_data.get("name", "Unnamed Rule")

        severity_str = rule_data.get("severity", "medium").lower()
        try:
            severity = Severity[severity_str.upper()]
        except KeyError:
            severity = Severity.MEDIUM

        action_str = rule_data.get("action", "flag").lower()
        try:
            action = ComplianceAction[action_str.upper()]
        except KeyError:
            action = ComplianceAction.FLAG

        description = rule_data.get("description", "")
        remediation = rule_data.get("remediation", f"Review and remediate {name}")

        entity_types = rule_data.get("entity_types", [])
        keywords = rule_data.get("keywords", [])
        patterns = rule_data.get("patterns", [])

        if not (entity_types or keywords or patterns):
            raise ValueError(f"Rule {rule_id} has no matching criteria")

        return ComplianceRule(
            id=rule_id,
            name=name,
            description=description,
            framework=framework.value,
            severity=severity,
            action=action,
            entity_types=entity_types,
            keywords=keywords,
            patterns=patterns,
            remediation=remediation,
        )

    def validate_rules(self, rules: List[ComplianceRule]) -> Dict[str, Any]:
        report: Dict[str, Any] = {
            "total": len(rules),
            "by_framework": {},
            "by_severity": {},
            "by_action": {},
            "issues": [],
        }

        for rule in rules:
            framework = rule.framework
            report["by_framework"][framework] = report["by_framework"].get(framework, 0) + 1

            severity = rule.severity.name.lower()
            report["by_severity"][severity] = report["by_severity"].get(severity, 0) + 1

            action = rule.action.name.lower()
            report["by_action"][action] = report["by_action"].get(action, 0) + 1

            for pattern in rule.patterns:
                try:
                    re.compile(pattern)
                except re.error as e:
                    report["issues"].append(f"Invalid regex in rule {rule.id}: {pattern} - {e}")

        return report


def load_compliance_rules(rules_dir: Optional[str] = None) -> List[ComplianceRule]:
    """
    Convenience function to load all compliance rules.
    Tries to load from Redis cache first if enabled.

    Args:
        rules_dir: Optional directory to load from

    Returns:
        List of loaded ComplianceRule objects
    """
    # 1. Try to load from cache
    if CACHE_ENABLED and REDIS_AVAILABLE and redis_client:
        try:
            cache_key = "phiblock:rules:all"
            cached_data = redis_client.get(cache_key)
            if cached_data:
                logger.info("Loading compliance rules from Redis cache")
                # mypy thinks cached_data could be bytes or Awaitable, but we know
                # it's str due to decode_responses=True
                rules_dicts = json.loads(str(cached_data))
                return [ComplianceRule(**r) for r in rules_dicts]
        except Exception as e:
            logger.error(f"Error loading rules from cache: {e}")

    # 2. Load from file system if cache miss
    logger.info("Loading compliance rules from file system")
    loader = RuleLoader(rules_dir)
    rules = loader.load_all_rules()

    # 3. Cache the results
    if CACHE_ENABLED and REDIS_AVAILABLE and redis_client and rules:
        try:
            cache_key = "phiblock:rules:all"
            # specific helper to handle Enums if needed, but asdict + str mixin might work
            # For robustness, we turn enums to values via a safe serializer

            class EnumEncoder(json.JSONEncoder):
                def default(self, obj):
                    if isinstance(obj, (ComplianceAction, ComplianceFramework, Severity)):
                        return obj.value
                    return super().default(obj)

            # Convert dataclasses to dicts first
            rules_data = [dataclasses.asdict(r) for r in rules]

            # Serialize with custom encoder
            serialized = json.dumps(rules_data, cls=EnumEncoder)

            redis_client.setex(cache_key, 3600, serialized)  # Cache for 1 hour
            logger.info("Cached compliance rules to Redis")
        except Exception as e:
            logger.error(f"Error caching rules: {e}")

    return rules
