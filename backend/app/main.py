from contextlib import asynccontextmanager
from datetime import datetime, timezone
from html import escape
import io
import os
from uuid import UUID
from fastapi import Depends, FastAPI, File, HTTPException, Query, Response, UploadFile, status
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .config import settings
from .database import Base, engine, get_db
from .evidence import add_reference, append_ledger, persist_original, seal_merkle_root
from .models import (
    AnalysisRun, AuthenticationResult, Case, CaseMessage, DeliveryHop, EvidenceConflict,
    EvidenceObject, EvidenceReference, GraphEdge, GraphNode, IndicatorHistory,
    LedgerEntry, MerkleRoot, Message, MimePart, ModelRegistry, OriginEnrichment,
    ParsedMessage, PlatformConfig, ScoreExplanation, StructuralFingerprint,
    UrlArtifact, AttachmentArtifact, User
)
from .parser import parse_email, parse_raw_headers
from .pipeline import execute_forensic_pipeline
from .reporting.pdf_generator import generate_forensic_report_pdf
from .correlation.graph_service import explore_graph_neighborhood, cluster_and_update_campaigns
from .correlation.ioc_exporter import export_indicators_to_csv, export_indicators_to_stix, export_indicators_to_misp
from .correlation.ioc_extractor import extract_all_iocs
from .evaluation.runner import run_model_evaluation
from .schemas import (
    AuthenticationResultOut, CaseCreate, CaseOut, CaseUpdate, ConfigUpdate,
    DashboardSummary, EvidenceReferenceOut, HeaderIngestRequest, IngestedMessageOut,
    LedgerEntryOut, LoginRequest, MerkleRootOut, MessageCreate, MessageOut,
    ModelRegistryOut, TokenResponse, UrlArtifactOut
)
from .security import create_access_token, password_hash, require_roles


def seed_admin(db: Session) -> None:
    if not db.scalar(select(User).where(User.email == "admin@drishtimail.local")):
        db.add(User(email="admin@drishtimail.local", password_hash=password_hash.hash("ChangeMe!2026"), role="admin"))
    if not db.scalar(select(User).where(User.email == "analyst@drishtimail.local")):
        db.add(User(email="analyst@drishtimail.local", password_hash=password_hash.hash("ChangeMe!2026"), role="analyst"))
    db.commit()


def seed_config(db: Session) -> None:
    defaults = {
        "trusted_mtas": {"hosts": ["mailgw.university.edu", "mx1.institution.ac.in"], "subnets": ["192.168.1.0/24", "10.10.0.0/16"]},
        "protected_identities": {"values": [{"name": "Dr. Sarah Mitchell", "email": "director@university.edu"}, {"name": "Prof. R. K. Sharma", "email": "registrar@university.edu"}]},
        "institutional_domains": {"domains": ["university.edu", "institution.ac.in"]},
        "scoring": {"critical": 75, "high": 55, "elevated": 25},
        "retention": {"body_days": 90, "header_days": 365, "legal_hold": True},
    }
    for key, value in defaults.items():
        if not db.get(PlatformConfig, key):
            db.add(PlatformConfig(key=key, value=value))
    db.commit()


