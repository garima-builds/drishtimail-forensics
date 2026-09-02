"""F1 / M10: Evidence Conflict Rule Table.

Defines the 9 canonical conflict classes where two independent forensic evidence signals
contradict each other, specifying rule IDs, severities, base score adjustments, and
evaluation criteria.
"""
from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class ConflictRule:
    rule_id: str
    conflict_type: str
    severity: Literal["Low", "Medium", "High", "Critical"]
    title: str
    description: str
    base_score_adjustment: int
    category: str


class ConflictRuleTable:
    """Catalog of all canonical evidence conflict rules."""

    RULES: dict[str, ConflictRule] = {
        "C01": ConflictRule(
            rule_id="C01",
            conflict_type="authenticated_but_misaligned",
            severity="High",
            title="Authenticated but Misaligned Sender",
            description="Message holds a technical SPF or DKIM pass, but the envelope/signing domain does NOT align with the visible Header From domain.",
            base_score_adjustment=15,
            category="protocol_identity",
        ),
        "C02": ConflictRule(
            rule_id="C02",
            conflict_type="reply_path_divergence",
            severity="High",
            title="Reply-Path Header Divergence",
            description="Visible From header points to one entity while Reply-To routes responses to a different, unrelated domain.",
            base_score_adjustment=20,
            category="header_routing",
        ),
        "C03": ConflictRule(
            rule_id="C03",
            conflict_type="auth_pass_vs_content_risk",
            severity="Critical",
            title="Cryptographic Pass with High Content Threat",
            description="Sender authentication fully passes, yet independent NLP intent analysis identifies high-risk fraud or credential phishing cues. Strong indicator of a compromised sender account or authorized MTA relay abuse.",
            base_score_adjustment=25,
            category="account_compromise",
        ),
        "C04": ConflictRule(
            rule_id="C04",
            conflict_type="auth_fail_vs_benign_content",
            severity="Low",
            title="Authentication Failure with Benign Content (Forwarding Artifact)",
            description="Sender authentication failed due to forwarding/mailing list intermediate hops, but content analysis reveals zero hostile payloads or pressure cues.",
            base_score_adjustment=-10,
            category="transit_artifact",
        ),
        "C05": ConflictRule(
            rule_id="C05",
            conflict_type="display_text_vs_destination_host",
            severity="Critical",
            title="Visible Anchor vs Destination Host Mismatch",
            description="Hyperlink anchor text explicitly displays a trusted brand or URL, but the href attribute routes to an external destination host.",
            base_score_adjustment=25,
            category="deceptive_content",
        ),
        "C06": ConflictRule(
            rule_id="C06",
            conflict_type="qr_destination_vs_body_divergence",
            severity="High",
            title="QR Code Payload vs Body Text Divergence",
            description="Email body text contains no suspicious links or mentions, while an attached or inline QR code embeds an unlinked external URL.",
            base_score_adjustment=20,
            category="quishing_evasion",
        ),
        "C07": ConflictRule(
            rule_id="C07",
            conflict_type="geography_vs_claimed_entity",
            severity="Medium",
            title="Origin Geography vs Claimed Sender Entity",
            description="Message claims domestic institutional origin, but earliest reliable relay hop resolves to an offshore datacenter or anonymizing proxy.",
            base_score_adjustment=15,
            category="infrastructure_anomaly",
        ),
        "C08": ConflictRule(
            rule_id="C08",
            conflict_type="header_timestamp_vs_relay_timing",
            severity="Medium",
            title="Relay Clock Anomaly / Negative Transit Latency",
            description="Recorded timestamps in Received headers show negative or physically impossible transit intervals, suggesting clock skew or forged headers.",
            base_score_adjustment=10,
            category="temporal_inconsistency",
        ),
        "C09": ConflictRule(
            rule_id="C09",
            conflict_type="feed_reputation_vs_baseline",
            severity="Low",
            title="External Feed Flag on Established Local Sender",
            description="An external reputation feed flagged an indicator, but local institutional history demonstrates a long, familiar, clean baseline.",
            base_score_adjustment=-5,
            category="reputation_attenuation",
        ),
    }

    @classmethod
    def get_by_id(cls, rule_id: str) -> ConflictRule | None:
        return cls.RULES.get(rule_id.upper())

    @classmethod
    def get_by_type(cls, conflict_type: str) -> ConflictRule | None:
        for rule in cls.RULES.values():
            if rule.conflict_type == conflict_type:
                return rule
        return None

    @classmethod
    def all_rules(cls) -> list[ConflictRule]:
        return list(cls.RULES.values())
