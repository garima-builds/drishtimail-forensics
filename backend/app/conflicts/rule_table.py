"""F1 / M10: Evidence Conflict Rule Definitions.

Declares the 9 canonical conflict classes where two independent pieces of forensic
evidence contradict each other, requiring cross-evidence reconciliation.
"""
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ConflictRule:
    rule_id: str
    conflict_type: str
    severity: str
    title: str
    description: str


CONFLICT_RULES = [
    ConflictRule(
        rule_id="C01",
        conflict_type="authenticated_but_misaligned",
        severity="High",
        title="Authenticated but Misaligned Sender",
        description="Message holds a technical SPF or DKIM pass, but the envelope/signing domain does NOT align with the visible Header From domain.",
    ),
    ConflictRule(
        rule_id="C02",
        conflict_type="reply_path_divergence",
        severity="High",
        title="Reply-Path Header Divergence",
        description="Visible From header points to one entity while Reply-To routes responses to a different, unrelated domain.",
    ),
    ConflictRule(
        rule_id="C03",
        conflict_type="auth_pass_vs_content_risk",
        severity="Critical",
        title="Cryptographic Pass with High Content Threat",
        description="Sender authentication fully passes, yet independent NLP intent analysis identifies high-risk fraud or credential phishing cues. Strong indicator of a compromised sender account.",
    ),
    ConflictRule(
        rule_id="C04",
        conflict_type="auth_fail_vs_benign_content",
        severity="Low",
        title="Authentication Failure with Benign Content (Forwarding)",
        description="Sender authentication failed due to forwarding/mailing list hops, but content analysis reveals zero hostile payloads or pressure cues.",
    ),
    ConflictRule(
        rule_id="C05",
        conflict_type="display_text_vs_destination_host",
        severity="Critical",
        title="Visible Anchor vs Destination Host Mismatch",
        description="Hyperlink anchor text explicitly displays a trusted brand or URL, but the href attribute routes to an external destination host.",
    ),
    ConflictRule(
        rule_id="C06",
        conflict_type="qr_destination_vs_body_divergence",
        severity="High",
        title="QR Code Payload vs Body Text Divergence",
        description="Email body text contains no suspicious links or mentions, while an attached or inline QR code embeds an unlinked external URL.",
    ),
    ConflictRule(
        rule_id="C07",
        conflict_type="geography_vs_claimed_entity",
        severity="Medium",
        title="Origin Geography vs Claimed Sender Entity",
        description="Message claims domestic institutional origin, but earliest reliable relay hop resolves to an offshore datacenter or anonymizing proxy.",
    ),
    ConflictRule(
        rule_id="C08",
        conflict_type="header_timestamp_vs_relay_timing",
        severity="Medium",
        title="Relay Clock Anomaly / Negative Transit Latency",
        description="Recorded timestamps in Received headers show negative or physically impossible transit intervals, suggesting clock skew or forged headers.",
    ),
    ConflictRule(
        rule_id="C09",
        conflict_type="feed_reputation_vs_baseline",
        severity="Low",
        title="External Feed Flag on Established Local Sender",
        description="An external reputation feed flagged an indicator, but local institutional history demonstrates a long, familiar, clean baseline.",
    ),
]
