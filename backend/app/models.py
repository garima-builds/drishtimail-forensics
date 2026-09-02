import uuid
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, CheckConstraint, DateTime, Float, ForeignKey, Identity, Integer, JSON, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


# M7 / F7 Core Evidence Models
class EvidenceObject(Base):
    __tablename__ = "evidence_objects"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sha256: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    storage_key: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    filename: Mapped[str] = mapped_column(String(512), nullable=False)
    content_type: Mapped[str] = mapped_column(String(255), default="message/rfc822")
    byte_size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    ingested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class EvidenceReference(Base):
    __tablename__ = "evidence_references"
    __table_args__ = (
        CheckConstraint("byte_start >= 0", name="evidence_reference_start_nonnegative"),
        CheckConstraint("byte_end >= byte_start", name="evidence_reference_range_valid")
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    evidence_object_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("evidence_objects.id", ondelete="RESTRICT"), nullable=False, index=True)
    header_name: Mapped[str | None] = mapped_column(String(255))
    mime_part_index: Mapped[int | None] = mapped_column(Integer)
    byte_start: Mapped[int] = mapped_column(BigInteger, nullable=False)
    byte_end: Mapped[int] = mapped_column(BigInteger, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class LedgerEntry(Base):
    __tablename__ = "evidence_ledger"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sequence: Mapped[int] = mapped_column(BigInteger, Identity(always=True), nullable=False, unique=True)
    event_type: Mapped[str] = mapped_column(Text, nullable=False)
    subject_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    evidence_reference_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("evidence_references.id", ondelete="RESTRICT"), nullable=False)
    payload_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    previous_hash: Mapped[str | None] = mapped_column(String(64))
    entry_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class MerkleRoot(Base):
    __tablename__ = "merkle_roots"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    root_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    from_sequence: Mapped[int] = mapped_column(BigInteger, nullable=False)
    to_sequence: Mapped[int] = mapped_column(BigInteger, nullable=False)
    computed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(320), nullable=False, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(512), nullable=False)
    role: Mapped[str] = mapped_column(String(32), nullable=False, default="analyst")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# M1 Ingestion Models
class Message(Base):
    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sender: Mapped[str] = mapped_column(String(320), nullable=False)
    subject: Mapped[str] = mapped_column(String(998), nullable=False)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    verdict: Mapped[str] = mapped_column(String(20), default="Elevated")
    score: Mapped[int] = mapped_column(default=0)
    confidence: Mapped[str] = mapped_column(String(20), default="Medium")
    status: Mapped[str] = mapped_column(String(20), default="New")
    evidence_reference: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str] = mapped_column(Text, default="Awaiting analysis")


class MimePart(Base):
    __tablename__ = "mime_parts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("messages.id", ondelete="RESTRICT"), nullable=False, index=True)
    evidence_object_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("evidence_objects.id", ondelete="RESTRICT"), nullable=False)
    part_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content_type: Mapped[str] = mapped_column(String(255), nullable=False)
    filename: Mapped[str | None] = mapped_column(String(512))
    byte_start: Mapped[int] = mapped_column(BigInteger, nullable=False)
    byte_end: Mapped[int] = mapped_column(BigInteger, nullable=False)
    sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ParsedMessage(Base):
    __tablename__ = "parsed_messages"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("messages.id", ondelete="RESTRICT"), nullable=False, unique=True)
    evidence_object_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("evidence_objects.id", ondelete="RESTRICT"), nullable=False, unique=True)
    rfc_message_id: Mapped[str | None] = mapped_column(String(998), index=True)
    dedupe_key: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    headers: Mapped[dict] = mapped_column(JSON, nullable=False)
    plain_text: Mapped[str] = mapped_column(Text, nullable=False, default="")
    html_body: Mapped[str] = mapped_column(Text, nullable=False, default="")
    attachment_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    evidence_map: Mapped[dict] = mapped_column(JSON, nullable=False)
    parsed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# M3 Header & Protocol Models
class AuthenticationResult(Base):
    __tablename__ = "authentication_results"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("messages.id", ondelete="RESTRICT"), nullable=False, unique=True)
    spf: Mapped[str] = mapped_column(String(16), nullable=False)
    dkim: Mapped[str] = mapped_column(String(16), nullable=False)
    dmarc: Mapped[str] = mapped_column(String(16), nullable=False)
    spf_aligned: Mapped[bool] = mapped_column(Boolean, default=False)
    dkim_aligned: Mapped[bool] = mapped_column(Boolean, default=False)
    arc_status: Mapped[str] = mapped_column(String(16), default="none")
    forwarding_detected: Mapped[bool] = mapped_column(Boolean, default=False)
    semantics_key: Mapped[str] = mapped_column(String(96), nullable=False)
    establishes: Mapped[str] = mapped_column(Text, nullable=False)
    does_not_establish: Mapped[str] = mapped_column(Text, nullable=False)
    investigation_effect: Mapped[str] = mapped_column(Text, nullable=False)
    evidence_reference_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("evidence_references.id", ondelete="RESTRICT"), nullable=False)


