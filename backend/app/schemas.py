from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


# Auth & Users
class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: UUID
    email: str
    role: str
    created_at: datetime

    model_config = {"from_attributes": True}


# Evidence & Ledger (M7 / F7)
class EvidenceReferenceOut(BaseModel):
    id: UUID
    evidence_object_id: UUID
    header_name: str | None = None
    mime_part_index: int | None = None
    byte_start: int
    byte_end: int
    description: str

    model_config = {"from_attributes": True}


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


# M1 Ingestion
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


class IngestedMessageOut(MessageOut):
    duplicate: bool = False


class HeaderIngestRequest(BaseModel):
    headers_raw: str = Field(default="", min_length=0)
    raw_headers: str | None = None
    sender: str | None = None
    subject: str | None = None

    def get_raw_headers(self) -> str:
        return self.headers_raw or self.raw_headers or ""


class MimePartOut(BaseModel):
    id: UUID
    part_index: int
    content_type: str
    filename: str | None
    byte_start: int
    byte_end: int
    sha256: str

    model_config = {"from_attributes": True}


# M3 Header & Protocol
class AuthenticationResultOut(BaseModel):
    spf: str
    dkim: str
    dmarc: str
    spf_aligned: bool = False
    dkim_aligned: bool = False
    arc_status: str = "none"
    forwarding_detected: bool = False
    semantics_key: str
    establishes: str
    does_not_establish: str
    investigation_effect: str
    evidence_reference_id: UUID

    model_config = {"from_attributes": True}


class DeliveryHopOut(BaseModel):
    hop_no: int
    timestamp: datetime | None = None
    claimed_host: str | None = None
    real_ip: str | None = None
    rdns: str | None = None
    tls_version: str | None = None
    delay_seconds: float | None = None
    trust_status: str
    raw_header: str

    model_config = {"from_attributes": True}


# M4 Origin & Geolocation
class OriginEnrichmentOut(BaseModel):
    ip: str
    country: str | None = None
    country_code: str | None = None
    region: str | None = None
    city: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    accuracy_radius: int | None = None
    asn: int | None = None
    isp: str | None = None
    infra_type: str
    confidence: str
    caveat: str

    model_config = {"from_attributes": True}


class DomainIntelOut(BaseModel):
    domain: str
    registrar: str | None = None
    creation_date: datetime | None = None
    age_days: int | None = None
    nameservers: list[str] = []
    mail_records: list[str] = []
    high_risk_flags: list[str] = []

    model_config = {"from_attributes": True}


# M9 Content & URL
class UrlArtifactOut(BaseModel):
    raw_url: str
    normalized_url: str
    provenance: str
    destination_host: str | None = None
    redirect_chain: list[str] = []
    anchor_text: str | None = None
    mismatch_flag: bool = False
    evidence_reference_id: UUID

    model_config = {"from_attributes": True}


class AttachmentArtifactOut(BaseModel):
    filename: str
    declared_mime: str | None = None
    true_mime: str | None = None
    byte_size: int
    sha256: str
    static_indicators: list[dict] = []
    evidence_reference_id: UUID

    model_config = {"from_attributes": True}


# M2 Detections & Findings
class FindingOut(BaseModel):
    id: UUID
    title: str
    category: str
    severity: str
    contribution: float
    evidence_reference_id: UUID

    model_config = {"from_attributes": True}


# M10 Conflicts (F1)
class EvidenceConflictOut(BaseModel):
    conflict_type: str
    summary: str
    severity: str
    evidence_ref_a_id: UUID
    evidence_ref_b_id: UUID
    detail: dict

    model_config = {"from_attributes": True}


# M11 Explainable Score (F8)
class ScoreContribution(BaseModel):
    signal: str
    family: str
    points: int
    reason: str
    evidence_reference_id: UUID | None = None


class ScoreExplanationOut(BaseModel):
    score: int
    verdict: str
    confidence: str
    contributions: list[ScoreContribution]
    disclaimer: str
    first_contact_suppressed: bool = False

    model_config = {"from_attributes": True}


# M5 Correlation Graph (F6 / F4)
class GraphNodeOut(BaseModel):
    id: UUID
    node_type: str
    value: str
    first_seen: datetime
    sighting_count: int

    model_config = {"from_attributes": True}


class GraphEdgeOut(BaseModel):
    from_node: UUID
    to_node: UUID
    edge_type: str
    weight: float
    evidence_reference_id: UUID

    model_config = {"from_attributes": True}


class GraphExploreOut(BaseModel):
    nodes: list[GraphNodeOut]
    edges: list[GraphEdgeOut]


class IndicatorHistoryOut(BaseModel):
    indicator_type: str
    value: str
    first_seen: datetime
    last_seen: datetime
    sighting_count: int
    distinct_cases: int
    familiarity_band: str

    model_config = {"from_attributes": True}


class CampaignOut(BaseModel):
    id: UUID
    name: str
    shared_indicators: list[str]
    score: float
    status: str
    created_at: datetime
    message_count: int = 0

    model_config = {"from_attributes": True}


# M6 Cases & Workflow
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


# Summary & Admin
class DashboardSummary(BaseModel):
    total_messages: int
    critical: int
    high: int
    elevated: int
    low: int
    new: int
    total_cases: int = 0
    active_campaigns: int = 0


class ConfigUpdate(BaseModel):
    value: dict


class ModelRegistryOut(BaseModel):
    id: UUID
    version: str
    trained_at: datetime
    calibrated_at: datetime
    metrics: dict
    is_active: bool
    corpus_manifest: dict

    model_config = {"from_attributes": True}

