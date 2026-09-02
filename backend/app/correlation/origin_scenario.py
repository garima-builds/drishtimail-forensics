"""M5: Investigative Origin Scenario Classifier.

Synthesizes multi-module findings to classify the most probable attack delivery mechanism
into clear, confidence-scored forensic hypotheses.
"""
from typing import Any


def classify_origin_scenario(
    *,
    auth_results: dict[str, Any],
    detections: dict[str, Any],
    conflicts: list[dict[str, Any]],
    url_artifacts: list[dict[str, Any]],
    qr_results: list[dict[str, Any]],
) -> dict[str, Any]:
    """Determine the most probable forensic delivery scenario."""
    dmarc = auth_results.get("dmarc", "none")
    forwarding = auth_results.get("forwarding_detected", False)
    has_lookalike = bool(detections.get("lookalike_domains"))
    has_imp = bool(detections.get("impersonation"))
    has_bec = bool(detections.get("bec_patterns"))
    has_qr = any(q.get("payload") for q in qr_results)
    conflict_types = {c.get("conflict_type") for c in conflicts}

    # Scenario 1: Deceptive Lookalike Domain
    if has_lookalike:
        return {
            "scenario": "Deceptive Lookalike Domain Infrastructure",
            "confidence": "High",
            "hypothesis": (
                "The adversary registered or operated a visually similar domain name (typosquat or homoglyph substitution) "
                "to deceive recipients into mistaking the sender for an official brand or institutional entity."
            ),
            "investigative_leads": [
                "Inspect domain registration WHOIS creation date and nameservers.",
                "Search campaign graph for other phishing templates sharing this lookalike host.",
                "Review passive DNS resolution history for IP infrastructure reuse.",
            ],
        }

    # Scenario 2: Compromised Legitimate Account
    if "auth_pass_vs_content_risk" in conflict_types or (dmarc == "pass" and (has_bec or has_imp or has_qr)):
        return {
            "scenario": "Compromised Legitimate Account / Infrastructure Abuse",
            "confidence": "High",
            "hypothesis": (
                "The email originated from genuine, authenticated domain infrastructure, but contains hostile social engineering, "
                "fraud instructions, or disguised links. This pattern strongly indicates unauthorized mailbox compromise or trusted MTA relay abuse."
            ),
            "investigative_leads": [
                "Notify sender domain administrators of potential account compromise / credential leakage.",
                "Correlate earliest reliable origin IP against normal user geographic login baselines.",
                "Inspect message for thread hijacking and mailbox rule manipulation.",
            ],
        }

    # Scenario 3: QR Code / Quishing Evasion
    if has_qr:
        return {
            "scenario": "Quishing / Image-Embedded Payload Evasion",
            "confidence": "High",
            "hypothesis": (
                "The adversary deliberately avoided placing hyperlinks in the email body text to evade text-based URL filters, "
                "instead embedding the credential harvesting destination inside an image or document QR code."
            ),
            "investigative_leads": [
                "Trace decoded QR destination URL through unshorteners and registrar databases.",
                "Check whether QR template matches known shared campaign fingerprints.",
            ],
        }

    # Scenario 4: Direct Sender Address Spoofing
    if dmarc == "fail" or (auth_results.get("spf") in {"fail", "softfail"} and not forwarding):
        return {
            "scenario": "Direct Header Sender Spoofing",
            "confidence": "Medium",
            "hypothesis": (
                "The adversary injected the claimed sender identity into the Header From line without cryptographic authorization. "
                "The receiving border MTA correctly identified SPF/DMARC policy violations."
            ),
            "investigative_leads": [
                "Trace the earliest reliable origin IP in the Received headers to identify the sending MTA provider.",
                "Check for Reply-To header diversion.",
            ],
        }

    # Scenario 5: Forwarded / Mailing List Transit
    if forwarding:
        return {
            "scenario": "Forwarded Message / Mailing List Intermediary",
            "confidence": "Moderate",
            "hypothesis": (
                "The message traversed intermediary forwarding or list servers, causing standard SPF / alignment breaks. "
                "Evaluate DKIM and ARC signatures to assess original sender authenticity."
            ),
            "investigative_leads": [
                "Inspect ARC-Seal and ARC-Authentication-Results headers.",
                "Identify the hop immediately preceding the forwarding MTA.",
            ],
        }

    # Default Scenario: Unattributed External Email
    return {
        "scenario": "Standard External Email Transit",
        "confidence": "Limited",
        "hypothesis": "Message represents standard external correspondence with no strong adversarial deception signatures.",
        "investigative_leads": [
            "Monitor sender domain history for future campaign clustering.",
        ],
    }
