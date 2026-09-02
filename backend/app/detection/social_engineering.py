"""M2: Social Engineering & Intent Pressure Detector.

Identifies psychological manipulation cues: urgency, authority, secrecy, financial actions,
and threats of negative consequence.
"""
import re
from typing import Any

INTENT_CATEGORIES = {
    "urgency": [
        r"\b(?:urgent|immediately|action required|within 24 hours|expires today|account suspended|final notice|immediate response)\b",
        r"\b(?:act now|time sensitive|deadline|do not delay|restricted within|asap)\b",
    ],
    "authority": [
        r"\b(?:office of the|director|registrar|head of department|ceo|cfo|executive|provost|dean|management|it support|security team)\b",
        r"\b(?:administrative order|compliance mandate|official notice|authorized personnel)\b",
    ],
    "secrecy": [
        r"\b(?:keep this confidential|strictly confidential|do not discuss|private matter|between us|do not disclose|discreetly)\b",
        r"\b(?:sensitive transaction|private assignment|confidential project)\b",
    ],
    "financial_instruction": [
        r"\b(?:wire transfer|bank details|new account details|swift code|remittance|invoice payment|change of bank|process payment)\b",
        r"\b(?:gift cards?|itunes card|google play card|steam card|reimburse|purchase cards)\b",
    ],
    "threat_of_consequence": [
        r"\b(?:disciplinary action|terminated|account termination|legal action|access revoked|suspended permanently|penalties)\b",
        r"\b(?:will be locked|lose access|service cancellation)\b",
    ],
}


def detect_social_engineering(text: str) -> list[dict[str, Any]]:
    """Scan text for social engineering intent cues across categories."""
    if not text:
        return []

    lowered = text.lower()
    findings: list[dict[str, Any]] = []

    for category, patterns in INTENT_CATEGORIES.items():
        matched_cues: list[str] = []
        for pat in patterns:
            for match in re.finditer(pat, lowered):
                matched_cues.append(match.group(0))

        if matched_cues:
            unique_cues = list(dict.fromkeys(matched_cues))
            findings.append({
                "category": category,
                "title": f"Social Engineering: {category.replace('_', ' ').title()}",
                "cues": unique_cues,
                "count": len(unique_cues),
                "severity": "High" if category in {"financial_instruction", "threat_of_consequence"} else "Medium",
                "summary": f"Detected {len(unique_cues)} {category.replace('_', ' ')} cue(s): {', '.join(unique_cues[:4])}",
            })

    return findings
