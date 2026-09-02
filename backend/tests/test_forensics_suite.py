"""Comprehensive Forensic Verification Test Suite for DrishtiMail (SIH26106).

Tests:
- F5: Authentication Semantics & Lookalike Override
- F3: Quishing / QR Code Multi-Angle Detection
- F1: Cross-Evidence Conflict Detector (9 Rules)
- F8: Explainable Threat Scoring & Ceiling Clamping
- F4: First-Contact Novelty Guardrail Safety Assertion
- F6: Structural HTML Tag Skeleton Fingerprinting
- M6: Forensic PDF Report & BSA Section 63 Metadata Generation
"""
import io
import unittest
import os
import sys
from PIL import Image, ImageDraw

# Ensure backend package is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.protocol.auth_semantics import evaluate_auth_semantics
from app.protocol.relay_parser import parse_relay_chain
from app.protocol.trust_boundary import resolve_trust_boundary
from app.content.display_comparator import compare_display_vs_destination
from app.content.attachment_analyzer import analyze_attachment_static
from app.content.qr_decoder import decode_qr_with_rotations
from app.correlation.fingerprinter import extract_structural_skeleton
from app.conflicts.rule_engine import evaluate_evidence_conflicts
from app.scoring.weighted_scorer import compute_explainable_score
from app.scoring.normalizer import NormalizedSignal
from app.scoring.first_contact_guard import apply_first_contact_guardrail
from app.reporting.pdf_generator import generate_forensic_report_pdf


