"""Dedicated Verification Test Suite for M10 (Evidence Conflict Detector) and M11 (Explainable Threat Scoring).

Tests:
1. ConflictRuleTable catalog integrity (all 9 rules).
2. ConflictRuleEngine evaluation of all 9 conflict types (C01 to C09) with evidence reference IDs.
3. ConflictNarrator dual-sided citations and non-attribution framing.
4. SignalNormalizer signal normalization across all families.
5. WeightedScorer family ceilings clamping.
6. FirstContactGuard safety assertion preventing novelty-induced escalation.
7. ScoreExplainer ordered contributions and non-attribution disclaimers.
8. Non-certainty linguistic checks (no '100% malicious', 'confirmed attacker', etc.).
"""
import unittest
import sys
import os
import uuid

# Ensure backend package is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.conflicts.rule_table import ConflictRuleTable, ConflictRule
from app.conflicts.narrator import ConflictNarrator
from app.conflicts.rule_engine import ConflictRuleEngine, evaluate_evidence_conflicts
from app.scoring.normalizer import SignalNormalizer, NormalizedSignal, normalize_all_signals
from app.scoring.first_contact_guard import apply_first_contact_guardrail
from app.scoring.explainer import ScoreExplainer, FIXED_DISCLAIMER
from app.scoring.weighted_scorer import WeightedScorer, compute_explainable_score


