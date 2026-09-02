"""F2 / M12: Corpus Manifest & Limitations Disclosure.

Defines evaluation datasets and explicitly discloses what public corpora do and do not cover,
ensuring transparency about era, encoding, and institutional traffic biases.
"""
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CorpusMetadata:
    corpus_id: str
    name: str
    source_url: str
    sample_count: int
    languages_covered: list[str]
    explicit_limitations: str


DEFAULT_CORPUS_MANIFEST = {
    "corpus_id": "public_eval_v1",
    "name": "Held-Out Public Phishing & Benign Validation Corpus",
    "total_samples": 500,
    "class_distribution": {
        "phishing": 150,
        "bec_fraud": 100,
        "malware_carrier": 80,
        "impersonation": 70,
        "spam": 50,
        "benign": 50,
    },
    "languages": ["English", "Hindi (limited)"],
    "explicit_limitations": (
        "This evaluation set is derived from held-out public phishing collections (Nazario, Enron subset, APWG samples). "
        "IMPORTANT LIMITATION: It does NOT contain real internal institutional correspondence or proprietary enterprise mailflows. "
        "Performance on local institutional traffic may vary; public corpora carry historical era and header-encoding biases."
    ),
}
