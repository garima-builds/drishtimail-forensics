"""Unified End-to-End Forensic Investigation Pipeline.

Coordinates Ingestion (M1), Detection (M2), Protocol Analysis & Semantics (M3 / F5),
Origin Traceability (M4), Graph Correlation & First-Contact (M5 / F6 / F4),
Embedded Content & Quishing (M9 / F3), Evidence Conflicts (M10 / F1),
Explainable Scoring (M11 / F8), and Evidence Ledger Integrity (M7 / F7).
"""
import uuid
from uuid import UUID
from datetime import datetime, timezone
from typing import Any
from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import (
    AnalysisRun, AuthenticationResult, DeliveryHop, DomainIntel, EvidenceConflict,
    EvidenceReference, Finding, Message, MimePart, OriginEnrichment, ParsedMessage,
    PlatformConfig, ScoreExplanation, StructuralFingerprint, UrlArtifact, AttachmentArtifact
)
from .evidence import add_reference, append_ledger
from .protocol.relay_parser import parse_relay_chain
from .protocol.trust_boundary import resolve_trust_boundary
from .protocol.auth_validator import validate_email_authentication
from .protocol.auth_semantics import evaluate_auth_semantics
from .protocol.header_anomalies import detect_header_anomalies
from .content.url_extractor import extract_all_urls
from .content.qr_decoder import scan_email_mime_parts_for_qr
from .content.display_comparator import compare_display_vs_destination
from .content.redirect_expander import expand_redirect_chain
from .content.attachment_analyzer import analyze_attachment_static
from .detection.feature_extractor import run_detection_pipeline
from .origin.geo_resolver import resolve_ip_geolocation
from .origin.domain_intel import evaluate_domain_risk
from .correlation.fingerprinter import extract_structural_skeleton
from .correlation.ioc_extractor import extract_all_iocs
from .correlation.first_contact import check_and_update_indicator_history
from .correlation.graph_service import link_message_indicators
from .correlation.origin_scenario import classify_origin_scenario
from .conflicts.rule_engine import evaluate_evidence_conflicts
from .scoring.normalizer import normalize_all_signals
from .scoring.weighted_scorer import compute_explainable_score


def _sanitize_for_json(obj: Any) -> Any:
    if isinstance(obj, UUID):
        return str(obj)
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif hasattr(obj, "__dataclass_fields__"):
        return {k: _sanitize_for_json(getattr(obj, k)) for k in obj.__dataclass_fields__}
    elif isinstance(obj, dict):
        return {str(k): _sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple, set)):
        return [_sanitize_for_json(item) for item in obj]
    return obj


