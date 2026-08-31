from contextlib import asynccontextmanager
from html import escape
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile, status
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .config import settings
from .database import Base, engine, get_db
from .analysis import analyze_message, authentication_semantics, campaign_summary, extract_urls
from .evidence import add_reference, append_ledger, persist_original, seal_merkle_root
from .models import AnalysisRun, AuthenticationResult, Case, CaseMessage, EvidenceReference, LedgerEntry, MerkleRoot, Message, ParsedMessage, PlatformConfig, UrlArtifact, User
from .parser import parse_email
from .schemas import AuthenticationResultOut, CaseCreate, CaseOut, CaseUpdate, ConfigUpdate, DashboardSummary, EvidenceReferenceOut, IngestedMessageOut, LedgerEntryOut, LoginRequest, MerkleRootOut, MessageCreate, MessageOut, TokenResponse, UrlArtifactOut
from .security import create_access_token, password_hash, require_roles


def seed_messages(db: Session) -> None:
    if db.scalar(select(func.count()).select_from(Message)):
        return
    db.add_all([
        Message(sender="accounts@micros0ft-support.example", subject="Action required: M365 account verification", verdict="Critical", score=92, confidence="High", status="New", evidence_reference="headers:From[0-42]; body:text[114-293]", summary="Lookalike sender, DMARC misalignment, and a QR-originated redirect require review."),
        Message(sender="registrar@university.edu", subject="Updated academic calendar", verdict="Low", score=12, confidence="High", status="Closed", evidence_reference="headers:Received[0-180]; body:text[0-187]", summary="Authenticated institutional sender with no material anomalies."),
    ])
    db.commit()


def seed_admin(db: Session) -> None:
    if not db.scalar(select(User).where(User.email == "admin@drishtimail.local")):
        db.add(User(email="admin@drishtimail.local", password_hash=password_hash.hash("ChangeMe!2026"), role="admin"))
        db.commit()


def seed_config(db: Session) -> None:
    defaults = {
        "trusted_mtas": {"hosts": []}, "protected_identities": {"values": []},
        "scoring": {"critical": 75, "high": 55, "elevated": 25},
        "retention": {"body_days": 90, "header_days": 365, "legal_hold": True},
    }
    for key, value in defaults.items():
        if not db.get(PlatformConfig, key):
            db.add(PlatformConfig(key=key, value=value))
    db.commit()


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    with next(get_db()) as db:
        seed_admin(db)
        seed_config(db)
        seed_messages(db)
    yield