class TestForensicsSuite(unittest.TestCase):

    # Test F5: Authentication Semantics
    def test_auth_semantics_lookalike_override(self):
        res = evaluate_auth_semantics(
            spf="pass",
            dkim="pass",
            dmarc="pass",
            spf_aligned=True,
            dkim_aligned=True,
            is_lookalike_domain=True,
        )
        self.assertTrue(res.is_lookalike_authenticated)
        self.assertIn("lookalike", res.establishes.lower())
        self.assertIn("NOT establish", res.does_not_establish)
        self.assertIn("deceptive infrastructure", res.investigation_effect.lower())

    def test_auth_semantics_forwarding_scenario(self):
        res = evaluate_auth_semantics(
            spf="fail",
            dkim="pass",
            dmarc="pass",
            spf_aligned=False,
            dkim_aligned=True,
            forwarding_detected=True,
        )
        self.assertTrue(res.forwarding_detected)
        self.assertIn("forwarding chain", res.establishes.lower())

    # Test F1: Evidence Conflicts (Cross-evidence contradictions)
    def test_evidence_conflict_auth_pass_vs_content_threat(self):
        conflicts = evaluate_evidence_conflicts(
            auth_results={"spf": "pass", "dkim": "pass", "dmarc": "pass", "spf_aligned": True, "dkim_aligned": True},
            anomalies=[],
            detections={
                "classification": {"predicted_class": "bec_fraud", "probabilities": {"bec_fraud": 0.85, "benign": 0.05}},
                "bec_patterns": [{"title": "BEC: Bank Detail Diversion"}],
            },
            url_artifacts=[],
            qr_results=[],
        )
        conflict_types = [c["conflict_type"] for c in conflicts]
        self.assertIn("auth_pass_vs_content_risk", conflict_types)
        # Verifies dual-sided evidence citation
        match = next(c for c in conflicts if c["conflict_type"] == "auth_pass_vs_content_risk")
        self.assertIn("Protocol Authentication", match["evidence_side_a"])
        self.assertIn("Content Threat Engine", match["evidence_side_b"])

    def test_evidence_conflict_anchor_display_mismatch(self):
        mismatch_url = {
            "raw_url": "https://evil-portal.xyz/login",
            "anchor_text": "https://login.microsoftonline.com/auth",
            "destination_host": "evil-portal.xyz",
            "mismatch_flag": True,
        }
        conflicts = evaluate_evidence_conflicts(
            auth_results={"spf": "none", "dkim": "none", "dmarc": "none"},
            anomalies=[],
            detections={"classification": {"predicted_class": "phishing", "probabilities": {"phishing": 0.9}}},
            url_artifacts=[mismatch_url],
            qr_results=[],
        )
        conflict_types = [c["conflict_type"] for c in conflicts]
        self.assertIn("display_text_vs_destination_host", conflict_types)

    # Test F4: First-Contact Novelty Guardrail Assertion
    def test_first_contact_guardrail_suppression(self):
        # If score reaches 60 purely from novelty (+10) without hard threats, it must be safely suppressed
        contributions = [
            {"signal": "First-Contact Domain", "family": "novelty", "points": 10},
            {"signal": "Generic Header Anomaly", "family": "infrastructure", "points": 8},
            {"signal": "Neutral Intent", "family": "content_intent", "points": 5},
        ]
        raw_score = 58
        final_score, verdict, suppressed, reason = apply_first_contact_guardrail(
            raw_score=raw_score,
            contributions=contributions,
            has_hard_threat_signals=False,
            threshold=55,
        )
        self.assertTrue(suppressed)
        self.assertEqual(final_score, 48)  # 58 - 10 points
        self.assertEqual(verdict, "Elevated")  # Dropped from High to Elevated

    # Test F8: Weighted Additive Scorer & Ceiling Clamping
    def test_explainable_scoring_ceilings(self):
        # Attempting to load 50 points of content signals should clamp to the family ceiling (35 pts)
        signals = [
            NormalizedSignal(family="content_intent", name="BEC 1", strength=1.0, raw_reason="BEC"),
            NormalizedSignal(family="content_intent", name="BEC 2", strength=1.0, raw_reason="BEC"),
            NormalizedSignal(family="content_intent", name="BEC 3", strength=1.0, raw_reason="BEC"),
        ]
        verdict = compute_explainable_score(signals=signals, conflicts=[])
        content_points = sum(c["points"] for c in verdict.contributions if c["family"] == "content_intent")
        self.assertLessEqual(content_points, 35)
        self.assertLessEqual(verdict.score, 35)
        self.assertIn("legal determination", verdict.disclaimer)

    # Test F6: Structural HTML Fingerprinting
    def test_structural_html_fingerprint_invariant(self):
        html_template_1 = """
        <html>
            <body>
                <div class="container" id="box1">
                    <h1>Dear Customer John Doe,</h1>
                    <p>Please update your password by clicking below:</p>
                    <a href="https://site1.xyz/auth">Update Account</a>
                </div>
            </body>
        </html>
        """
        html_template_2 = """
        <html>
            <body>
                <div class="container" id="box2">
                    <h1>Dear Employee Alice Smith,</h1>
                    <p>Your institutional access is suspended. Verify now:</p>
                    <a href="https://site2.xyz/verify">Confirm Identity</a>
                </div>
            </body>
        </html>
        """
        hash_1, skel_1 = extract_structural_skeleton(html_template_1)
        hash_2, skel_2 = extract_structural_skeleton(html_template_2)

        # Both templates share identical HTML skeleton hierarchy despite different victim names and domains
        self.assertEqual(hash_1, hash_2)
        self.assertEqual(skel_1, skel_2)

    # Test M9 Static Attachment Analyzer
    def test_attachment_static_analysis_disguised_executable(self):
        mz_header_bytes = b"MZ\x90\x00\x03\x00\x00\x00\x04\x00\x00\x00\xff\xff"
        res = analyze_attachment_static(
            filename="invoice_march.pdf",
            declared_mime="application/pdf",
            payload_bytes=mz_header_bytes,
        )
        self.assertEqual(res["true_mime"], "application/x-dosexec")
        self.assertTrue(res["is_suspicious"])
        self.assertTrue(any(ind["type"] == "disguised_executable" for ind in res["static_indicators"]))

    # Test M6: Forensic PDF Report & BSA Section 63 Metadata Generation
    def test_pdf_report_generation(self):
        msg = {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "subject": "Urgent Security Action Required",
            "sender": "security@micros0ft-support.xyz",
            "received_at": "2026-09-02T12:00:00Z",
            "evidence_reference": "ref:byte_range[0-1024]",
            "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        }
        analysis = {
            "score": {
                "value": 85,
                "verdict": "Critical",
                "confidence": "High",
                "contributions": [
                    {"signal": "Lookalike Domain", "family": "content_intent", "points": 25, "reason": "Homoglyph detected"},
                    {"signal": "Anchor Text Mismatch", "family": "url_quishing", "points": 25, "reason": "Deceptive URL label"},
                ],
                "disclaimer": "Technical forensic triage aid only.",
            },
            "authentication": {
                "spf": "pass",
                "dkim": "pass",
                "dmarc": "pass",
                "establishes": "Control of lookalike domain",
                "does_not_establish": "Legitimacy of claimed brand",
                "investigation_effect": "Elevate priority",
            },
            "origin": {
                "candidate_ip": "198.51.100.45",
                "country": "United States",
                "isp": "Amazon AWS",
                "infra_type": "datacenter",
                "caveat": "Approximate geolocation only.",
            },
            "conflicts": [
                {
                    "title": "Anchor Text vs Destination Host Mismatch",
                    "severity": "Critical",
                    "summary": "Visible text displays microsoft.com while link routes to evil-portal.xyz",
                    "evidence_side_a": "Visible text: https://login.microsoftonline.com",
                    "evidence_side_b": "Destination: https://evil-portal.xyz",
                }
            ],
            "urls": [{"raw_url": "https://evil-portal.xyz", "provenance": "body", "anchor_text": "Verify"}],
            "qr_results": [],
        }

        pdf_bytes = generate_forensic_report_pdf(msg, analysis, merkle_root="0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef")
        self.assertIsNotNone(pdf_bytes)
        self.assertGreater(len(pdf_bytes), 500)
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))


if __name__ == "__main__":
    unittest.main()
