"""Unit tests for compliance rule caching logic."""

import json
import unittest
from unittest.mock import patch

from app.compliance.models import ComplianceAction, ComplianceFramework, ComplianceRule, Severity
from app.compliance.rules import load_compliance_rules


class TestRuleCaching(unittest.TestCase):
    """Test suite for cache-aware rule loading."""

    def setUp(self):
        """Set up sample rule data for tests."""
        # Sample rule for testing
        self.sample_rule = ComplianceRule(
            id="rule_1",
            framework=ComplianceFramework.GDPR,
            name="Test Rule",
            description="Test Description",
            severity=Severity.HIGH,
            action=ComplianceAction.FLAG,
            entity_types=["test_entity"],
            keywords=["test"],
            patterns=[r"test"],
            remediation="Fix it",
        )
        self.sample_rule_dict = {
            "id": "rule_1",
            "framework": "GDPR",
            "name": "Test Rule",
            "description": "Test Description",
            "severity": "high",
            "action": "flag",
            "entity_types": ["test_entity"],
            "keywords": ["test"],
            "patterns": ["test"],
            "remediation": "Fix it",
        }

    @patch("app.compliance.rules.redis_client")
    @patch("app.compliance.rules.CACHE_ENABLED", True)
    @patch("app.compliance.rules.REDIS_AVAILABLE", True)
    @patch("app.compliance.rules.RuleLoader")
    def test_load_from_cache_hit(self, mock_loader_cls, mock_redis):
        """Test that rules are loaded from cache when available."""
        # Setup mock Redis to return cached data
        cached_data = json.dumps([self.sample_rule_dict])
        mock_redis.get.return_value = cached_data

        # Call function
        rules = load_compliance_rules()

        # Verify result
        self.assertEqual(len(rules), 1)
        self.assertEqual(rules[0].id, "rule_1")
        self.assertEqual(rules[0].framework, ComplianceFramework.GDPR.value)

        # Verify Redis get was called
        mock_redis.get.assert_called_with("guardrails:rules:all")

        # Verify Loader was NOT called
        mock_loader_cls.assert_not_called()

    @patch("app.compliance.rules.redis_client")
    @patch("app.compliance.rules.CACHE_ENABLED", True)
    @patch("app.compliance.rules.REDIS_AVAILABLE", True)
    @patch("app.compliance.rules.RuleLoader")
    def test_load_from_cache_miss_then_cache(self, mock_loader_cls, mock_redis):
        """Test that rules are loaded from file on cache miss, then cached."""
        # Setup mock Redis to return None (cache miss)
        mock_redis.get.return_value = None

        # Setup mock loader to return rules
        mock_loader_instance = mock_loader_cls.return_value
        mock_loader_instance.load_all_rules.return_value = [self.sample_rule]

        # Call function
        rules = load_compliance_rules()

        # Verify result
        self.assertEqual(len(rules), 1)
        self.assertEqual(rules[0].id, "rule_1")

        # Verify Redis get was called
        mock_redis.get.assert_called_with("guardrails:rules:all")

        # Verify Loader WAS called
        mock_loader_cls.assert_called_once()
        mock_loader_instance.load_all_rules.assert_called_once()

        # Verify Redis setex was called to cache the result
        # Check that the call argument contains the rule ID (simple check)
        args, _ = mock_redis.setex.call_args
        self.assertEqual(args[0], "guardrails:rules:all")
        self.assertEqual(args[1], 3600)
        self.assertIn('"id": "rule_1"', args[2])

    @patch("app.compliance.rules.redis_client")
    @patch("app.compliance.rules.CACHE_ENABLED", False)
    def test_cache_disabled(self, mock_redis):
        """Test that cache is skipped when disabled."""
        with patch("app.compliance.rules.RuleLoader") as mock_loader_cls:
            mock_loader_instance = mock_loader_cls.return_value
            mock_loader_instance.load_all_rules.return_value = [self.sample_rule]

            load_compliance_rules()

            mock_redis.get.assert_not_called()
            mock_loader_cls.assert_called_once()

    @patch("app.compliance.rules.redis_client", None)
    @patch("app.compliance.rules.CACHE_ENABLED", True)
    @patch("app.compliance.rules.REDIS_AVAILABLE", True)
    def test_redis_client_none(self):
        """Test graceful handling when redis_client is None even if available flag is True."""
        with patch("app.compliance.rules.RuleLoader") as mock_loader_cls:
            mock_loader_instance = mock_loader_cls.return_value
            mock_loader_instance.load_all_rules.return_value = [self.sample_rule]

            load_compliance_rules()

            mock_loader_cls.assert_called_once()
