import hashlib
import io
import json
from uuid import UUID

from minio import Minio
from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import settings
from .models import EvidenceObject, EvidenceReference, LedgerEntry, MerkleRoot


def object_store() -> Minio:
    return Minio(settings.minio_endpoint, access_key=settings.minio_access_key, secret_key=settings.minio_secret_key, secure=False)


def persist_original(db: Session, *, filename: str, content_type: str, data: bytes) -> EvidenceObject:
    digest = hashlib.sha256(data).hexdigest()
    existing = db.scalar(select(EvidenceObject).where(EvidenceObject.sha256 == digest))
    if existing:
        return existing
    storage_key = f"originals/{digest[:2]}/{digest}.eml"
    client = object_store()
    if not client.bucket_exists(settings.minio_bucket):
        client.make_bucket(settings.minio_bucket)
    client.put_object(settings.minio_bucket, storage_key, io.BytesIO(data), len(data), content_type=content_type or "message/rfc822")
    record = EvidenceObject(sha256=digest, storage_key=storage_key, filename=filename or "message.eml", content_type=content_type or "message/rfc822", byte_size=len(data))
    db.add(record)
    db.flush()
    return record


def add_reference(db: Session, *, evidence_object_id: UUID, byte_start: int, byte_end: int, description: str, header_name: str | None = None, mime_part_index: int | None = None) -> EvidenceReference:
    original = db.get(EvidenceObject, evidence_object_id)
    if not original:
        raise ValueError("Evidence object does not exist")
    safe_start = max(0, min(byte_start, original.byte_size))
    safe_end = max(safe_start, min(byte_end, original.byte_size))
    reference = EvidenceReference(evidence_object_id=evidence_object_id, header_name=header_name, mime_part_index=mime_part_index, byte_start=safe_start, byte_end=safe_end, description=description)
    db.add(reference)
    db.flush()
    return reference


def append_ledger(db: Session, *, event_type: str, subject_id: UUID, evidence_reference_id: UUID, payload: dict) -> LedgerEntry:
    previous = db.scalar(select(LedgerEntry).order_by(LedgerEntry.sequence.desc()).limit(1))
    payload_hash = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    previous_hash = previous.entry_hash if previous else None
    chain_data = f"{previous_hash or ''}:{event_type}:{subject_id}:{evidence_reference_id}:{payload_hash}"
    entry = LedgerEntry(event_type=event_type, subject_id=subject_id, evidence_reference_id=evidence_reference_id, payload_hash=payload_hash, previous_hash=previous_hash, entry_hash=hashlib.sha256(chain_data.encode()).hexdigest())
    db.add(entry)
    db.flush()
    return entry


def merkle_hash(hashes: list[str]) -> str:
    if not hashes:
        raise ValueError("Cannot calculate a Merkle root for an empty ledger range")
    level = hashes[:]
    while len(level) > 1:
        if len(level) % 2:
            level.append(level[-1])
        level = [hashlib.sha256((level[i] + level[i + 1]).encode()).hexdigest() for i in range(0, len(level), 2)]
    return level[0]


def seal_merkle_root(db: Session) -> MerkleRoot:
    last_root = db.scalar(select(MerkleRoot).order_by(MerkleRoot.to_sequence.desc()).limit(1))
    start = (last_root.to_sequence + 1) if last_root else 1
    entries = db.scalars(select(LedgerEntry).where(LedgerEntry.sequence >= start).order_by(LedgerEntry.sequence)).all()
    if not entries:
        raise ValueError("No unsealed ledger entries")
    root = MerkleRoot(root_hash=merkle_hash([entry.entry_hash for entry in entries]), from_sequence=entries[0].sequence, to_sequence=entries[-1].sequence)
    db.add(root)
    db.flush()
    return root
