"""F2 / M12: ML Model Validation Runner.

Evaluates the actual trained scikit-learn model artifact against the held-out test partition,
computes true multi-class metrics (accuracy, macro F1, confusion matrix), and logs the run
to the PostgreSQL ModelRegistry.
"""
import json
import os
from datetime import datetime, timezone
from typing import Any
import joblib
from sqlalchemy import select
from sqlalchemy.orm import Session
from .manifest import DEFAULT_CORPUS_MANIFEST
from .metrics import compute_multiclass_metrics
from ..models import ModelRegistry
from ..detection.train_classifier import train_and_save, CLASSES


def load_model_and_test_set():
    """Load trained pipeline and held-out test partition."""
    detection_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "detection"))
    model_path = os.path.join(detection_dir, "model.joblib")
    meta_path = os.path.join(detection_dir, "split_metadata.json")

    # If model or metadata is missing, train and generate it
    if not os.path.exists(model_path) or not os.path.exists(meta_path):
        train_and_save()

    model = joblib.load(model_path)
    with open(meta_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    test_set = metadata.get("held_out_test_set", [])
    X_test = [item["text"] for item in test_set]
    y_test = [item["label"] for item in test_set]

    return model, X_test, y_test, metadata


def run_model_evaluation(
    db: Session,
    model_version: str = "drishtimail-nlp-v2.1",
) -> dict[str, Any]:
    """Execute evaluation against actual held-out test partition and log to ModelRegistry."""
    model, X_test, y_test, metadata = load_model_and_test_set()

    # Run real model predictions on held-out test samples
    y_pred = list(model.predict(X_test))
    metrics = compute_multiclass_metrics(y_test, y_pred, CLASSES)

    manifest = dict(DEFAULT_CORPUS_MANIFEST)
    manifest["test_samples_count"] = len(X_test)
    manifest["model_type"] = metadata.get("model_type", "TF-IDF + Calibrated LinearSVC")
    manifest["random_seed"] = metadata.get("random_seed", 42)

    now_dt = datetime.now(timezone.utc)

    registry_entry = db.scalar(select(ModelRegistry).where(ModelRegistry.version == model_version))
    if not registry_entry:
        registry_entry = ModelRegistry(
            version=model_version,
            trained_at=now_dt,
            calibrated_at=now_dt,
            metrics=metrics,
            is_active=True,
            corpus_manifest=manifest,
        )
        db.add(registry_entry)
    else:
        registry_entry.calibrated_at = now_dt
        registry_entry.metrics = metrics
        registry_entry.corpus_manifest = manifest
        registry_entry.is_active = True

    db.commit()
    db.refresh(registry_entry)

    return registry_entry