class TestM10EvidenceConflicts(unittest.TestCase):
    """Test suite for M10 Evidence Conflict Detector."""

    def setUp(self):
        self.ref_auth = uuid.uuid4()
        self.ref_from = uuid.uuid4()
        self.ref_reply_to = uuid.uuid4()
        self.ref_received = uuid.uuid4()
        self.ref_body = uuid.uuid4()
        self.evidence_refs = {
            "auth": self.ref_auth,
            "from": self.ref_from,
            "reply_to": self.ref_reply_to,
            "received": self.ref_received,
            "body": self.ref_body,
        }

    def test_conflict_rule_table_catalog(self):
        """Verify ConflictRuleTable contains all 9 canonical rules with valid metadata."""
        all_rules = ConflictRuleTable.all_rules()
        self.assertEqual(len(all_rules), 9)

        expected_ids = {"C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09"}
        found_ids = {r.rule_id for r in all_rules}
        self.assertEqual(expected_ids, found_ids)

        for rule in all_rules:
            self.assertIn(rule.severity, ["Low", "Medium", "High", "Critical"])
            self.assertIsInstance(rule.base_score_adjustment, int)
            self.assertTrue(len(rule.title) > 0)
            self.assertTrue(len(rule.description) > 0)

        # Test lookup helpers
        r_c03 = ConflictRuleTable.get_by_id("C03")
        self.assertIsNotNone(r_c03)
        self.assertEqual(r_c03.conflict_type, "auth_pass_vs_content_risk")

        r_by_type = ConflictRuleTable.get_by_type("display_text_vs_destination_host")
        self.assertIsNotNone(r_by_type)
        self.assertEqual(r_by_type.rule_id, "C05")

    def test_conflict_rule_c01_authenticated_but_misaligned(self):
        """C01: Verify detection of SPF/DKIM pass on unaligned 3rd party domain."""
        conflicts = ConflictRuleEngine.evaluate(
            auth_results={"spf": "pass", "dkim": "pass", "dmarc": "none", "spf_aligned": False, "dkim_aligned": False},
            anomalies=[],
            detections={"classification": {"predicted_class": "benign", "probabilities": {"benign": 0.9}}},
            url_artifacts=[],
            qr_results=[],
            evidence_refs=self.evidence_refs,
        )
        c01 = next((c for c in conflicts if c["rule_id"] == "C01"), None)
        self.assertIsNotNone(c01)
        self.assertEqual(c01["conflict_type"], "authenticated_but_misaligned")
        self.assertEqual(c01["severity"], "High")
        self.assertEqual(c01["score_adjustment"], 15)
        self.assertEqual(c01["evidence_ref_a_id"], self.ref_auth)
        self.assertEqual(c01["evidence_ref_b_id"], self.ref_from)
        self.assertIn("SPF=pass", c01["evidence_side_a"])
        self.assertIn("alignment check failed", c01["evidence_side_b"].lower())

    def test_conflict_rule_c02_reply_path_divergence(self):
        """C02: Verify detection of Reply-To divergence from Header From."""
        anomalies = [{
            "type": "reply_to_divergence",
            "severity": "High",
            "header_name": "Reply-To",
            "description": "Reply-To domain 'attacker-gmail.com' does not match From domain 'university.edu'.",
        }]
        conflicts = ConflictRuleEngine.evaluate(
            auth_results={"spf": "none", "dkim": "none", "dmarc": "none"},
            anomalies=anomalies,
            detections={"classification": {"predicted_class": "benign", "probabilities": {"benign": 0.8}}},
            url_artifacts=[],
            qr_results=[],
            evidence_refs=self.evidence_refs,
        )
        c02 = next((c for c in conflicts if c["rule_id"] == "C02"), None)
        self.assertIsNotNone(c02)
        self.assertEqual(c02["conflict_type"], "reply_path_divergence")
        self.assertEqual(c02["severity"], "High")
        self.assertEqual(c02["score_adjustment"], 20)
        self.assertEqual(c02["evidence_ref_a_id"], self.ref_from)
        self.assertEqual(c02["evidence_ref_b_id"], self.ref_reply_to)

    def test_conflict_rule_c03_auth_pass_vs_content_risk(self):
        """C03: Verify detection of DMARC Pass with hostile intent cues (Compromised Account)."""
        conflicts = ConflictRuleEngine.evaluate(
            auth_results={"spf": "pass", "dkim": "pass", "dmarc": "pass", "spf_aligned": True, "dkim_aligned": True},
            anomalies=[],
            detections={
                "classification": {"predicted_class": "bec_fraud", "probabilities": {"bec_fraud": 0.90, "benign": 0.05}},
                "bec_patterns": [{"title": "BEC: Bank Detail Diversion"}],
            },
            url_artifacts=[],
            qr_results=[],
            evidence_refs=self.evidence_refs,
        )
        c03 = next((c for c in conflicts if c["rule_id"] == "C03"), None)
        self.assertIsNotNone(c03)
        self.assertEqual(c03["conflict_type"], "auth_pass_vs_content_risk")
        self.assertEqual(c03["severity"], "Critical")
        self.assertEqual(c03["score_adjustment"], 25)
        self.assertEqual(c03["evidence_ref_a_id"], self.ref_auth)
        self.assertEqual(c03["evidence_ref_b_id"], self.ref_body)
        self.assertIn("Protocol Authentication", c03["evidence_side_a"])
        self.assertIn("Content Threat Engine", c03["evidence_side_b"])

    def test_conflict_rule_c04_auth_fail_vs_benign_content(self):
        """C04: Verify mitigation of false-alarm authentication failures on forwarded benign traffic."""
        conflicts = ConflictRuleEngine.evaluate(
            auth_results={"spf": "fail", "dkim": "pass", "dmarc": "none", "forwarding_detected": True},
            anomalies=[],
            detections={"classification": {"predicted_class": "benign", "probabilities": {"benign": 0.95}}},
            url_artifacts=[],
            qr_results=[],
            evidence_refs=self.evidence_refs,
        )
        c04 = next((c for c in conflicts if c["rule_id"] == "C04"), None)
        self.assertIsNotNone(c04)
        self.assertEqual(c04["conflict_type"], "auth_fail_vs_benign_content")
        self.assertEqual(c04["severity"], "Low")
        self.assertEqual(c04["score_adjustment"], -10)
        self.assertIn("forwarding headers present", c04["evidence_side_b"].lower())

    def test_conflict_rule_c05_display_text_vs_destination_host(self):
        """C05: Verify detection of anchor text mimicry pointing to divergent destination."""
        url_artifact = {
            "raw_url": "https://evil-phish-portal.xyz/login",
            "normalized_url": "https://evil-phish-portal.xyz/login",
            "anchor_text": "https://login.microsoftonline.com/auth",
            "destination_host": "evil-phish-portal.xyz",
            "mismatch_flag": True,
        }
        conflicts = ConflictRuleEngine.evaluate(
            auth_results={"spf": "none", "dkim": "none", "dmarc": "none"},
            anomalies=[],
            detections={"classification": {"predicted_class": "phishing", "probabilities": {"phishing": 0.85}}},
            url_artifacts=[url_artifact],
            qr_results=[],
            evidence_refs=self.evidence_refs,
        )
        c05 = next((c for c in conflicts if c["rule_id"] == "C05"), None)
        self.assertIsNotNone(c05)
        self.assertEqual(c05["conflict_type"], "display_text_vs_destination_host")
        self.assertEqual(c05["severity"], "Critical")
        self.assertEqual(c05["score_adjustment"], 25)
        self.assertIn("https://login.microsoftonline.com/auth", c05["evidence_side_a"])
        self.assertIn("evil-phish-portal.xyz", c05["evidence_side_b"])

    def test_conflict_rule_c06_qr_destination_vs_body_divergence(self):
        """C06: Verify detection of QR code with external destination when body text has no links."""
        conflicts = ConflictRuleEngine.evaluate(
            auth_results={"spf": "none", "dkim": "none", "dmarc": "none"},
            anomalies=[],
            detections={"classification": {"predicted_class": "phishing", "probabilities": {"phishing": 0.75}}},
            url_artifacts=[],  # No text body links
            qr_results=[{"payload": "https://unlinked-credential-harvester.xyz/auth"}],
            evidence_refs=self.evidence_refs,
        )
        c06 = next((c for c in conflicts if c["rule_id"] == "C06"), None)
        self.assertIsNotNone(c06)
        self.assertEqual(c06["conflict_type"], "qr_destination_vs_body_divergence")
        self.assertEqual(c06["severity"], "High")
        self.assertEqual(c06["score_adjustment"], 20)
        self.assertIn("unlinked-credential-harvester.xyz", c06["evidence_side_b"])

    def test_conflict_rule_c07_geography_vs_claimed_entity(self):
        """C07: Verify detection when leadership sender originates from offshore cloud/datacenter IP."""
        origin_info = {
            "ip": "198.51.100.22",
            "country": "Seychelles",
            "country_code": "SC",
            "infra_type": "datacenter",
            "isp": "Offshore Cloud VPS",
        }
        conflicts = ConflictRuleEngine.evaluate(
            auth_results={"spf": "none", "dkim": "none", "dmarc": "none"},
            anomalies=[],
            detections={
                "classification": {"predicted_class": "impersonation", "probabilities": {"impersonation": 0.85}},
                "impersonation": [{"title": "Executive Impersonation: Director"}],
            },
            url_artifacts=[],
            qr_results=[],
            origin_info=origin_info,
            evidence_refs=self.evidence_refs,
        )
        c07 = next((c for c in conflicts if c["rule_id"] == "C07"), None)
        self.assertIsNotNone(c07)
        self.assertEqual(c07["conflict_type"], "geography_vs_claimed_entity")
        self.assertEqual(c07["severity"], "Medium")
        self.assertEqual(c07["score_adjustment"], 15)
        self.assertIn("Datacenter", c07["evidence_side_b"])

    def test_conflict_rule_c08_header_timestamp_vs_relay_timing(self):
        """C08: Verify detection of impossible negative latency across Received hops."""
        anomalies = [{
            "type": "negative_hop_delay",
            "severity": "Medium",
            "title": "Impossible Relay Hop Timestamp",
            "description": "Negative transit interval detected between hop 2 and 3.",
        }]
        conflicts = ConflictRuleEngine.evaluate(
            auth_results={"spf": "none", "dkim": "none", "dmarc": "none"},
            anomalies=anomalies,
            detections={"classification": {"predicted_class": "benign", "probabilities": {"benign": 0.8}}},
            url_artifacts=[],
            qr_results=[],
            evidence_refs=self.evidence_refs,
        )
        c08 = next((c for c in conflicts if c["rule_id"] == "C08"), None)
        self.assertIsNotNone(c08)
        self.assertEqual(c08["conflict_type"], "header_timestamp_vs_relay_timing")
        self.assertEqual(c08["severity"], "Medium")
        self.assertEqual(c08["score_adjustment"], 10)

    def test_conflict_rule_c09_feed_reputation_vs_baseline(self):
        """C09: Verify attenuation of external threat feed alert on familiar institutional sender."""
        indicator_history = {
            "value": "trusted-partner.edu",
            "familiarity_band": "Common",
            "sighting_count": 42,
            "distinct_cases": 0,
        }
        external_flags = [{
            "feed_name": "Commercial Threat Feed",
            "indicator": "trusted-partner.edu",
            "category": "suspicious",
        }]
        conflicts = ConflictRuleEngine.evaluate(
            auth_results={"spf": "pass", "dkim": "pass", "dmarc": "pass", "spf_aligned": True, "dkim_aligned": True},
            anomalies=[],
            detections={"classification": {"predicted_class": "benign", "probabilities": {"benign": 0.95}}},
            url_artifacts=[],
            qr_results=[],
            indicator_history=indicator_history,
            external_threat_flags=external_flags,
            evidence_refs=self.evidence_refs,
        )
        c09 = next((c for c in conflicts if c["rule_id"] == "C09"), None)
        self.assertIsNotNone(c09)
        self.assertEqual(c09["conflict_type"], "feed_reputation_vs_baseline")
        self.assertEqual(c09["severity"], "Low")
        self.assertEqual(c09["score_adjustment"], -5)


