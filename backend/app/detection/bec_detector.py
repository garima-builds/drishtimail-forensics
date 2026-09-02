"""M2: Business Email Compromise (BEC) & Fraud Pattern Detector.

Identifies specific institutional fraud patterns: bank detail diversion, fake invoices,
payroll redirection, and executive gift-card requests.
"""
import re
from typing import Any

BEC_PATTERNS = {
    "bank_account_update": {
        "title": "BEC: Bank Account Detail Diversion",
        "severity": "Critical",
        "patterns": [
            r"\b(?:updated|new|changed)\s+(?:banking|bank account|remittance|wire|payment)\s+(?:details|information|instructions|details for payment)\b",
            r"\b(?:kindly note our new bank|update our banking details on your system|account change notice)\b",
            r"\b(?:beneficiary name|iban|swift|routing number|sort code)\s*:\s*[A-Z0-9]{4,}\b",
        ],
        "description": "Message instructs recipient to update stored banking details or divert an impending invoice payment.",
    },
    "fake_invoice": {
        "title": "BEC: Urgent / Unverified Invoice Payment",
        "severity": "High",
        "patterns": [
            r"\b(?:overdue invoice|outstanding payment|invoice attached|remittance advice|settle the balance)\b",
            r"\b(?:payment confirmation|pending invoice #?[0-9a-z\-]+|proof of payment)\b",
            r"\b(?:process the attached invoice|approved for payment)\b",
        ],
        "description": "Message demands immediate payment on an invoice or asks to verify an attached payment request.",
    },
    "payroll_diversion": {
        "title": "BEC: Direct Deposit / Payroll Diversion",
        "severity": "Critical",
        "patterns": [
            r"\b(?:update my direct deposit|change my payroll account|new bank account for my salary|direct deposit information)\b",
            r"\b(?:can i change my direct deposit before the next pay cycle|hr payroll change)\b",
        ],
        "description": "Message impersonates an employee requesting HR/finance to redirect direct-deposit salary to a new account.",
    },
    "gift_card_scam": {
        "title": "BEC: Executive Gift Card Solicitation",
        "severity": "High",
        "patterns": [
            r"\b(?:gift cards?|google play|apple store|itunes|steam card|amazon gift|ebay card)\b.*?\b(?:scratch the back|send the codes?|need you to purchase|buy for me)\b",
            r"\b(?:i am in a meeting|cannot take calls|need a quick favour|purchase \d+ cards)\b",
        ],
        "description": "Message mimics leadership asking a subordinate to urgently buy retail gift cards under the pretext of being in a meeting.",
    },
}


def detect_bec_patterns(text: str) -> list[dict[str, Any]]:
    """Scan text for explicit BEC and wire fraud patterns."""
    if not text:
        return []

    lowered = text.lower()
    matches: list[dict[str, Any]] = []

    for key, spec in BEC_PATTERNS.items():
        found = False
        matched_text = []
        for pat in spec["patterns"]:
            match = re.search(pat, lowered, re.IGNORECASE)
            if match:
                found = True
                matched_text.append(match.group(0))

        if found:
            matches.append({
                "pattern_type": key,
                "title": spec["title"],
                "severity": spec["severity"],
                "matched_snippets": matched_text,
                "description": spec["description"],
            })

    return matches