def seed_sample_investigations(db: Session) -> None:
    if db.scalar(select(func.count()).select_from(Message)):
        return

    # Sample Case 1: Quishing & Lookalike Threat
    eml_sample_1 = (
        b"From: IT Support <security@micros0ft-m365-auth.xyz>\r\n"
        b"To: analyst@university.edu\r\n"
        b"Subject: Action Required: Mandatory Microsoft 365 Security Re-authentication\r\n"
        b"Date: Wed, 02 Sep 2026 09:15:00 +0000\r\n"
        b"Message-ID: <auth-notice-9921@micros0ft-m365-auth.xyz>\r\n"
        b"Received: from external-relay.xyz ([198.51.100.45]) by mx1.institution.ac.in with ESMTP id 88123; Wed, 02 Sep 2026 09:15:02 +0000\r\n"
        b"Received-SPF: pass (external-relay.xyz: domain of security@micros0ft-m365-auth.xyz designates 198.51.100.45 as permitted sender)\r\n"
        b"Authentication-Results: mx1.institution.ac.in; dkim=pass header.i=@micros0ft-m365-auth.xyz; dmarc=pass action=none header.from=micros0ft-m365-auth.xyz\r\n"
        b"Content-Type: text/html; charset=UTF-8\r\n\r\n"
        b"<html><body>"
        b"<p>Dear Faculty Member,</p>"
        b"<p>Your institutional account access will be terminated within 24 hours due to an expiring SSL token.</p>"
        b"<p>Scan the QR code below using your mobile device camera to confirm your password:</p>"
        b"<p><a href=\"https://evil-phish-server.xyz/login?id=8831\">https://login.microsoftonline.com/verify-token</a></p>"
        b"<div style=\"display:none\">system-session-validation-noise-token-bypass-tag</div>"
        b"</body></html>"
    )

    parsed_1 = parse_email(eml_sample_1)
    orig_1 = persist_original(db, filename="quishing_attack.eml", content_type="message/rfc822", data=eml_sample_1)
    ref_1 = add_reference(db, evidence_object_id=orig_1.id, byte_start=0, byte_end=len(eml_sample_1), description="Preserved Quishing Sample")
    msg_1 = Message(sender=parsed_1.sender, subject=parsed_1.subject, verdict="Critical", score=94, confidence="High", status="New", evidence_reference=str(ref_1.id), summary="Lookalike domain, anchor text mismatch, and adversarial concealment detected.")
    db.add(msg_1)
    db.flush()

    db.add(ParsedMessage(
        message_id=msg_1.id,
        evidence_object_id=orig_1.id,
        rfc_message_id=parsed_1.rfc_message_id,
        dedupe_key=parsed_1.dedupe_key,
        headers=parsed_1.headers,
        plain_text=parsed_1.plain_text,
        html_body=parsed_1.html_body,
        attachment_count=parsed_1.attachment_count,
        evidence_map=parsed_1.evidence_map,
    ))

    # Sample Case 2: BEC / Account Compromise with Aligned DMARC
    eml_sample_2 = (
        b"From: Prof. R. K. Sharma <registrar@university.edu>\r\n"
        b"Reply-To: r.k.sharma.exec@gmail.com\r\n"
        b"To: finance@university.edu\r\n"
        b"Subject: Urgent: Updated Bank Details for Vendor Remittance Payment\r\n"
        b"Date: Wed, 02 Sep 2026 10:20:00 +0000\r\n"
        b"Message-ID: <legit-msg-4411@university.edu>\r\n"
        b"Received: from mailgw.university.edu ([203.0.113.12]) by mx1.institution.ac.in; Wed, 02 Sep 2026 10:20:01 +0000\r\n"
        b"Authentication-Results: mx1.institution.ac.in; spf=pass; dkim=pass header.d=university.edu; dmarc=pass header.from=university.edu\r\n"
        b"Content-Type: text/plain; charset=UTF-8\r\n\r\n"
        b"Dear Accounts Team,\n\n"
        b"Please note that our vendor has updated banking details for invoice #INV-2026-88. "
        b"Process the wire transfer immediately to the following new beneficiary account before end of day.\n\n"
        b"Beneficiary: Global Supplies Ltd\n"
        b"IBAN: GB29NWBK60161331926819\n"
        b"SWIFT: NWBKGB2L\n\n"
        b"Keep this confidential as I am in an executive meeting.\n"
    )

    parsed_2 = parse_email(eml_sample_2)
    orig_2 = persist_original(db, filename="bec_fraud.eml", content_type="message/rfc822", data=eml_sample_2)
    ref_2 = add_reference(db, evidence_object_id=orig_2.id, byte_start=0, byte_end=len(eml_sample_2), description="Preserved BEC Fraud Sample")
    msg_2 = Message(sender=parsed_2.sender, subject=parsed_2.subject, verdict="Critical", score=88, confidence="High", status="Investigating", evidence_reference=str(ref_2.id), summary="Cryptographic DMARC pass contradicted by wire fraud intent and Reply-To redirection.")
    db.add(msg_2)
    db.flush()

    db.add(ParsedMessage(
        message_id=msg_2.id,
        evidence_object_id=orig_2.id,
        rfc_message_id=parsed_2.rfc_message_id,
        dedupe_key=parsed_2.dedupe_key,
        headers=parsed_2.headers,
        plain_text=parsed_2.plain_text,
        html_body=parsed_2.html_body,
        attachment_count=parsed_2.attachment_count,
        evidence_map=parsed_2.evidence_map,
    ))

    # Sample Case 3: Legitimate Authenticated Institutional Mail
    eml_sample_3 = (
        b"From: Academic Office <academics@university.edu>\r\n"
        b"To: all-students@university.edu\r\n"
        b"Subject: Fall 2026 Semester Examination Schedule and Hall Tickets\r\n"
        b"Date: Wed, 02 Sep 2026 11:00:00 +0000\r\n"
        b"Message-ID: <official-exam-sched-01@university.edu>\r\n"
        b"Received: from mailgw.university.edu ([203.0.113.12]) by mx1.institution.ac.in; Wed, 02 Sep 2026 11:00:01 +0000\r\n"
        b"Authentication-Results: mx1.institution.ac.in; spf=pass; dkim=pass header.d=university.edu; dmarc=pass header.from=university.edu\r\n"
        b"Content-Type: text/plain; charset=UTF-8\r\n\r\n"
        b"Dear Students,\n\n"
        b"The examination schedule for the upcoming semester has been published on the official portal at https://university.edu/exams.\n"
        b"Hall tickets will be available for download starting Friday.\n\n"
        b"Best regards,\nAcademic Operations\n"
    )

    parsed_3 = parse_email(eml_sample_3)
    orig_3 = persist_original(db, filename="benign_exam_schedule.eml", content_type="message/rfc822", data=eml_sample_3)
    ref_3 = add_reference(db, evidence_object_id=orig_3.id, byte_start=0, byte_end=len(eml_sample_3), description="Preserved Benign Sample")
    msg_3 = Message(sender=parsed_3.sender, subject=parsed_3.subject, verdict="Low", score=8, confidence="High", status="Closed", evidence_reference=str(ref_3.id), summary="Legitimate authenticated institutional communication.")
    db.add(msg_3)
    db.flush()

    db.add(ParsedMessage(
        message_id=msg_3.id,
        evidence_object_id=orig_3.id,
        rfc_message_id=parsed_3.rfc_message_id,
        dedupe_key=parsed_3.dedupe_key,
        headers=parsed_3.headers,
        plain_text=parsed_3.plain_text,
        html_body=parsed_3.html_body,
        attachment_count=parsed_3.attachment_count,
        evidence_map=parsed_3.evidence_map,
    ))

    db.commit()

    # Run initial pipeline on seeded samples to populate artifacts
    try:
        execute_forensic_pipeline(db, msg_1.id)
        execute_forensic_pipeline(db, msg_2.id)
        execute_forensic_pipeline(db, msg_3.id)
    except Exception:
        pass


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    with next(get_db()) as db:
        seed_admin(db)
        seed_config(db)
        seed_sample_investigations(db)
    yield