app = FastAPI(title="DrishtiMail Forensics API", version="0.1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


@app.get("/health")
def health():
    return {"status": "ok", "service": "drishtimail-api"}


@app.get(f"{settings.api_prefix}/messages", response_model=list[MessageOut])
def list_messages(db: Session = Depends(get_db)):
    return db.scalars(select(Message).order_by(Message.received_at.desc())).all()


@app.post(f"{settings.api_prefix}/messages", response_model=MessageOut, status_code=status.HTTP_201_CREATED)
def create_message(payload: MessageCreate, db: Session = Depends(get_db)):
    message = Message(**payload.model_dump())
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


@app.post(f"{settings.api_prefix}/auth/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == payload.email.lower()))
    if not user or not password_hash.verify(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    return TokenResponse(access_token=create_access_token(user))


@app.post(f"{settings.api_prefix}/evidence/upload", response_model=EvidenceReferenceOut, status_code=status.HTTP_201_CREATED)
def upload_evidence(file: UploadFile = File(...), _: User = Depends(require_roles("admin", "investigator", "analyst")), db: Session = Depends(get_db)):
    data = file.file.read()
    if not data:
        raise HTTPException(status_code=422, detail="Uploaded evidence is empty")
    try:
        original = persist_original(db, filename=file.filename or "message.eml", content_type=file.content_type or "message/rfc822", data=data)
        reference = add_reference(db, evidence_object_id=original.id, byte_start=0, byte_end=len(data), description="Complete preserved original")
        append_ledger(db, event_type="evidence.ingested", subject_id=original.id, evidence_reference_id=reference.id, payload={"sha256": original.sha256, "byte_size": original.byte_size, "storage_key": original.storage_key})
        db.commit()
        db.refresh(reference)
        return reference
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=503, detail="Evidence storage is unavailable") from exc


@app.post(f"{settings.api_prefix}/ingest/upload", response_model=IngestedMessageOut, status_code=status.HTTP_201_CREATED)
def ingest_email(file: UploadFile = File(...), _: User = Depends(require_roles("admin", "investigator", "analyst")), db: Session = Depends(get_db)):
    if not (file.filename or "").lower().endswith(".eml") and file.content_type not in {"message/rfc822", "application/octet-stream"}:
        raise HTTPException(status_code=415, detail="Upload an RFC 5322 .eml message")
    raw = file.file.read()
    if not raw:
        raise HTTPException(status_code=422, detail="Uploaded message is empty")
    parsed = parse_email(raw)
    prior = db.scalar(select(ParsedMessage).where(ParsedMessage.dedupe_key == parsed.dedupe_key))
    if prior:
        message = db.get(Message, prior.message_id)
        return IngestedMessageOut(**MessageOut.model_validate(message).model_dump(), duplicate=True)
    try:
        original = persist_original(db, filename=file.filename or "message.eml", content_type="message/rfc822", data=raw)
        complete_ref = add_reference(db, evidence_object_id=original.id, byte_start=0, byte_end=len(raw), description="Complete preserved RFC 5322 message")
        message = Message(sender=parsed.sender, subject=parsed.subject, evidence_reference=str(complete_ref.id), summary="Ingested and awaiting forensic analysis")
        db.add(message)
        db.flush()
        evidence_map = {name: list(offsets) for name, offsets in parsed.header_ranges.items()}
        evidence_map["body"] = list(parsed.body_range)
        db.add(ParsedMessage(message_id=message.id, evidence_object_id=original.id, rfc_message_id=parsed.rfc_message_id, dedupe_key=parsed.dedupe_key, headers=parsed.headers, plain_text=parsed.plain_text, attachment_count=parsed.attachment_count, evidence_map=evidence_map))
        append_ledger(db, event_type="message.ingested", subject_id=message.id, evidence_reference_id=complete_ref.id, payload={"sha256": original.sha256, "message_id": parsed.rfc_message_id, "dedupe_key": parsed.dedupe_key})
        db.commit()
        db.refresh(message)
        return IngestedMessageOut(**MessageOut.model_validate(message).model_dump())
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=503, detail="Message ingestion is unavailable") from exc


@app.get(f"{settings.api_prefix}/evidence/{{reference_id}}", response_model=EvidenceReferenceOut)
def get_evidence_reference(reference_id: str, _: User = Depends(require_roles("admin", "investigator", "analyst")), db: Session = Depends(get_db)):
    reference = db.get(EvidenceReference, reference_id)
    if not reference:
        raise HTTPException(status_code=404, detail="Evidence reference not found")
    return reference


@app.get(f"{settings.api_prefix}/ledger/entries", response_model=list[LedgerEntryOut])
def list_ledger(_: User = Depends(require_roles("admin", "investigator")), db: Session = Depends(get_db)):
    return db.scalars(select(LedgerEntry).order_by(LedgerEntry.sequence)).all()


@app.get(f"{settings.api_prefix}/ledger/export")
def export_ledger(_: User = Depends(require_roles("admin", "investigator")), db: Session = Depends(get_db)):
    entries = db.scalars(select(LedgerEntry).order_by(LedgerEntry.sequence)).all()
    return {"entries": [LedgerEntryOut.model_validate(entry).model_dump(mode="json") for entry in entries]}


@app.post(f"{settings.api_prefix}/ledger/roots", response_model=MerkleRootOut, status_code=status.HTTP_201_CREATED)
def create_merkle_root(_: User = Depends(require_roles("admin", "investigator")), db: Session = Depends(get_db)):
    try:
        root = seal_merkle_root(db)
        db.commit()
        db.refresh(root)
        return root
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.post(f"{settings.api_prefix}/messages/{{message_id}}/analyze/authentication", response_model=AuthenticationResultOut, status_code=status.HTTP_201_CREATED)
def analyze_authentication(message_id: str, _: User = Depends(require_roles("admin", "investigator", "analyst")), db: Session = Depends(get_db)):
    prior = db.scalar(select(AuthenticationResult).where(AuthenticationResult.message_id == message_id))
    if prior:
        return prior
    parsed = db.scalar(select(ParsedMessage).where(ParsedMessage.message_id == message_id))
    if not parsed:
        raise HTTPException(status_code=404, detail="Preserved message not found")
    result = authentication_semantics(parsed.headers)
    start, end = parsed.evidence_map.get("authentication-results", parsed.evidence_map.get("body", [0, 0]))
    reference = add_reference(db, evidence_object_id=parsed.evidence_object_id, byte_start=start, byte_end=end, header_name="Authentication-Results", description="Authentication semantics source header")
    record = AuthenticationResult(message_id=message_id, spf=result.spf, dkim=result.dkim, dmarc=result.dmarc, semantics_key=result.key, establishes=result.establishes, does_not_establish=result.does_not_establish, investigation_effect=result.effect, evidence_reference_id=reference.id)
    db.add(record)
    append_ledger(db, event_type="analysis.authentication", subject_id=record.message_id, evidence_reference_id=reference.id, payload={"semantics_key": result.key})
    db.commit(); db.refresh(record)
    return record


@app.post(f"{settings.api_prefix}/messages/{{message_id}}/analyze/urls", response_model=list[UrlArtifactOut], status_code=status.HTTP_201_CREATED)
def analyze_urls(message_id: str, _: User = Depends(require_roles("admin", "investigator", "analyst")), db: Session = Depends(get_db)):
    existing = db.scalars(select(UrlArtifact).where(UrlArtifact.message_id == message_id)).all()
    if existing:
        return existing
    parsed = db.scalar(select(ParsedMessage).where(ParsedMessage.message_id == message_id))
    if not parsed:
        raise HTTPException(status_code=404, detail="Preserved message not found")
    start, end = parsed.evidence_map.get("body", [0, 0])
    reference = add_reference(db, evidence_object_id=parsed.evidence_object_id, byte_start=start, byte_end=end, mime_part_index=0, description="Plain-text body URL extraction source")
    records = [UrlArtifact(message_id=message_id, raw_url=raw, normalized_url=normalized, provenance="body", evidence_reference_id=reference.id) for raw, normalized in extract_urls(parsed.plain_text)]
    db.add_all(records)
    if records:
        append_ledger(db, event_type="analysis.urls", subject_id=records[0].message_id, evidence_reference_id=reference.id, payload={"count": len(records), "urls": [record.normalized_url for record in records]})
    db.commit()
    return records


@app.post(f"{settings.api_prefix}/messages/{{message_id}}/analyze")
def run_full_analysis(message_id: str, _: User = Depends(require_roles("admin", "investigator", "analyst")), db: Session = Depends(get_db)):
    existing = db.scalar(select(AnalysisRun).where(AnalysisRun.message_id == message_id))
    if existing:
        return existing.result
    message = db.get(Message, message_id)
    parsed = db.scalar(select(ParsedMessage).where(ParsedMessage.message_id == message_id))
    if not message or not parsed:
        raise HTTPException(status_code=404, detail="Preserved message not found")
    result = analyze_message(sender=message.sender, subject=message.subject, headers=parsed.headers, plain_text=parsed.plain_text, attachment_count=parsed.attachment_count)
    start, end = parsed.evidence_map.get("body", [0, 0])
    reference = add_reference(db, evidence_object_id=parsed.evidence_object_id, byte_start=start, byte_end=end, mime_part_index=0, description="Offline forensic analysis source")
    db.add(AnalysisRun(message_id=message.id, evidence_reference_id=reference.id, result=result))
    message.score = result["score"]["value"]
    message.verdict = result["score"]["verdict"]
    message.confidence = result["score"]["confidence"]
    message.summary = result["score"]["disclaimer"]
    append_ledger(db, event_type="analysis.completed", subject_id=message.id, evidence_reference_id=reference.id, payload={"score": result["score"]["value"], "verdict": result["score"]["verdict"], "conflict_count": len(result["conflicts"])})
    db.commit()
    return result


@app.get(f"{settings.api_prefix}/messages/{{message_id}}/analysis")
def get_full_analysis(message_id: str, _: User = Depends(require_roles("admin", "investigator", "analyst")), db: Session = Depends(get_db)):
    run = db.scalar(select(AnalysisRun).where(AnalysisRun.message_id == message_id))
    if not run:
        raise HTTPException(status_code=404, detail="No completed analysis for this message")
    return run.result


@app.get(f"{settings.api_prefix}/campaigns")
def list_campaigns(_: User = Depends(require_roles("admin", "investigator", "analyst")), db: Session = Depends(get_db)):
    runs = db.scalars(select(AnalysisRun)).all()
    return campaign_summary([(str(run.message_id), run.result) for run in runs])


def case_out(case: Case, db: Session) -> CaseOut:
    message_ids = db.scalars(select(CaseMessage.message_id).where(CaseMessage.case_id == case.id)).all()
    return CaseOut(id=case.id, title=case.title, status=case.status, owner_id=case.owner_id, notes=case.notes, created_at=case.created_at, message_ids=message_ids)


@app.get(f"{settings.api_prefix}/cases", response_model=list[CaseOut])
def list_cases(_: User = Depends(require_roles("admin", "investigator", "analyst")), db: Session = Depends(get_db)):
    return [case_out(case, db) for case in db.scalars(select(Case).order_by(Case.created_at.desc())).all()]


@app.post(f"{settings.api_prefix}/cases", response_model=CaseOut, status_code=status.HTTP_201_CREATED)
def create_case(payload: CaseCreate, user: User = Depends(require_roles("admin", "investigator", "analyst")), db: Session = Depends(get_db)):
    if payload.message_ids and db.scalar(select(func.count()).select_from(Message).where(Message.id.in_(payload.message_ids))) != len(payload.message_ids):
        raise HTTPException(status_code=404, detail="One or more messages do not exist")
    case = Case(title=payload.title, owner_id=user.id, notes=[])
    db.add(case); db.flush()
    db.add_all([CaseMessage(case_id=case.id, message_id=message_id) for message_id in payload.message_ids])
    db.commit(); db.refresh(case)
    return case_out(case, db)


@app.patch(f"{settings.api_prefix}/cases/{{case_id}}", response_model=CaseOut)
def update_case(case_id: str, payload: CaseUpdate, _: User = Depends(require_roles("admin", "investigator", "analyst")), db: Session = Depends(get_db)):
    case = db.get(Case, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    if payload.status:
        case.status = payload.status
    if payload.note:
        case.notes = [*case.notes, {"at": "recorded", "text": payload.note}]
    db.commit(); db.refresh(case)
    return case_out(case, db)


@app.get(f"{settings.api_prefix}/admin/config/{{key}}")
def get_config(key: str, _: User = Depends(require_roles("admin")), db: Session = Depends(get_db)):
    record = db.get(PlatformConfig, key)
    if not record:
        raise HTTPException(status_code=404, detail="Configuration key not found")
    return {"key": record.key, "value": record.value}


@app.put(f"{settings.api_prefix}/admin/config/{{key}}")
def update_config(key: str, payload: ConfigUpdate, _: User = Depends(require_roles("admin")), db: Session = Depends(get_db)):
    record = db.get(PlatformConfig, key)
    if record:
        record.value = payload.value
    else:
        record = PlatformConfig(key=key, value=payload.value); db.add(record)
    db.commit()
    return {"key": key, "value": record.value}


@app.get(f"{settings.api_prefix}/messages/{{message_id}}/report", response_class=HTMLResponse)
def export_report(message_id: str, _: User = Depends(require_roles("admin", "investigator")), db: Session = Depends(get_db)):
    message = db.get(Message, message_id)
    run = db.scalar(select(AnalysisRun).where(AnalysisRun.message_id == message_id))
    if not message or not run:
        raise HTTPException(status_code=404, detail="A completed analysis is required before reporting")
    root = db.scalar(select(MerkleRoot).order_by(MerkleRoot.to_sequence.desc()).limit(1))
    score = run.result["score"]
    contributions = "".join(f"<li>{escape(item['signal'])}: {item['points']} points — {escape(item['reason'])}</li>" for item in score["contributions"])
    integrity = root.root_hash if root else "No Merkle root sealed yet"
    return f"<!doctype html><title>DrishtiMail Forensic Report</title><main><h1>DrishtiMail Forensic Report</h1><p><b>Subject:</b> {escape(message.subject)}<br><b>Sender:</b> {escape(message.sender)}<br><b>Verdict:</b> {escape(score['verdict'])} ({score['value']}/100)</p><h2>Explainable score</h2><ul>{contributions}</ul><h2>Evidence integrity</h2><p>Analysis reference: {escape(str(run.evidence_reference_id))}<br>Merkle root: {escape(integrity)}</p><h2>Authentication semantics</h2><p>{escape(run.result['authentication']['investigation_effect'])}</p><footer>Generated by DrishtiMail Forensics. This report is an investigative aid, not an identity attribution.</footer></main>"


@app.get(f"{settings.api_prefix}/messages/{{message_id}}", response_model=MessageOut)
def get_message(message_id: str, db: Session = Depends(get_db)):
    message = db.get(Message, message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    return message


@app.get(f"{settings.api_prefix}/dashboard/summary", response_model=DashboardSummary)
def dashboard_summary(db: Session = Depends(get_db)):
    messages = db.scalars(select(Message)).all()
    return DashboardSummary(total_messages=len(messages), critical=sum(m.verdict == "Critical" for m in messages), high=sum(m.verdict == "High" for m in messages), elevated=sum(m.verdict == "Elevated" for m in messages), new=sum(m.status == "New" for m in messages))
