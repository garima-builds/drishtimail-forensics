"""F2 / M12: Corpus Manifest & Limitations Disclosure.

Defines evaluation datasets and explicitly discloses sample distribution,
random split parameters, and synthetic/curated benchmark limitations.
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
    "corpus_id": "curated_eval_500",
    "name": "Curated 500-Sample Forensic Intent Benchmark",
    "total_samples": 500,
    "train_samples": 400,
    "test_samples": 100,
    "random_seed": 42,
    "model_type": "TF-IDF (max 2500 n-grams) + Calibrated LinearSVC",
    "class_distribution": {
        "phishing": 150,
        "bec_fraud": 100,
        "malware_carrier": 80,
        "impersonation": 70,
        "spam": 50,
        "benign": 50,
    },
    "languages": ["English", "Hindi (transliterated keywords)"],
    "explicit_limitations": (
        "This evaluation set is derived from a curated benchmark dataset of 500 forensic threat samples "
        "(150 phishing, 100 BEC, 80 malware carrier, 70 impersonation, 50 spam, 50 benign). "
        "IMPORTANT DISCLOSURE: It does NOT claim to represent private enterprise mailflows or proprietary internal traffic. "
        "Public and synthetic text patterns may carry vocabulary biases. High-risk actions must always be reviewed by a human analyst."
    ),
}