class DeliveryHop(Base):
    __tablename__ = "delivery_hops"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("messages.id", ondelete="RESTRICT"), nullable=False, index=True)
    hop_no: Mapped[int] = mapped_column(Integer, nullable=False)
    timestamp: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    claimed_host: Mapped[str | None] = mapped_column(Text)
    real_ip: Mapped[str | None] = mapped_column(Text)
    rdns: Mapped[str | None] = mapped_column(Text)
    tls_version: Mapped[str | None] = mapped_column(Text)
    delay_seconds: Mapped[float | None] = mapped_column(Float)
    trust_status: Mapped[str] = mapped_column(String(32), default="unverified")
    raw_header: Mapped[str] = mapped_column(Text, nullable=False)


# M4 Origin & Geolocation Models
class OriginEnrichment(Base):
    __tablename__ = "origin_enrichments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("messages.id", ondelete="RESTRICT"), nullable=False, unique=True)
    ip: Mapped[str] = mapped_column(Text, nullable=False)
    country: Mapped[str | None] = mapped_column(String(100))
    country_code: Mapped[str | None] = mapped_column(String(8))
    region: Mapped[str | None] = mapped_column(String(100))
    city: Mapped[str | None] = mapped_column(String(100))
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)
    accuracy_radius: Mapped[int | None] = mapped_column(Integer)
    asn: Mapped[int | None] = mapped_column(Integer)
    isp: Mapped[str | None] = mapped_column(Text)
    infra_type: Mapped[str] = mapped_column(String(32), default="unknown")
    confidence: Mapped[str] = mapped_column(String(20), default="Limited")
    caveat: Mapped[str] = mapped_column(Text, nullable=False)
    enriched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class DomainIntel(Base):
    __tablename__ = "domain_intel"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    domain: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    registrar: Mapped[str | None] = mapped_column(Text)
    creation_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    age_days: Mapped[int | None] = mapped_column(Integer)
    nameservers: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    mail_records: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    high_risk_flags: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    checked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# M9 Content & URL Engine Models
class UrlArtifact(Base):
    __tablename__ = "url_artifacts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("messages.id", ondelete="RESTRICT"), nullable=False, index=True)
    raw_url: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_url: Mapped[str] = mapped_column(Text, nullable=False)
    provenance: Mapped[str] = mapped_column(String(24), nullable=False, default="body")
    destination_host: Mapped[str | None] = mapped_column(Text)
    redirect_chain: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    anchor_text: Mapped[str | None] = mapped_column(Text)
    mismatch_flag: Mapped[bool] = mapped_column(Boolean, default=False)
    evidence_reference_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("evidence_references.id", ondelete="RESTRICT"), nullable=False)


class AttachmentArtifact(Base):
    __tablename__ = "attachment_artifacts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("messages.id", ondelete="RESTRICT"), nullable=False, index=True)
    filename: Mapped[str] = mapped_column(String(512), nullable=False)
    declared_mime: Mapped[str | None] = mapped_column(String(255))
    true_mime: Mapped[str | None] = mapped_column(String(255))
    byte_size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    static_indicators: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    evidence_reference_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("evidence_references.id", ondelete="RESTRICT"), nullable=False)


# M2 Detections & Findings
class Finding(Base):
    __tablename__ = "findings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("messages.id", ondelete="RESTRICT"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    category: Mapped[str] = mapped_column(String(64), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    contribution: Mapped[float] = mapped_column(Float, default=0)
    evidence_reference_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("evidence_references.id", ondelete="RESTRICT"), nullable=False)


class AnalysisRun(Base):
    __tablename__ = "analysis_runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("messages.id", ondelete="RESTRICT"), nullable=False, unique=True)
    evidence_reference_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("evidence_references.id", ondelete="RESTRICT"), nullable=False)
    result: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# M10 Evidence Conflicts (F1)
