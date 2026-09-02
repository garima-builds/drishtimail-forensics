"""End-to-End API and Pipeline Integration Tests."""
import unittest
import os
import sys
import uuid
from uuid import UUID
from fastapi.testclient import TestClient
from sqlalchemy import select

# Ensure backend package is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app.database import Base, engine, get_db
from app.models import User
from app.security import create_access_token


class TestApiEndpoints(unittest.TestCase):
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

    def test_01_dashboard_summary(self):
        """Verify dashboard summary endpoint."""
        res = self.client.get("/api/v1/dashboard/summary")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("total_messages", data)
        self.assertIn("critical", data)
        self.assertIn("high", data)

    def test_02_ingest_raw_headers_and_analyze(self):
        """Verify raw header paste ingestion and automatic forensic pipeline run."""
        test_uid = uuid.uuid4().hex[:8]
        raw_headers = (
            "From: Security Support <security@micros0ft-login.xyz>\n"
            "To: victim@university.edu\n"
            f"Subject: Urgent Security Update {test_uid}\n"
            "Date: Wed, 02 Sep 2026 11:00:00 +0000\n"
            f"Message-ID: <raw-header-{test_uid}@micros0ft-login.xyz>\n"
            "Received: from 198.51.100.99 by mx1.institution.ac.in; Wed, 02 Sep 2026 11:00:01 +0000\n"
            "Authentication-Results: mx1.institution.ac.in; spf=pass; dkim=pass; dmarc=pass header.from=micros0ft-login.xyz\n"
        )
        res = self.client.post(
            "/api/v1/ingest/raw-headers",
            headers=self.headers,
            json={"raw_headers": raw_headers, "subject": f"Urgent Security Update {test_uid}"},
        )
        self.assertIn(res.status_code, [200, 201])
        msg_data = res.json()
        self.assertIn("id", msg_data)
        msg_id = msg_data["id"]

        # Fetch detailed analysis result
        res_analysis = self.client.get(f"/api/v1/messages/{msg_id}/analysis", headers=self.headers)
        self.assertEqual(res_analysis.status_code, 200)
        analysis = res_analysis.json()
        self.assertIsNotNone(analysis)
        self.assertIn("score", analysis)
        self.assertIn("authentication", analysis)
        self.assertIn("origin", analysis)

    def test_03_cases_workflow(self):
        """Verify case creation and notes update workflow."""
        # Create case
        res_create = self.client.post(
            "/api/v1/cases",
            headers=self.headers,
            json={"title": "Phishing Incident Q3-2026", "message_ids": []},
        )
        self.assertEqual(res_create.status_code, 201)
        case_data = res_create.json()
        case_id = case_data["id"]
        self.assertEqual(case_data["title"], "Phishing Incident Q3-2026")

        # Update case note
        res_update = self.client.patch(
            f"/api/v1/cases/{case_id}",
            headers=self.headers,
            json={"status": "In Investigation", "note": "Initial triage completed. High priority."},
        )
        self.assertEqual(res_update.status_code, 200)
        updated = res_update.json()
        self.assertEqual(updated["status"], "In Investigation")
        self.assertEqual(len(updated["notes"]), 1)

    def test_04_ioc_export_formats(self):
        """Verify STIX 2.1, MISP, and CSV IOC exports."""
        # STIX export
        res_stix = self.client.get("/api/v1/export/iocs?format=stix")
        self.assertEqual(res_stix.status_code, 200)
        stix_data = res_stix.json()
        self.assertEqual(stix_data.get("type"), "bundle")

        # CSV export
        res_csv = self.client.get("/api/v1/export/iocs?format=csv")
        self.assertEqual(res_csv.status_code, 200)
        self.assertIn("indicator_type", res_csv.text)

    def test_05_admin_config_get_and_put(self):
        """Verify platform configuration retrieval and modification."""
        # Get trusted MTAs
        res_get = self.client.get("/api/v1/admin/config/trusted_mtas")
        self.assertEqual(res_get.status_code, 200)

        # Update scoring thresholds
        res_put = self.client.put(
            "/api/v1/admin/config/scoring",
            headers=self.headers,
            json={"value": {"critical": 70, "high": 50, "elevated": 20}},
        )
        self.assertEqual(res_put.status_code, 200)
        self.assertEqual(res_put.json()["value"]["critical"], 70)

    def test_06_bulk_zip_ingest(self):
        """Verify bulk zip ingestion of multiple .eml messages."""
        import zipfile
        import io
        buf = io.BytesIO()
        test_id1 = uuid.uuid4().hex[:8]
        test_id2 = uuid.uuid4().hex[:8]
        with zipfile.ZipFile(buf, "w") as zf:
            eml1 = f"From: a@test.com\nTo: b@test.com\nSubject: Bulk 1 {test_id1}\nMessage-ID: <b1-{test_id1}@test.com>\n\nBody 1 {test_id1}".encode()
            eml2 = f"From: c@test.com\nTo: d@test.com\nSubject: Bulk 2 {test_id2}\nMessage-ID: <b2-{test_id2}@test.com>\n\nBody 2 {test_id2}".encode()
            zf.writestr("mail1.eml", eml1)
            zf.writestr("mail2.eml", eml2)
        buf.seek(0)

        res = self.client.post(
            "/api/v1/ingest/bulk-zip",
            headers=self.headers,
            files={"file": ("batch.zip", buf, "application/zip")},
        )
        self.assertEqual(res.status_code, 201)
        items = res.json()
        self.assertIsInstance(items, list)
        self.assertEqual(len(items), 2)


if __name__ == "__main__":
    unittest.main()
