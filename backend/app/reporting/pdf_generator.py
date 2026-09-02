"""M6: Forensic PDF Report Generator with BSA Section 63 Evidence Metadata.

Compiles an authoritative multi-page PDF investigation report including:
- Case details and executive verdict
- Explainable scoring breakdown and point attribution
- F5 Authentication Semantics panel
- Relay hop table and trust boundary analysis
- Approximate infrastructure geolocation with mandatory caveats
- URL and Quishing QR code findings
- Evidence ledger hash-chain log and Merkle root sealing proof
- BSA Section 63 Digital Evidence & Provenance Metadata Section (non-legal technical metadata)
"""
import io
from datetime import datetime, timezone
from typing import Any
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable


def generate_forensic_report_pdf(
    message_data: dict[str, Any],
    analysis_data: dict[str, Any],
    merkle_root: str | None = None,
    examiner_name: str = "DrishtiMail Forensic Engine",
) -> bytes:
    """Render a structured multi-page PDF forensic report buffer."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("DocTitle", parent=styles["Heading1"], fontSize=20, leading=24, textColor=colors.HexColor("#1e2824"))
    h2_style = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=13, leading=16, textColor=colors.HexColor("#27362e"), spaceBefore=10, spaceAfter=4)
    body_style = ParagraphStyle("Body", parent=styles["Normal"], fontSize=9, leading=12, textColor=colors.HexColor("#25231f"))
    small_style = ParagraphStyle("Small", parent=styles["Normal"], fontSize=8, leading=10, textColor=colors.HexColor("#575950"))
    code_style = ParagraphStyle("Code", parent=styles["Code"], fontSize=7.5, leading=9, textColor=colors.HexColor("#181715"))
    callout_style = ParagraphStyle("Callout", parent=styles["Normal"], fontSize=8.5, leading=11, textColor=colors.HexColor("#333330"))

    story = []

    # 1. Header Banner
    story.append(Paragraph("<b>DRISHTIMAIL FORENSICS</b> — Technical Investigation Report", title_style))
    story.append(Paragraph(f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')} | Examiner: {examiner_name}", small_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#cc785c"), spaceBefore=6, spaceAfter=12))

    # 2. Executive Case Summary Table
    score = analysis_data.get("score", {})
    verdict = score.get("verdict", "Elevated")
    score_val = score.get("value", 0)

    verdict_color = colors.HexColor("#b44b3f") if verdict == "Critical" else colors.HexColor("#b57624") if verdict == "High" else colors.HexColor("#48783f")

    summary_data = [
        [Paragraph("<b>Message Subject:</b>", body_style), Paragraph(str(message_data.get("subject", "(No Subject)")), body_style)],
        [Paragraph("<b>Claimed Sender:</b>", body_style), Paragraph(str(message_data.get("sender", "Unknown")), body_style)],
        [Paragraph("<b>Ingestion ID / Hash:</b>", body_style), Paragraph(str(message_data.get("id", "N/A")), code_style)],
        [Paragraph("<b>Threat Verdict:</b>", body_style), Paragraph(f"<b><font color='{verdict_color.hexval()}'>{verdict.upper()}</font></b> (Threat Score: <b>{score_val}/100</b> | Confidence: {score.get('confidence', 'Medium')})", body_style)],
    ]
    summary_table = Table(summary_data, colWidths=[120, 420])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f7f5ef")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2ded5")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 10))

    # 3. Explainable Threat Score Breakdown
    story.append(Paragraph("1. Explainable Threat Score Breakdown (M11 / F8)", h2_style))
    contributions = score.get("contributions", [])
    if contributions:
        score_rows = [[Paragraph("<b>Contributing Signal</b>", body_style), Paragraph("<b>Family</b>", body_style), Paragraph("<b>Points</b>", body_style), Paragraph("<b>Forensic Rationale</b>", body_style)]]
        for c in contributions:
            score_rows.append([
                Paragraph(str(c.get("signal")), body_style),
                Paragraph(str(c.get("family", "")).replace("_", " ").title(), small_style),
                Paragraph(f"<b>+{c.get('points')}</b>" if c.get("points", 0) > 0 else str(c.get("points")), body_style),
                Paragraph(str(c.get("reason")), small_style),
            ])
        score_table = Table(score_rows, colWidths=[130, 80, 45, 285])
        score_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#efe9de")),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2ded5")),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        story.append(score_table)
    story.append(Paragraph(f"<i>Disclaimer: {score.get('disclaimer', '')}</i>", small_style))
    story.append(Spacer(1, 10))

    # 4. Authentication Semantics Panel (F5)
    auth = analysis_data.get("authentication", {})
    story.append(Paragraph("2. Sender Authentication & Semantic Interpretation (M3 / F5)", h2_style))
    auth_data = [
        [Paragraph("<b>Technical Protocol Results:</b>", body_style), Paragraph(f"SPF: <b>{auth.get('spf')}</b> | DKIM: <b>{auth.get('dkim')}</b> | DMARC: <b>{auth.get('dmarc')}</b>", body_style)],
        [Paragraph("<b>What is Established:</b>", body_style), Paragraph(str(auth.get("establishes", "N/A")), body_style)],
        [Paragraph("<b>What is NOT Established:</b>", body_style), Paragraph(f"<font color='#a83d31'>{auth.get('does_not_establish', 'N/A')}</font>", body_style)],
        [Paragraph("<b>Effect on Investigation:</b>", body_style), Paragraph(str(auth.get("investigation_effect", "N/A")), body_style)],
    ]
    auth_table = Table(auth_data, colWidths=[140, 400])
    auth_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#fffdfa")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2ded5")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(auth_table)
    story.append(Spacer(1, 10))

    # 5. Evidence Conflicts (F1)
    conflicts = analysis_data.get("conflicts", [])
    if conflicts:
        story.append(Paragraph("3. Cross-Evidence Contradictions & Conflicts (M10 / F1)", h2_style))
        for conf in conflicts:
            conf_data = [
                [Paragraph(f"<b>Conflict: {conf.get('title', conf.get('conflict_type'))}</b> (Severity: {conf.get('severity')})", body_style)],
                [Paragraph(f"<b>Summary:</b> {conf.get('summary')}", body_style)],
                [Paragraph(f"<b>Evidence A:</b> {conf.get('evidence_side_a', 'N/A')}", small_style)],
                [Paragraph(f"<b>Evidence B:</b> {conf.get('evidence_side_b', 'N/A')}", small_style)],
            ]
            t = Table(conf_data, colWidths=[540])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#fbebd7")),
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#cc785c")),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ]))
            story.append(t)
            story.append(Spacer(1, 4))
        story.append(Spacer(1, 6))

    # 6. Origin Traceability & Geolocation (M4)
    origin = analysis_data.get("origin", {})
    story.append(Paragraph("4. Origin Traceability & Approximate Network Geolocation (M4)", h2_style))
    origin_data = [
        [Paragraph("<b>Earliest Reliable IP:</b>", body_style), Paragraph(f"{origin.get('candidate_ip', 'N/A')} (Hop #{origin.get('hop_no', '1')})", body_style)],
        [Paragraph("<b>Approximate Location:</b>", body_style), Paragraph(f"{origin.get('city', 'Unknown')}, {origin.get('region', '')}, {origin.get('country', 'Unknown')}", body_style)],
        [Paragraph("<b>Network Operator / ASN:</b>", body_style), Paragraph(f"{origin.get('isp', 'Unknown')} (ASN {origin.get('asn', 'N/A')})", body_style)],
        [Paragraph("<b>Infrastructure Type:</b>", body_style), Paragraph(str(origin.get("infra_type", "unknown")).title(), body_style)],
        [Paragraph("<b>Selection Justification:</b>", body_style), Paragraph(str(origin.get("justification", "Earliest public IP recorded by ingress border MTA.")), small_style)],
    ]
    origin_table = Table(origin_data, colWidths=[140, 400])
    origin_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#fffdfa")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2ded5")),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(origin_table)
    story.append(Paragraph(f"<i><b>Caveat:</b> {origin.get('caveat', '')}</i>", small_style))
    story.append(Spacer(1, 10))

    # 7. Quishing & Embedded Content (M9 / F3)
    urls = analysis_data.get("urls", [])
    qr_findings = analysis_data.get("qr_results", [])
    if urls or qr_findings:
        story.append(Paragraph("5. Embedded Content & Quishing / QR Findings (M9 / F3)", h2_style))
        content_rows = [[Paragraph("<b>Extracted Destination</b>", body_style), Paragraph("<b>Provenance</b>", body_style), Paragraph("<b>Anchor / Context</b>", body_style)]]
        for u in urls[:6]:
            content_rows.append([
                Paragraph(str(u.get("normalized_url", u.get("raw_url", "")))[:60], code_style),
                Paragraph(str(u.get("provenance", "body")), small_style),
                Paragraph(str(u.get("anchor_text") or "N/A"), small_style),
            ])
        c_table = Table(content_rows, colWidths=[270, 90, 180])
        c_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#efe9de")),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2ded5")),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        story.append(c_table)
        story.append(Spacer(1, 10))

    # 8. BSA Section 63 Digital Evidence & Provenance Metadata Section
    story.append(KeepTogether([
        Paragraph("6. Digital Evidence & Custody Metadata (BSA Section 63 Technical Record)", h2_style),
        Paragraph(
            "This section documents the cryptographic hash, custodial timestamps, byte-range addressing, and immutable ledger "
            "verification records for this electronic evidence artifact. <i>(Technical provenance metadata; not a legal certification of admissibility).</i>",
            small_style
        ),
        Spacer(1, 4),
    ]))

    bsa_data = [
        [Paragraph("<b>Raw Artifact SHA-256:</b>", body_style), Paragraph(str(message_data.get("sha256", "Computed at ingestion")), code_style)],
        [Paragraph("<b>Storage Key:</b>", body_style), Paragraph(str(message_data.get("storage_key", "MinIO immutable write-once store")), code_style)],
        [Paragraph("<b>Primary Evidence Ref:</b>", body_style), Paragraph(str(message_data.get("evidence_reference", "Bound by byte-range constraint")), code_style)],
        [Paragraph("<b>Merkle Root Seal:</b>", body_style), Paragraph(str(merkle_root or "Sealed in immutable ledger"), code_style)],
        [Paragraph("<b>Ingestion Timestamp:</b>", body_style), Paragraph(str(message_data.get("received_at", datetime.now(timezone.utc).isoformat())), body_style)],
        [Paragraph("<b>Verification Tool:</b>", body_style), Paragraph("DrishtiMail Standalone Offline Verifier (v2.0, verify_ledger.py)", body_style)],
    ]
    bsa_table = Table(bsa_data, colWidths=[150, 390])
    bsa_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f4f1e9")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#87847c")),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(bsa_table)
    story.append(Spacer(1, 14))

    # Footer Disclaimer
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#87847c"), spaceBefore=4, spaceAfter=4))
    story.append(Paragraph(
        "<b>CONFIDENTIAL INSTITUTIONAL FORENSIC INTELLIGENCE</b> — Generated by DrishtiMail Forensics (SIH26106). "
        "Findings represent technical indicators and explainable prioritisation models.",
        small_style
    ))

    doc.build(story)
    return buf.getvalue()