app = FastAPI(title="DrishtiMail Forensics API", version="2.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


@app.get("/health")
def health():
    return {"status": "ok", "service": "drishtimail-api", "version": "2.0.0"}


# Auth Routes
@app.post(f"{settings.api_prefix}/auth/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == payload.email.lower()))
    if not user or not password_hash.verify(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    return TokenResponse(access_token=create_access_token(user))


# Ingestion Routes (M1 & M7)
@app.post(f"{settings.api_prefix}/ingest/upload", response_model=IngestedMessageOut, status_code=status.HTTP_201_CREATED)
def ingest_email_file(file: UploadFile = File(...), _: User = Depends(require_roles("admin", "investigator", "analyst")), db: Session = Depends(get_db)):
    raw = file.file.read()
    if not raw:
        raise HTTPException(status_code=422, detail="Uploaded file is empty")

    parsed = parse_email(raw)
    prior = db.scalar(select(ParsedMessage).where(ParsedMessage.dedupe_key == parsed.dedupe_key))
    if prior:
        message = db.get(Message, prior.message_id)
        return IngestedMessageOut(**MessageOut.model_validate(message).model_dump(), duplicate=True)

    try:
        orig = persist_original(db, filename=file.filename or "message.eml", content_type="message/rfc822", data=raw)
        ref = add_reference(db, evidence_object_id=orig.id, byte_start=0, byte_end=len(raw), description="Complete preserved RFC 5322 message")

        message = Message(sender=parsed.sender, subject=parsed.subject, evidence_reference=str(ref.id), summary="Ingested and ready for forensic analysis")
        db.add(message)
        db.flush()

        db.add(ParsedMessage(
            message_id=message.id,
            evidence_object_id=orig.id,
            rfc_message_id=parsed.rfc_message_id,
            dedupe_key=parsed.dedupe_key,
            headers=parsed.headers,
            plain_text=parsed.plain_text,
            html_body=parsed.html_body,
            attachment_count=parsed.attachment_count,
            evidence_map=parsed.evidence_map,
        ))

        # Store MIME parts
        for part in parsed.mime_parts:
            db.add(MimePart(
                message_id=message.id,
                evidence_object_id=orig.id,
                part_index=part.part_index,
                content_type=part.content_type,
                filename=part.filename,
                byte_start=part.byte_start,
                byte_end=part.byte_end,
                sha256=part.sha256,
            ))

        append_ledger(db, event_type="message.ingested", subject_id=message.id, evidence_reference_id=ref.id, payload={"sha256": orig.sha256, "rfc_id": parsed.rfc_message_id})
        db.commit()
        db.refresh(message)

        # Automatically trigger pipeline execution
        execute_forensic_pipeline(db, message.id)
        db.refresh(message)

        return IngestedMessageOut(**MessageOut.model_validate(message).model_dump())
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {exc}") from exc


@app.post(f"{settings.api_prefix}/ingest/bulk-zip", response_model=list[IngestedMessageOut], status_code=status.HTTP_201_CREATED)
def ingest_bulk_zip(file: UploadFile = File(...), _: User = Depends(require_roles("admin", "investigator", "analyst")), db: Session = Depends(get_db)):
    raw_zip = file.file.read()
    if not raw_zip:
        raise HTTPException(status_code=422, detail="Uploaded zip archive is empty")

    results: list[IngestedMessageOut] = []
    try:
        import zipfile
        with zipfile.ZipFile(io.BytesIO(raw_zip), "r") as zf:
            for item in zf.infolist():
                if item.is_dir() or not (item.filename.lower().endswith(".eml") or item.filename.lower().endswith(".txt")):
                    continue
                # Zip-slip prevention
                if ".." in item.filename or item.filename.startswith("/") or item.filename.startswith("\\"):
                    continue

                raw_eml = zf.read(item.filename)
                if not raw_eml:
                    continue

                parsed = parse_email(raw_eml)
                prior = db.scalar(select(ParsedMessage).where(ParsedMessage.dedupe_key == parsed.dedupe_key))
                if prior:
                    msg = db.get(Message, prior.message_id)
                    results.append(IngestedMessageOut(**MessageOut.model_validate(msg).model_dump(), duplicate=True))
                    continue

                base_fname = os.path.basename(item.filename)
                orig = persist_original(db, filename=base_fname or "message.eml", content_type="message/rfc822", data=raw_eml)
                ref = add_reference(db, evidence_object_id=orig.id, byte_start=0, byte_end=len(raw_eml), description=f"Bulk archive preserved: {base_fname}")

                message = Message(sender=parsed.sender, subject=parsed.subject, evidence_reference=str(ref.id), summary="Bulk ingested; analysis completed")
                db.add(message)
                db.flush()

                db.add(ParsedMessage(
                    message_id=message.id,
                    evidence_object_id=orig.id,
                    rfc_message_id=parsed.rfc_message_id,
                    dedupe_key=parsed.dedupe_key,
                    headers=parsed.headers,
                    plain_text=parsed.plain_text,
                    html_body=parsed.html_body,
                    attachment_count=parsed.attachment_count,
                    evidence_map=parsed.evidence_map,
                ))

                for part in parsed.mime_parts:
                    db.add(MimePart(
                        message_id=message.id,
                        evidence_object_id=orig.id,
                        part_index=part.part_index,
                        content_type=part.content_type,
                        filename=part.filename,
                        byte_start=part.byte_start,
                        byte_end=part.byte_end,
                        sha256=part.sha256,
                    ))

                append_ledger(db, event_type="message.ingested", subject_id=message.id, evidence_reference_id=ref.id, payload={"sha256": orig.sha256, "rfc_id": parsed.rfc_message_id, "bulk_source": file.filename})
                db.commit()
                db.refresh(message)

                execute_forensic_pipeline(db, message.id)
                db.refresh(message)
                results.append(IngestedMessageOut(**MessageOut.model_validate(message).model_dump(), duplicate=False))

    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="Invalid or corrupt ZIP archive")
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Bulk ingestion failed: {exc}") from exc

    return results


@app.post(f"{settings.api_prefix}/ingest/raw-headers", response_model=IngestedMessageOut, status_code=status.HTTP_201_CREATED)
def ingest_raw_headers(payload: HeaderIngestRequest, _: User = Depends(require_roles("admin", "investigator", "analyst")), db: Session = Depends(get_db)):
    raw_str = payload.get_raw_headers()
    if not raw_str or len(raw_str.strip()) < 10:
        raise HTTPException(status_code=400, detail="Valid raw headers string (min 10 characters) is required")
    parsed = parse_raw_headers(raw_str)
    prior = db.scalar(select(ParsedMessage).where(ParsedMessage.dedupe_key == parsed.dedupe_key))
    if prior:
        message = db.get(Message, prior.message_id)
        return IngestedMessageOut(**MessageOut.model_validate(message).model_dump(), duplicate=True)

    sender = payload.sender or parsed.sender
    subject = payload.subject or parsed.subject
    raw_bytes = raw_str.encode("utf-8")

    orig = persist_original(db, filename="raw_headers.txt", content_type="text/plain", data=raw_bytes)
    ref = add_reference(db, evidence_object_id=orig.id, byte_start=0, byte_end=len(raw_bytes), description="Pasted raw email headers")

    message = Message(sender=sender, subject=subject, evidence_reference=str(ref.id), summary="Header-only investigation queued")
    db.add(message)
    db.flush()

    db.add(ParsedMessage(
        message_id=message.id,
        evidence_object_id=orig.id,
        rfc_message_id=parsed.rfc_message_id,
        dedupe_key=parsed.dedupe_key,
        headers=parsed.headers,
        plain_text="",
        html_body="",
        attachment_count=0,
        evidence_map=parsed.evidence_map,
    ))

    append_ledger(db, event_type="headers.ingested", subject_id=message.id, evidence_reference_id=ref.id, payload={"sha256": orig.sha256})
    db.commit()
    db.refresh(message)

    execute_forensic_pipeline(db, message.id)
    db.refresh(message)
    return IngestedMessageOut(**MessageOut.model_validate(message).model_dump())


# Messages & Pipeline Execution Routes
@app.get(f"{settings.api_prefix}/messages", response_model=list[MessageOut])
def list_messages(db: Session = Depends(get_db)):
    return db.scalars(select(Message).order_by(Message.received_at.desc())).all()


@app.get(f"{settings.api_prefix}/messages/{{message_id}}", response_model=MessageOut)
def get_message(message_id: str, db: Session = Depends(get_db)):
    msg = db.get(Message, message_id)
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    return msg


@app.post(f"{settings.api_prefix}/messages/{{message_id}}/analyze")
def run_pipeline(message_id: str, _: User = Depends(require_roles("admin", "investigator", "analyst")), db: Session = Depends(get_db)):
    try:
        val_uuid = UUID(message_id)
        result = execute_forensic_pipeline(db, val_uuid)
        return result
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Pipeline execution failed: {exc}") from exc


@app.get(f"{settings.api_prefix}/messages/{{message_id}}/analysis")
def get_analysis_result(message_id: str, _: User = Depends(require_roles("admin", "investigator", "analyst")), db: Session = Depends(get_db)):
    val_uuid = UUID(message_id)
    run = db.scalar(select(AnalysisRun).where(AnalysisRun.message_id == val_uuid).order_by(AnalysisRun.created_at.desc()).limit(1))
    if not run or not run.result:
        return execute_forensic_pipeline(db, val_uuid)
    return run.result


# Graph & Campaign Routes (M5 / F6)
@app.get(f"{settings.api_prefix}/graph/explore")
def explore_graph(node_id: str | None = Query(None), db: Session = Depends(get_db)):
    return explore_graph_neighborhood(db, node_id_or_value=node_id or "")


@app.get(f"{settings.api_prefix}/campaigns")
def list_campaigns(db: Session = Depends(get_db)):
    return cluster_and_update_campaigns(db)


# IOC Export Routes (M5)
@app.get(f"{settings.api_prefix}/export/iocs")
def export_iocs(format: str = Query("json", enum=["json", "stix", "misp", "csv"]), db: Session = Depends(get_db)):
    nodes = db.scalars(select(GraphNode)).all()
    indicators = [
        {"indicator_type": n.node_type, "value": n.value, "first_seen": n.first_seen.isoformat(), "sighting_count": n.sighting_count, "provenance": "correlation_graph"}
        for n in nodes if n.node_type != "message"
    ]

    if format == "csv":
        csv_data = export_indicators_to_csv(indicators)
        return Response(content=csv_data, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=drishtimail_iocs.csv"})
    elif format == "stix":
        return export_indicators_to_stix(indicators)
    elif format == "misp":
        return export_indicators_to_misp(indicators)
    return {"indicators": indicators, "count": len(indicators)}


# PDF & HTML Report Routes (M6)
@app.get(f"{settings.api_prefix}/messages/{{message_id}}/report.pdf")
def get_report_pdf(message_id: str, db: Session = Depends(get_db)):
    val_uuid = UUID(message_id)
    msg = db.get(Message, val_uuid)
    run = db.scalar(select(AnalysisRun).where(AnalysisRun.message_id == val_uuid))
    if not msg or not run:
        raise HTTPException(status_code=404, detail="Completed analysis required before report generation")

    merkle = db.scalar(select(MerkleRoot).order_by(MerkleRoot.to_sequence.desc()).limit(1))
    root_str = merkle.root_hash if merkle else None

    pdf_bytes = generate_forensic_report_pdf(
        message_data={"id": str(msg.id), "subject": msg.subject, "sender": msg.sender, "received_at": msg.received_at.isoformat(), "evidence_reference": msg.evidence_reference},
        analysis_data=run.result,
        merkle_root=root_str,
    )
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=DrishtiMail_Report_{message_id[:8]}.pdf"}
    )


@app.get(f"{settings.api_prefix}/messages/{{message_id}}/report", response_class=HTMLResponse)
def get_report_html(message_id: str, db: Session = Depends(get_db)):
    val_uuid = UUID(message_id)
    msg = db.get(Message, val_uuid)
    run = db.scalar(select(AnalysisRun).where(AnalysisRun.message_id == val_uuid))
    if not msg or not run:
        raise HTTPException(status_code=404, detail="Completed analysis required before report generation")

    score = run.result.get("score", {})
    auth = run.result.get("authentication", {})
    contributions = "".join(f"<li><b>{escape(c.get('signal', ''))}</b> (+{c.get('points', 0)} pts): {escape(c.get('reason', ''))}</li>" for c in score.get("contributions", []))

    return f"""<!doctype html>
<html>
<head>
<title>DrishtiMail Forensic Report - {escape(msg.subject)}</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 40px; color: #25231f; background: #fffdfa; line-height: 1.5; }}
h1, h2 {{ color: #1e2824; }}
.badge {{ padding: 4px 8px; border-radius: 4px; font-weight: bold; background: #fbebd7; color: #b44b3f; }}
.card {{ border: 1px solid #e2ded5; border-radius: 8px; padding: 16px; margin: 16px 0; background: #f7f5ef; }}
</style>
</head>
<body>
<h1>DrishtiMail Forensic Investigation Report</h1>
<div class="card">
<p><b>Subject:</b> {escape(msg.subject)}<br>
<b>Sender:</b> {escape(msg.sender)}<br>
<b>Verdict:</b> <span class="badge">{escape(score.get('verdict', ''))}</span> (Score: {score.get('value', 0)}/100 | Confidence: {score.get('confidence', '')})</p>
</div>
<h2>1. Explainable Threat Contributions</h2>
<ul>{contributions}</ul>
<h2>2. Authentication Semantics (F5)</h2>
<p><b>Establishes:</b> {escape(auth.get('establishes', ''))}<br>
<b>Does NOT Establish:</b> <font color="#a83d31">{escape(auth.get('does_not_establish', ''))}</font><br>
<b>Investigation Effect:</b> {escape(auth.get('investigation_effect', ''))}</p>
<h2>3. BSA Section 63 Provenance Metadata</h2>
<p><b>Primary Evidence Reference:</b> {escape(msg.evidence_reference)}<br>
<b>Verification Tool:</b> DrishtiMail Standalone Offline Verifier (v2.0)</p>
<hr>
<p><i>Disclaimer: {escape(score.get('disclaimer', ''))}</i></p>
</body>
</html>"""


# Cases Routes (M6)
def case_out(case: Case, db: Session) -> CaseOut:
    msg_ids = db.scalars(select(CaseMessage.message_id).where(CaseMessage.case_id == case.id)).all()
    return CaseOut(id=case.id, title=case.title, status=case.status, owner_id=case.owner_id, notes=case.notes, created_at=case.created_at, message_ids=msg_ids)


@app.get(f"{settings.api_prefix}/cases", response_model=list[CaseOut])
def list_cases(db: Session = Depends(get_db)):
    return [case_out(c, db) for c in db.scalars(select(Case).order_by(Case.created_at.desc())).all()]


@app.post(f"{settings.api_prefix}/cases", response_model=CaseOut, status_code=status.HTTP_201_CREATED)
def create_case(payload: CaseCreate, user: User = Depends(require_roles("admin", "investigator", "analyst")), db: Session = Depends(get_db)):
    case = Case(title=payload.title, owner_id=user.id, notes=[])
    db.add(case)
    db.flush()
    for m_id in payload.message_ids:
        db.add(CaseMessage(case_id=case.id, message_id=m_id))
    db.commit()
    db.refresh(case)
    return case_out(case, db)


@app.patch(f"{settings.api_prefix}/cases/{{case_id}}", response_model=CaseOut)
def update_case(case_id: str, payload: CaseUpdate, db: Session = Depends(get_db)):
    case = db.get(Case, UUID(case_id))
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    if payload.status:
        case.status = payload.status
    if payload.note:
        case.notes = [*case.notes, {"at": datetime.now(timezone.utc).isoformat(), "text": payload.note}]
    db.commit()
    db.refresh(case)
    return case_out(case, db)


# ML Model Evaluation Routes (M12 / F2)
@app.post(f"{settings.api_prefix}/evaluation/run", response_model=ModelRegistryOut)
def trigger_evaluation(_: User = Depends(require_roles("admin", "analyst", "investigator")), db: Session = Depends(get_db)):
    return run_model_evaluation(db)


@app.get(f"{settings.api_prefix}/evaluation/registry", response_model=list[ModelRegistryOut])
def get_model_registry(db: Session = Depends(get_db)):
    return db.scalars(select(ModelRegistry).order_by(ModelRegistry.trained_at.desc())).all()


# Ledger & Merkle Root Routes (M7 / F7)
@app.get(f"{settings.api_prefix}/ledger/entries", response_model=list[LedgerEntryOut])
def list_ledger(_: User = Depends(require_roles("admin", "investigator")), db: Session = Depends(get_db)):
    return db.scalars(select(LedgerEntry).order_by(LedgerEntry.sequence)).all()


@app.post(f"{settings.api_prefix}/ledger/roots", response_model=MerkleRootOut, status_code=status.HTTP_201_CREATED)
def seal_root(_: User = Depends(require_roles("admin", "investigator")), db: Session = Depends(get_db)):
    root = seal_merkle_root(db)
    db.commit()
    db.refresh(root)
    return root


# Admin & Platform Config Routes (M8)
@app.get(f"{settings.api_prefix}/admin/config/{{key}}")
def get_config(key: str, db: Session = Depends(get_db)):
    cfg = db.get(PlatformConfig, key)
    if not cfg:
        raise HTTPException(status_code=404, detail="Config key not found")
    return {"key": cfg.key, "value": cfg.value}


@app.put(f"{settings.api_prefix}/admin/config/{{key}}")
def update_config(key: str, payload: ConfigUpdate, _: User = Depends(require_roles("admin")), db: Session = Depends(get_db)):
    cfg = db.get(PlatformConfig, key)
    if cfg:
        cfg.value = payload.value
    else:
        cfg = PlatformConfig(key=key, value=payload.value)
        db.add(cfg)
    db.commit()
    return {"key": key, "value": cfg.value}


# Dashboard Summary Route
@app.get(f"{settings.api_prefix}/dashboard/summary", response_model=DashboardSummary)
def get_dashboard_summary(db: Session = Depends(get_db)):
    messages = db.scalars(select(Message)).all()
    cases_count = db.scalar(select(func.count()).select_from(Case)) or 0
    return DashboardSummary(
        total_messages=len(messages),
        critical=sum(m.verdict == "Critical" for m in messages),
        high=sum(m.verdict == "High" for m in messages),
        elevated=sum(m.verdict == "Elevated" for m in messages),
        low=sum(m.verdict == "Low" for m in messages),
        new=sum(m.status == "New" for m in messages),
        total_cases=cases_count,
        active_campaigns=db.scalar(select(func.count()).select_from(GraphNode).where(GraphNode.sighting_count > 1)) or 0,
    )

