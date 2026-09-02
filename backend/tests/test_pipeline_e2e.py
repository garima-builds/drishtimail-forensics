"""Comprehensive End-to-End Pipeline Verification Test (SIH26106).

Validates the full chain:
UPLOAD .EML
→ MIME PARSING
→ AUTHENTICATION ANALYSIS & SEMANTICS (F5)
→ URL/QR ANALYSIS (F3)
→ THREAT DETECTION (M2)
→ EVIDENCE CONFLICTS (F1)
→ EXPLAINABLE SCORE (F8)
→ ORIGIN/GEOLOCATION (M4)
→ CAMPAIGN CORRELATION & FIRST CONTACT (F4, F6)
→ EVIDENCE LEDGER (F7)
→ CASE/REPORT (M6)
"""
import unittest
import os
import sys
import uuid
from fastapi.testclient import TestClient
from sqlalchemy import select

# Ensure backend package is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app.database import Base, engine, get_db
from app.models import (
    User, Message, ParsedMessage, MimePart, AuthenticationResult,
    EvidenceConflict, ScoreExplanation, LedgerEntry, AnalysisRun, Case
)
from app.security import create_access_token


class TestPipelineE2E(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        from app.database import SessionLocal
        from app.main import seed_admin, seed_config
        with SessionLocal() as db:
            seed_admin(db)
            seed_config(db)
            admin_user = db.scalar(select(User).where(User.email == "admin@drishtimail.local"))
            cls.token = create_access_token(admin_user)
        cls.client = TestClient(app)
        cls.headers = {"Authorization": f"Bearer {cls.token}"}

    def test_complete_end_to_end_forensic_pipeline(self):
        """Execute and verify complete 11-step forensic analysis on an adversarial message."""
        test_uid = uuid.uuid4().hex[:8]
        
        # 1. Construct representative adversarial .eml message
        # Contains:
        # - Pass SPF/DKIM on lookalike domain (micros0ft-portal.xyz)
        # - Urgency & Wire Diversion / Executive Impersonation in body
        # - Display URL mismatch (anchor says login.microsoftonline.com, points to evil-auth.xyz)
        raw_eml_content = (
            f"From: Microsoft Security <alert@micros0ft-portal.xyz>\r\n"
            f"To: ceo@institution.ac.in\r\n"
            f"Subject: CRITICAL: Immediate Account Re-Verification Required {test_uid}\r\n"
            f"Date: Wed, 02 Sep 2026 14:30:00 +0000\r\n"
            f"Message-ID: <threat-{test_uid}@micros0ft-portal.xyz>\r\n"
            f"Received: from 198.51.100.42 by mx1.institution.ac.in; Wed, 02 Sep 2026 14:30:01 +0000\r\n"
            f"Authentication-Results: mx1.institution.ac.in; spf=pass (mx1: domain of alert@micros0ft-portal.xyz designates 198.51.100.42 as permitted sender); dkim=pass header.i=@micros0ft-portal.xyz; dmarc=pass\r\n"
            f"Content-Type: text/html; charset=utf-8\r\n\r\n"
            f"<html><body>"
            f"<p>URGENT: Your institutional credentials will expire in 2 hours.</p>"
            f"<p>Immediate executive action is required. Verify your credentials below:</p>"
            f"<a href=\"https://evil-auth.xyz/login?session={test_uid}\">https://login.microsoftonline.com/auth</a>"
            f"<p>Also please execute the pending vendor invoice wire transfer immediately.</p>"
            f"</body></html>"
        ).encode("utf-8")

        # Step 1: Upload .EML
        res_upload = self.client.post(
            "/api/v1/ingest/upload",
            headers=self.headers,
            files={"file": (f"phish_sample_{test_uid}.eml", raw_eml_content, "message/rfc822")},
        )
        self.assertIn(res_upload.status_code, [200, 201])
        msg_data = res_upload.json()
        msg_id = msg_data["id"]
        self.assertIsNotNone(msg_id)

        # Step 2: Fetch and verify complete Analysis Run results
        res_analysis = self.client.get(f"/api/v1/messages/{msg_id}/analysis", headers=self.headers)
        self.assertEqual(res_analysis.status_code, 200)
        analysis = res_analysis.json()
        self.assertIsNotNone(analysis)

        # Step 3: Verify Authentication Semantics (M3 / F5)
        auth = analysis.get("authentication", {})
        self.assertEqual(auth.get("spf"), "pass")
        self.assertEqual(auth.get("dkim"), "pass")
        self.assertTrue(auth.get("is_lookalike_authenticated"))
        self.assertIn("establishes", auth)
        self.assertIn("does_not_establish", auth)
        self.assertIn("investigation_effect", auth)

        # Step 4: Verify URL Extraction & Anchor Mismatch Detector (M9 / F3)
        urls = analysis.get("urls", [])
        self.assertGreaterEqual(len(urls), 1)
        mismatch_url = next((u for u in urls if u.get("mismatch_flag")), None)
        self.assertIsNotNone(mismatch_url, "Expected URL anchor mismatch to be detected")
        self.assertIn("evil-auth.xyz", mismatch_url.get("destination_host", ""))
        self.assertIn("login.microsoftonline.com", mismatch_url.get("anchor_text", ""))

        # Step 5: Verify NLP Intent & Threat Classifier (M2)
        detections = analysis.get("detections", {})
        classification = detections.get("classification", {})
        self.assertIn("predicted_class", classification)
        self.assertIn("probabilities", classification)
        self.assertIn(classification["predicted_class"], ["phishing", "bec_fraud", "impersonation"])
        # Check social engineering / BEC cues
        se_findings = detections.get("social_engineering", [])
        self.assertGreater(len(se_findings), 0)

        # Step 6: Verify Evidence Conflicts (M10 / F1)
        conflicts = analysis.get("conflicts", [])
        self.assertGreater(len(conflicts), 0)
        c_types = [c.get("conflict_type") for c in conflicts]
        # Should detect anchor mismatch conflict (C05) or auth pass vs content threat (C03)
        self.assertTrue(
            any(t in c_types for t in ["display_text_vs_destination_host", "auth_pass_vs_content_risk", "lookalike_sender_authenticated"]),
            f"Expected conflict among {c_types}"
        )
        # Verify dual-sided citations are populated
        sample_conflict = conflicts[0]
        self.assertTrue(bool(sample_conflict.get("evidence_side_a")))
        self.assertTrue(bool(sample_conflict.get("evidence_side_b")))

        # Step 7: Verify Explainable Threat Score (M11 / F8)
        score_data = analysis.get("score", {})
        self.assertIn(score_data.get("verdict"), ["Critical", "High"])
        self.assertGreaterEqual(score_data.get("value", 0), 55)
        self.assertIn("contributions", score_data)
        self.assertGreater(len(score_data["contributions"]), 0)
        self.assertIn("disclaimer", score_data)

        # Step 8: Verify Origin & Geolocation (M4)
        origin = analysis.get("origin", {})
        self.assertIn("ip", origin)
        self.assertIn("caveat", origin)

        # Step 9: Verify Correlation & Graph Fingerprinting (M5 / F6)
        struct_fp = analysis.get("structural_fingerprint", {})
        self.assertIn("hash", struct_fp)
        self.assertTrue(bool(struct_fp["hash"]))

        # Step 10: Verify Evidence Ledger Entry (M7 / F7)
        res_ledger = self.client.get("/api/v1/ledger/entries", headers=self.headers)
        self.assertEqual(res_ledger.status_code, 200)
        entries = res_ledger.json()
        msg_entries = [e for e in entries if e.get("subject_id") == msg_id]
        self.assertGreaterEqual(len(msg_entries), 1)

        # Step 11: Verify Forensic PDF Report & BSA Section 63 Metadata (M6)
        res_pdf = self.client.get(f"/api/v1/messages/{msg_id}/report.pdf")
        self.assertEqual(res_pdf.status_code, 200)
        self.assertEqual(res_pdf.headers.get("content-type"), "application/pdf")
        self.assertGreater(len(res_pdf.content), 500)
        # PDF starts with %PDF magic bytes
        self.assertTrue(res_pdf.content.startswith(b"%PDF"))


if __name__ == "__main__":
    unittest.main()