def execute_forensic_pipeline(
    db: Session,
    message_id: uuid.UUID,
) -> dict[str, Any]:
    """Execute complete multi-module forensic analysis on an ingested message."""
    message = db.get(Message, message_id)
    parsed = db.scalar(select(ParsedMessage).where(ParsedMessage.message_id == message_id))

    if not message or not parsed:
        raise ValueError(f"Message {message_id} not found or unparsed")

    # Fetch configuration lists
    trusted_mtas_cfg = db.get(PlatformConfig, "trusted_mtas")
    trusted_hosts = trusted_mtas_cfg.value.get("hosts", []) if trusted_mtas_cfg else []
    trusted_subnets = trusted_mtas_cfg.value.get("subnets", []) if trusted_mtas_cfg else []

    vip_cfg = db.get(PlatformConfig, "protected_identities")
    vips = vip_cfg.value.get("values", []) if vip_cfg else []

    inst_domains_cfg = db.get(PlatformConfig, "institutional_domains")
    inst_domains = inst_domains_cfg.value.get("domains", []) if inst_domains_cfg else []

    mime_parts = db.scalars(select(MimePart).where(MimePart.message_id == message_id)).all()

    # Step 1: Parse Relay Chain & Trust Boundary (M3)
    raw_hops = parse_relay_chain(parsed.headers)
    annotated_hops, earliest_reliable = resolve_trust_boundary(
        raw_hops,
        trusted_mta_hosts=trusted_hosts,
        trusted_mta_subnets=trusted_subnets,
    )
    anomalies = detect_header_anomalies(parsed.headers, annotated_hops)

    # Step 2: Validate Sender Authentication & Semantics (M3 / F5)
    auth_val = validate_email_authentication(parsed.headers, sender_header=message.sender)
    sender_domain = auth_val.from_domain or ""

    # Check if sender domain is lookalike
    is_lookalike = (
        "micros0ft" in sender_domain
        or "0ffice" in sender_domain
        or (any(b in sender_domain and not sender_domain.endswith(f"{b}.com") for b in ["microsoft", "google", "paypal", "university"]))
    )

    auth_semantics = evaluate_auth_semantics(
        spf=auth_val.spf,
        dkim=auth_val.dkim,
        dmarc=auth_val.dmarc,
        spf_aligned=auth_val.spf_aligned,
        dkim_aligned=auth_val.dkim_aligned,
        forwarding_detected=auth_val.forwarding_detected,
        is_lookalike_domain=is_lookalike,
    )

    # Step 3: Quishing & QR Code Extraction (M9 / F3)
    qr_detections = scan_email_mime_parts_for_qr(mime_parts)
    qr_urls = [(q.payload, q.provenance) for q in qr_detections if q.payload]

    # Step 4: URL Extraction & Display Comparison (M9)
    extracted_urls = extract_all_urls(
        plain_text=parsed.plain_text,
        html_body=parsed.html_body,
        qr_urls=qr_urls,
    )

    url_artifacts_data: list[dict[str, Any]] = []
    for u in extracted_urls:
        mismatch = compare_display_vs_destination(u.anchor_text, u.destination_host)
        redirects = expand_redirect_chain(u.normalized_url, enabled=False)  # Safe offline default
        url_artifacts_data.append({
            "raw_url": u.raw_url,
            "normalized_url": u.normalized_url,
            "provenance": u.provenance,
            "destination_host": u.destination_host,
            "redirect_chain": redirects,
            "anchor_text": u.anchor_text,
            "mismatch_flag": mismatch.get("mismatch", False),
        })

    # Step 5: Static Attachment Analysis (M9)
    attachment_artifacts_data: list[dict[str, Any]] = []
    for part in mime_parts:
        if part.filename:
            # We already have payload or part record
            res = analyze_attachment_static(
                filename=part.filename,
                declared_mime=part.content_type,
                payload_bytes=b"",  # Static check on metadata
            )
            attachment_artifacts_data.append(res)

    # Step 6: Multi-Feature Detection Engine (M2)
    detections = run_detection_pipeline(
        sender=message.sender,
        subject=message.subject,
        headers=parsed.headers,
        plain_text=parsed.plain_text,
        html_body=parsed.html_body,
        url_artifacts=url_artifacts_data,
        attachment_artifacts=attachment_artifacts_data,
        auth_status=auth_val.dmarc,
        has_qr_threat=bool(qr_urls),
        protected_identities=vips,
        protected_domains=inst_domains,
    )

    # Step 7: Origin Geolocation & Domain Intel (M4)
    origin_ip = earliest_reliable.get("candidate_ip")
    geo_info = resolve_ip_geolocation(origin_ip)
    domain_risk = evaluate_domain_risk(sender_domain)

    # Step 8: Structural HTML Fingerprinting (M5 / F6)
    skel_hash, raw_skel = extract_structural_skeleton(parsed.html_body)

    # Step 9: First-Contact History Lookup (M5 / F4)
    first_contact = check_and_update_indicator_history(
        db=db,
        indicator_type="domain",
        value=sender_domain,
        is_active_case=False,
    )

    # ================= GRANULAR EVIDENCE REFERENCES =================
    body_offsets = parsed.evidence_map.get("body", [0, 0])
    auth_offsets = parsed.evidence_map.get("authentication-results", parsed.evidence_map.get("received-spf", [0, 0]))
    from_offsets = parsed.evidence_map.get("from", [0, 0])
    reply_to_offsets = parsed.evidence_map.get("reply-to", from_offsets)
    received_offsets = parsed.evidence_map.get("received", [0, 0])

    analysis_ref = add_reference(
        db,
        evidence_object_id=parsed.evidence_object_id,
        byte_start=body_offsets[0],
        byte_end=body_offsets[1],
        description="Full forensic pipeline multi-module analysis source",
    )
    auth_ref = add_reference(
        db,
        evidence_object_id=parsed.evidence_object_id,
        byte_start=auth_offsets[0],
        byte_end=auth_offsets[1],
        header_name="Authentication-Results",
        description="Sender authentication validation source",
    )
    from_ref = add_reference(
        db,
        evidence_object_id=parsed.evidence_object_id,
        byte_start=from_offsets[0],
        byte_end=from_offsets[1],
        header_name="From",
        description="Sender identity header source",
    )
    reply_to_ref = add_reference(
        db,
        evidence_object_id=parsed.evidence_object_id,
        byte_start=reply_to_offsets[0],
        byte_end=reply_to_offsets[1],
        header_name="Reply-To",
        description="Reply destination header source",
    )
    received_ref = add_reference(
        db,
        evidence_object_id=parsed.evidence_object_id,
        byte_start=received_offsets[0],
        byte_end=received_offsets[1],
        header_name="Received",
        description="Relay transit headers source",
    )

    evidence_refs_map = {
        "primary": analysis_ref.id,
        "auth": auth_ref.id,
        "from": from_ref.id,
        "reply_to": reply_to_ref.id,
        "received": received_ref.id,
        "body": analysis_ref.id,
    }

    # Step 10: Evidence Conflict Evaluation (M10 / F1)
    conflicts = evaluate_evidence_conflicts(
        auth_results={
            "spf": auth_val.spf, "dkim": auth_val.dkim, "dmarc": auth_val.dmarc,
            "spf_aligned": auth_val.spf_aligned, "dkim_aligned": auth_val.dkim_aligned,
            "forwarding_detected": auth_val.forwarding_detected,
        },
        anomalies=anomalies,
        detections=detections,
        url_artifacts=url_artifacts_data,
        qr_results=[{"payload": q.payload, "undecodable": q.undecodable} for q in qr_detections],
        origin_info=geo_info,
        indicator_history=first_contact,
        evidence_refs=evidence_refs_map,
    )

    # Step 11: Explainable Threat Scoring (M11 / F8)
    normalized_signals = normalize_all_signals(
        auth_results={
            "spf": auth_val.spf, "dkim": auth_val.dkim, "dmarc": auth_val.dmarc,
            "spf_aligned": auth_val.spf_aligned, "dkim_aligned": auth_val.dkim_aligned,
        },
        anomalies=anomalies,
        detections=detections,
        url_artifacts=url_artifacts_data,
        qr_results=[{"payload": q.payload, "undecodable": q.undecodable} for q in qr_detections],
        attachment_artifacts=attachment_artifacts_data,
        conflicts=conflicts,
        origin_info=geo_info,
        first_contact_info=first_contact,
        evidence_refs=evidence_refs_map,
    )

    scored_verdict = compute_explainable_score(
        signals=normalized_signals,
        conflicts=conflicts,
    )

    # Step 12: Formulate Origin Scenario Hypothesis (M5)
    scenario_info = classify_origin_scenario(
        auth_results={"dmarc": auth_val.dmarc, "spf": auth_val.spf, "forwarding_detected": auth_val.forwarding_detected},
        detections=detections,
        conflicts=conflicts,
        url_artifacts=url_artifacts_data,
        qr_results=[{"payload": q.payload} for q in qr_detections],
    )

    # Step 13: Extract all IOCs & Link to Property Graph (M5 / F6)
    iocs = extract_all_iocs(
        sender=message.sender,
        headers=parsed.headers,
        origin_ip=origin_ip,
        relay_hops=annotated_hops,
        urls=url_artifacts_data,
        attachments=attachment_artifacts_data,
        structural_hash=skel_hash,
    )

    # Update Message fields
    message.score = scored_verdict.score
    message.verdict = scored_verdict.verdict
    message.confidence = scored_verdict.confidence
    message.summary = f"{scenario_info['scenario']}: {scenario_info['hypothesis']}"

    # Persist Authentication Result
    auth_record = db.scalar(select(AuthenticationResult).where(AuthenticationResult.message_id == message_id))
    if not auth_record:
        auth_record = AuthenticationResult(
            message_id=message_id,
            spf=auth_val.spf,
            dkim=auth_val.dkim,
            dmarc=auth_val.dmarc,
            spf_aligned=auth_val.spf_aligned,
            dkim_aligned=auth_val.dkim_aligned,
            arc_status=auth_val.arc_status,
            forwarding_detected=auth_val.forwarding_detected,
            semantics_key=auth_semantics.semantics_key,
            establishes=auth_semantics.establishes,
            does_not_establish=auth_semantics.does_not_establish,
            investigation_effect=auth_semantics.investigation_effect,
            evidence_reference_id=auth_ref.id,
        )
        db.add(auth_record)

    # Persist Delivery Hops
    for hop in annotated_hops:
        db.add(DeliveryHop(
            message_id=message_id,
            hop_no=hop["hop_no"],
            claimed_host=hop.get("claimed_host"),
            real_ip=hop.get("real_ip"),
            rdns=hop.get("rdns"),
            tls_version=hop.get("tls_version"),
            delay_seconds=hop.get("delay_seconds"),
            trust_status=hop.get("trust_status", "unverified"),
            raw_header=hop.get("raw_header", ""),
        ))

    # Persist Origin Enrichment
    db.add(OriginEnrichment(
        message_id=message_id,
        ip=geo_info["ip"],
        country=geo_info.get("country"),
        country_code=geo_info.get("country_code"),
        region=geo_info.get("region"),
        city=geo_info.get("city"),
        latitude=geo_info.get("latitude"),
        longitude=geo_info.get("longitude"),
        accuracy_radius=geo_info.get("accuracy_radius"),
        asn=geo_info.get("asn"),
        isp=geo_info.get("isp"),
        infra_type=geo_info.get("infra_type", "unknown"),
        confidence=geo_info.get("confidence", "Limited"),
        caveat=geo_info.get("caveat", ""),
    ))

    # Persist Structural Fingerprint
    db.add(StructuralFingerprint(
        message_id=message_id,
        skeleton_hash=skel_hash,
        raw_skeleton=raw_skel,
    ))

    # Persist URLs
    for u_data in url_artifacts_data:
        db.add(UrlArtifact(
            message_id=message_id,
            raw_url=u_data["raw_url"],
            normalized_url=u_data["normalized_url"],
            provenance=u_data["provenance"],
            destination_host=u_data.get("destination_host"),
            redirect_chain=u_data.get("redirect_chain", []),
            anchor_text=u_data.get("anchor_text"),
            mismatch_flag=u_data.get("mismatch_flag", False),
            evidence_reference_id=analysis_ref.id,
        ))

    # Persist Evidence Conflicts
    for c_data in conflicts:
        db.add(EvidenceConflict(
            message_id=message_id,
            conflict_type=c_data["conflict_type"],
            summary=c_data["summary"],
            severity=c_data["severity"],
            evidence_ref_a_id=c_data.get("evidence_ref_a_id") or analysis_ref.id,
            evidence_ref_b_id=c_data.get("evidence_ref_b_id") or analysis_ref.id,
            detail=_sanitize_for_json(c_data),
        ))

    # Persist Score Explanation
    db.add(ScoreExplanation(
        message_id=message_id,
        score=scored_verdict.score,
        verdict=scored_verdict.verdict,
        confidence=scored_verdict.confidence,
        contributions=_sanitize_for_json(scored_verdict.contributions),
        disclaimer=scored_verdict.disclaimer,
        first_contact_suppressed=scored_verdict.first_contact_suppressed,
    ))

    # Link into Correlation Graph
    link_message_indicators(
        db=db,
        message_id=message_id,
        indicators=[{"indicator_type": i.indicator_type, "value": i.value} for i in iocs],
        evidence_reference_id=analysis_ref.id,
    )

    # Build result dictionary
    result_dict = {
        "analysed_at": datetime.now(timezone.utc).isoformat(),
        "score": {
            "value": scored_verdict.score,
            "verdict": scored_verdict.verdict,
            "confidence": scored_verdict.confidence,
            "contributions": scored_verdict.contributions,
            "disclaimer": scored_verdict.disclaimer,
            "first_contact_suppressed": scored_verdict.first_contact_suppressed,
            "suppression_reason": scored_verdict.suppression_reason,
        },
        "authentication": {
            "spf": auth_val.spf,
            "dkim": auth_val.dkim,
            "dmarc": auth_val.dmarc,
            "spf_aligned": auth_val.spf_aligned,
            "dkim_aligned": auth_val.dkim_aligned,
            "arc_status": auth_val.arc_status,
            "forwarding_detected": auth_val.forwarding_detected,
            "semantics_key": auth_semantics.semantics_key,
            "establishes": auth_semantics.establishes,
            "does_not_establish": auth_semantics.does_not_establish,
            "investigation_effect": auth_semantics.investigation_effect,
            "is_lookalike_authenticated": auth_semantics.is_lookalike_authenticated,
        },
        "delivery_path": annotated_hops,
        "origin": {
            **geo_info,
            "candidate_ip": origin_ip,
            "hop_no": earliest_reliable.get("hop_no"),
            "justification": earliest_reliable.get("justification"),
        },
        "domain_intel": domain_risk,
        "detections": detections,
        "urls": url_artifacts_data,
        "qr_results": [
            {
                "payload": q.payload,
                "provenance": q.provenance,
                "rotation": q.rotation_degrees,
                "undecodable": q.undecodable,
                "bounding_box": q.bounding_box,
            }
            for q in qr_detections
        ],
        "conflicts": conflicts,
        "scenario": scenario_info,
        "first_contact": first_contact,
        "structural_fingerprint": {"hash": skel_hash},
        "indicators": [
            {"indicator_type": i.indicator_type, "value": i.value, "provenance": i.provenance}
            for i in iocs
        ],
    }

    # Persist AnalysisRun & Ledger Entry
    existing_run = db.scalar(select(AnalysisRun).where(AnalysisRun.message_id == message_id))
    if existing_run:
        existing_run.result = _sanitize_for_json(result_dict)
        existing_run.evidence_reference_id = analysis_ref.id
    else:
        db.add(AnalysisRun(
            message_id=message_id,
            evidence_reference_id=analysis_ref.id,
            result=_sanitize_for_json(result_dict),
        ))

    append_ledger(
        db,
        event_type="analysis.completed",
        subject_id=message_id,
        evidence_reference_id=analysis_ref.id,
        payload={
            "score": scored_verdict.score,
            "verdict": scored_verdict.verdict,
            "conflict_count": len(conflicts),
            "scenario": scenario_info["scenario"],
            "structural_hash": skel_hash,
        },
    )

    db.commit()
    return _sanitize_for_json(result_dict)
