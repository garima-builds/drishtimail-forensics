"""M7: PII Masking & Non-Custodial Privacy Sanitizer.

Masks sensitive personal data (Aadhaar, PAN, SSN, Credit Cards, IBAN/Bank accounts, Phone numbers)
when generating non-custodial views or sanitized analyst extracts.
"""
import re


AADHAAR_PATTERN = re.compile(r"\b([2-9]\d{3})\s?(\d{4})\s?(\d{4})\b")
PAN_PATTERN = re.compile(r"\b([A-Z]{5})(\d{4})([A-Z])\b", re.IGNORECASE)
CREDIT_CARD_PATTERN = re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b")
PHONE_PATTERN = re.compile(r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b")
IBAN_PATTERN = re.compile(r"\b[A-Z]{2}\d{2}[A-Z0-9]{11,30}\b", re.IGNORECASE)


def mask_aadhaar(match: re.Match) -> str:
    last4 = match.group(3)
    return f"XXXX-XXXX-{last4}"


def mask_pan(match: re.Match) -> str:
    pan = match.group(0)
    return f"{pan[:2]}XXXXX{pan[-2:]}"


def mask_credit_card(match: re.Match) -> str:
    digits = re.sub(r"\D", "", match.group(0))
    if len(digits) == 16:
        return f"{digits[:4]}-XXXX-XXXX-{digits[-4:]}"
    return "XXXX-XXXX-XXXX-XXXX"


def mask_phone(match: re.Match) -> str:
    phone = match.group(0)
    digits = re.sub(r"\D", "", phone)
    if len(digits) >= 10:
        return f"+XX-XXXXX-{digits[-4:]}"
    return "XXX-XXX-XXXX"


def mask_iban(match: re.Match) -> str:
    iban = match.group(0)
    return f"{iban[:4]}XXXX{iban[-4:]}"


def mask_pii_for_display(text: str | None) -> str:
    """Mask high-sensitivity PII tokens in text for non-custodial display."""
    if not text:
        return ""

    sanitized = text
    sanitized = AADHAAR_PATTERN.sub(mask_aadhaar, sanitized)
    sanitized = PAN_PATTERN.sub(mask_pan, sanitized)
    sanitized = CREDIT_CARD_PATTERN.sub(mask_credit_card, sanitized)
    sanitized = IBAN_PATTERN.sub(mask_iban, sanitized)
    sanitized = PHONE_PATTERN.sub(mask_phone, sanitized)

    return sanitized
