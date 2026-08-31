from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class MessageCreate(BaseModel):
    sender: str
    subject: str
    evidence_reference: str = Field(min_length=1)
    summary: str = "Queued for forensic analysis"


class MessageOut(BaseModel):
    id: UUID
    sender: str
    subject: str
    received_at: datetime
    verdict: str
    score: int
    confidence: str
    status: str
    evidence_reference: str
    summary: str

    model_config = {"from_attributes": True}


class DashboardSummary(BaseModel):
    total_messages: int
    critical: int
    high: int
    elevated: int
    new: int


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class EvidenceReferenceOut(BaseModel):
    id: UUID
    evidence_object_id: UUID
    header_name: str | None
    mime_part_index: int | None
    byte_start: int
    byte_end: int
    description: str

    model_config = {"from_attributes": True}


class IngestedMessageOut(MessageOut):
    duplicate: bool = False


class LedgerEntryOut(BaseModel):
    sequence: int
    event_type: str
    subject_id: UUID
    evidence_reference_id: UUID
    payload_hash: str
    previous_hash: str | None
    entry_hash: str
    created_at: datetime

    model_config = {"from_attributes": True}


class MerkleRootOut(BaseModel):
    root_hash: str
    from_sequence: int
    to_sequence: int
    computed_at: datetime

    model_config = {"from_attributes": True}


class AuthenticationResultOut(BaseModel):
    spf: str
    dkim: str
    dmarc: str
    semantics_key: str
    establishes: str
    does_not_establish: str
    investigation_effect: str
    evidence_reference_id: UUID

    model_config = {"from_attributes": True}


class UrlArtifactOut(BaseModel):
    raw_url: str
    normalized_url: str
    provenance: str
    evidence_reference_id: UUID

    model_config = {"from_attributes": True}


class CaseCreate(BaseModel):
    title: str = Field(min_length=3, max_length=256)
    message_ids: list[UUID] = []


class CaseOut(BaseModel):
    id: UUID
    title: str
    status: str
    owner_id: UUID | None
    notes: list
    created_at: datetime
    message_ids: list[UUID] = []

    model_config = {"from_attributes": True}


class CaseUpdate(BaseModel):
    status: str | None = None
    note: str | None = Field(default=None, max_length=2000)


class ConfigUpdate(BaseModel):
    value: dict