class TestM11ExplainableScoring(unittest.TestCase):
    """Test suite for M11 Explainable Threat Scoring Engine."""

    def test_signal_normalizer_across_families(self):
        """Verify SignalNormalizer standardizes signals with evidence references."""
        ref_id = str(uuid.uuid4())
        signals = SignalNormalizer.normalize_all_signals(
            auth_results={"spf": "fail", "dkim": "fail", "dmarc": "fail", "spf_aligned": False, "dkim_aligned": False},
            anomalies=[{"title": "Missing Message-ID", "severity": "Low", "description": "No RFC Message-ID"}],
            detections={
                "classification": {"predicted_class": "phishing", "probabilities": {"phishing": 0.88}},
                "lookalike_domains": [{"title": "Lookalike Domain: micros0ft", "severity": "Critical", "description": "Typosquat", "domain": "micros0ft.com"}],
                "concealment": [{"title": "Adversarial Zero-Width Concealment", "description": "Zero width spaces"}],
            },
            url_artifacts=[{
                "raw_url": "https://evil.xyz",
                "normalized_url": "https://evil.xyz",
                "anchor_text": "https://microsoft.com",
                "destination_host": "evil.xyz",
                "mismatch_flag": True,
                "evidence_reference_id": ref_id,
            }],
            qr_results=[{"payload": "https://evil-qr.xyz/auth"}],
            attachment_artifacts=[],
            conflicts=[],
            origin_info={"ip": "1.2.3.4", "infra_type": "datacenter"},
            first_contact_info={"is_first_contact": True, "value": "micros0ft.com", "suppressed": False},
            evidence_refs={"primary": ref_id, "auth": ref_id, "body": ref_id, "from": ref_id},
        )

        families = {s.family for s in signals}
        self.assertIn("authentication", families)
        self.assertIn("content_intent", families)
        self.assertIn("url_quishing", families)
        self.assertIn("infrastructure", families)
        self.assertIn("novelty", families)

        for sig in signals:
            self.assertGreaterEqual(sig.strength, 0.0)
            self.assertLessEqual(sig.strength, 1.0)
            self.assertIsNotNone(sig.raw_reason)
            self.assertIsNotNone(sig.evidence_reference_id)

    def test_weighted_scorer_family_ceiling_clamping(self):
        """Verify that no single family can exceed its assigned ceiling limit."""
        # Inject 4 strong content signals that would exceed 35 pts if uncapped
        signals = [
            NormalizedSignal(family="content_intent", name="Signal 1", strength=1.0, raw_reason="Reason 1"),
            NormalizedSignal(family="content_intent", name="Signal 2", strength=1.0, raw_reason="Reason 2"),
            NormalizedSignal(family="content_intent", name="Signal 3", strength=1.0, raw_reason="Reason 3"),
            NormalizedSignal(family="content_intent", name="Signal 4", strength=1.0, raw_reason="Reason 4"),
        ]
        verdict = WeightedScorer.compute(signals=signals, conflicts=[])

        content_points = verdict.family_breakdown["content_intent"]["allocated_points"]
        ceiling = verdict.family_breakdown["content_intent"]["ceiling_points"]

        self.assertEqual(ceiling, 35)
        self.assertEqual(content_points, 35)
        self.assertLessEqual(verdict.score, 35)

    def test_weighted_scorer_additive_math_and_conflicts(self):
        """Verify additive point calculation with positive conflict adjustment."""
        signals = [
            NormalizedSignal(family="authentication", name="DMARC Failure", strength=1.0, raw_reason="DMARC reject"),
            NormalizedSignal(family="content_intent", name="BEC Intent", strength=1.0, raw_reason="Wire instruction"),
        ]
        conflicts = [
            {"conflict_type": "reply_path_divergence", "score_adjustment": 20},
        ]
        verdict = WeightedScorer.compute(signals=signals, conflicts=conflicts)

        auth_pts = verdict.family_breakdown["authentication"]["allocated_points"]
        content_pts = verdict.family_breakdown["content_intent"]["allocated_points"]
        conflict_pts = sum(c["points"] for c in verdict.contributions if c["family"] == "conflicts")

        self.assertEqual(auth_pts, 28)
        self.assertEqual(content_pts, 22)
        self.assertEqual(conflict_pts, 20)
        self.assertEqual(verdict.score, 28 + 22 + 20)  # 70
        self.assertEqual(verdict.verdict, "High")

    def test_first_contact_guardrail_safety_assertion(self):
        """Verify F4 guardrail prevents novelty alone from triggering High/Critical verdict."""
        # Scenario: Clean message with mild infrastructure anomaly (8 pts), low intent (5 pts), and novelty (10 pts)
        contributions = [
            {"signal": "First-Contact Sender Domain", "family": "novelty", "points": 10},
            {"signal": "Generic Routing Delay", "family": "infrastructure", "points": 8},
            {"signal": "Informational Intent", "family": "content_intent", "points": 5},
        ]
        raw_score = 56  # Reaches 'High' threshold (55) if uncapped

        final_score, verdict, suppressed, reason = apply_first_contact_guardrail(
            raw_score=raw_score,
            contributions=contributions,
            has_hard_threat_signals=False,
            threshold=55,
        )

        self.assertTrue(suppressed)
        self.assertEqual(final_score, 46)  # 56 - 10
        self.assertEqual(verdict, "Elevated")  # Dropped from High to Elevated
        self.assertIn("novelty alone cannot trigger a High/Critical threat verdict", reason)

    def test_score_explainer_formatting_and_ordering(self):
        """Verify ScoreExplainer sorts contributions by impact and preserves evidence references."""
        ref_id = str(uuid.uuid4())
        signals = [
            NormalizedSignal(family="novelty", name="Novelty", strength=0.35, raw_reason="First contact", evidence_reference_id=ref_id),
            NormalizedSignal(family="authentication", name="DMARC Fail", strength=1.0, raw_reason="Rejected", evidence_reference_id=ref_id),
            NormalizedSignal(family="content_intent", name="BEC Wire Fraud", strength=1.0, raw_reason="Wire change", evidence_reference_id=ref_id),
        ]
        verdict = WeightedScorer.compute(signals=signals, conflicts=[])

        # Verify contributions are sorted descending by point impact
        points = [c["points"] for c in verdict.contributions]
        self.assertEqual(points, sorted(points, reverse=True))

        for c in verdict.contributions:
            self.assertIn("signal", c)
            self.assertIn("family", c)
            self.assertIn("points", c)
            self.assertIn("reason", c)

    def test_non_certainty_linguistic_guardrail(self):
        """Verify that no scoring explanation or disclaimer claims absolute certainty or legal attribution."""
        signals = [
            NormalizedSignal(family="content_intent", name="Hostile BEC Scam", strength=1.0, raw_reason="Fraud cue"),
        ]
        conflicts = [
            {"conflict_type": "auth_pass_vs_content_risk", "score_adjustment": 25},
        ]
        verdict = WeightedScorer.compute(signals=signals, conflicts=conflicts)

        disallowed_phrases = [
            "100% malicious", "confirmed attacker", "guaranteed phish", "court-admissible certificate", "absolute certainty"
        ]

        text_corpus = f"{verdict.disclaimer} {verdict.narrative_summary}".lower()
        for phrase in disallowed_phrases:
            self.assertNotIn(phrase, text_corpus)

        self.assertIn("legal determination", verdict.disclaimer.lower())
        self.assertIn("triage aid", verdict.disclaimer.lower())


if __name__ == "__main__":
    unittest.main()