class EvidenceConflict(Base):
    __tablename__ = "evidence_conflicts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("messages.id", ondelete="RESTRICT"), nullable=False, index=True)
    conflict_type: Mapped[str] = mapped_column(String(64), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(String(20), default="Medium")
    evidence_ref_a_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("evidence_references.id", ondelete="RESTRICT"), nullable=False)
    evidence_ref_b_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("evidence_references.id", ondelete="RESTRICT"), nullable=False)
    detail: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# M11 Explainable Scoring (F8)
class ScoreExplanation(Base):
    __tablename__ = "score_explanations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("messages.id", ondelete="RESTRICT"), nullable=False, unique=True)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    verdict: Mapped[str] = mapped_column(String(20), nullable=False)
    confidence: Mapped[str] = mapped_column(String(20), nullable=False)
    contributions: Mapped[list] = mapped_column(JSON, nullable=False)
    disclaimer: Mapped[str] = mapped_column(Text, nullable=False)
    first_contact_suppressed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# M5 Correlation Graph, Campaign Memory (F6) & First-Contact Baseline (F4)
class GraphNode(Base):
    __tablename__ = "graph_nodes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    node_type: Mapped[str] = mapped_column(String(32), nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=False, unique=True, index=True)
    first_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    sighting_count: Mapped[int] = mapped_column(Integer, default=1)


class GraphEdge(Base):
    __tablename__ = "graph_edges"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    from_node: Mapped[uuid.UUID] = mapped_column(ForeignKey("graph_nodes.id", ondelete="RESTRICT"), nullable=False, index=True)
    to_node: Mapped[uuid.UUID] = mapped_column(ForeignKey("graph_nodes.id", ondelete="RESTRICT"), nullable=False, index=True)
    edge_type: Mapped[str] = mapped_column(String(32), nullable=False)
    weight: Mapped[float] = mapped_column(Float, default=1.0)
    evidence_reference_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("evidence_references.id", ondelete="RESTRICT"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class IndicatorHistory(Base):
    __tablename__ = "indicator_history"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    indicator_type: Mapped[str] = mapped_column(String(32), nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    first_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    sighting_count: Mapped[int] = mapped_column(Integer, default=1)
    distinct_cases: Mapped[int] = mapped_column(Integer, default=0)
    familiarity_band: Mapped[str] = mapped_column(String(20), default="Novel")


class StructuralFingerprint(Base):
    __tablename__ = "structural_fingerprints"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("messages.id", ondelete="RESTRICT"), nullable=False, unique=True)
    skeleton_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    raw_skeleton: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Campaign(Base):
    __tablename__ = "campaigns"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    shared_indicators: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    score: Mapped[float] = mapped_column(Float, default=0)
    status: Mapped[str] = mapped_column(String(24), default="Active")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class CampaignMessage(Base):
    __tablename__ = "campaign_messages"

    campaign_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("campaigns.id", ondelete="RESTRICT"), primary_key=True)
    message_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("messages.id", ondelete="RESTRICT"), primary_key=True)
    primary_evidence_ref_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("evidence_references.id", ondelete="RESTRICT"), nullable=False)


# M6 Cases & Workflow
class Case(Base):
    __tablename__ = "cases"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="Open")
    owner_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    notes: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class CaseMessage(Base):
    __tablename__ = "case_messages"

    case_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("cases.id", ondelete="RESTRICT"), primary_key=True)
    message_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("messages.id", ondelete="RESTRICT"), primary_key=True)


# M8 / M12 Platform Config & Model Registry
class PlatformConfig(Base):
    __tablename__ = "platform_config"

    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    value: Mapped[dict] = mapped_column(JSON, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class ModelRegistry(Base):
    __tablename__ = "model_registry"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    version: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    trained_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    calibrated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    metrics: Mapped[dict] = mapped_column(JSON, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    corpus_manifest: Mapped[dict] = mapped_column(JSON, nullable=False)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    target_type: Mapped[str] = mapped_column(String(64), nullable=False)
    target_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    details: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class RetentionPolicy(Base):
    __tablename__ = "retention_policies"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    data_class: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    retention_days: Mapped[int] = mapped_column(Integer, nullable=False)
    legal_hold_exempt: Mapped[bool] = mapped_column(Boolean, default=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class AlertRule(Base):
    __tablename__ = "alert_rules"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    score_threshold: Mapped[int] = mapped_column(Integer, default=75)
    destinations: Mapped[list] = mapped_column(JSON, nullable=False, default=lambda: ["console"])
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("messages.id", ondelete="RESTRICT"), nullable=False, index=True)
    rule_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("alert_rules.id", ondelete="SET NULL"))
    status: Mapped[str] = mapped_column(String(20), default="Fired")
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

