"""Train Calibrated NLP Threat Classifier (M2 / M12).

Trains a scikit-learn TF-IDF + Calibrated Linear Classifier on the curated 500-sample corpus.
Evaluates model on an 80/20 held-out test split (400 train, 100 test, random_state=42, stratify=y).
Saves fitted model artifact to model.joblib and split metadata to split_metadata.json.
"""
import csv
import json
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.pipeline import Pipeline

CLASSES = ["phishing", "bec_fraud", "malware_carrier", "impersonation", "spam", "benign"]


def load_corpus() -> tuple[list[str], list[str]]:
    csv_path = os.path.join(os.path.dirname(__file__), "corpus_500.csv")
    texts = []
    labels = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            texts.append(row["text"])
            labels.append(row["label"])
    return texts, labels


def compute_metrics(y_true: list[str], y_pred: list[str], classes: list[str]) -> dict:
    confusion = {c: {c2: 0 for c2 in classes} for c in classes}
    for t, p in zip(y_true, y_pred):
        if t in confusion and p in confusion[t]:
            confusion[t][p] += 1

    per_class = {}
    f1_sum = 0.0
    prec_sum = 0.0
    rec_sum = 0.0

    for c in classes:
        tp = confusion[c][c]
        fp = sum(confusion[other][c] for other in classes if other != c)
        fn = sum(confusion[c][other] for other in classes if other != c)

        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0

        per_class[c] = {
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1": round(f1, 4),
            "support": sum(confusion[c].values()),
        }
        f1_sum += f1
        prec_sum += prec
        rec_sum += rec

    n = len(classes)
    acc = sum(1 for t, p in zip(y_true, y_pred) if t == p) / len(y_true) if y_true else 0.0

    return {
        "accuracy": round(acc, 4),
        "macro_f1": round(f1_sum / n, 4),
        "macro_precision": round(prec_sum / n, 4),
        "macro_recall": round(rec_sum / n, 4),
        "per_class": per_class,
        "confusion_matrix": confusion,
    }


def train_and_save():
    texts, labels = load_corpus()
    print(f"Loaded {len(texts)} samples across {len(set(labels))} classes.")

    # 80/20 Stratified Train/Test Split
    X_train, X_test, y_train, y_test = train_test_split(
        texts,
        labels,
        test_size=0.20,
        random_state=42,
        stratify=labels,
    )
    print(f"Split: {len(X_train)} Train samples, {len(X_test)} Test samples (random_state=42).")

    # Build Pipeline: TF-IDF + Calibrated Linear Classifier
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            max_features=2500,
            ngram_range=(1, 2),
            sublinear_tf=True,
            stop_words="english",
        )),
        ("clf", CalibratedClassifierCV(
            estimator=LinearSVC(dual="auto", random_state=42, C=1.0),
            cv=3,
        )),
    ])

    print("Fitting model pipeline...")
    pipeline.fit(X_train, y_train)

    # Evaluate on held-out test split
    y_pred = pipeline.predict(X_test)
    metrics = compute_metrics(y_test, list(y_pred), CLASSES)

    print("\n--- Model Evaluation Results on Held-Out Test Split (100 samples) ---")
    print(f"Accuracy: {metrics['accuracy'] * 100:.2f}%")
    print(f"Macro F1: {metrics['macro_f1'] * 100:.2f}%")
    print(f"Macro Precision: {metrics['macro_precision'] * 100:.2f}%")
    print(f"Macro Recall: {metrics['macro_recall'] * 100:.2f}%")

    # Save Model Artifact
    model_path = os.path.join(os.path.dirname(__file__), "model.joblib")
    joblib.dump(pipeline, model_path)
    print(f"\nSaved model artifact to: {model_path} ({os.path.getsize(model_path)} bytes)")

    # Save Held-Out Test Split & Metadata for Reproducible Evaluation
    meta_path = os.path.join(os.path.dirname(__file__), "split_metadata.json")
    test_data = [{"text": t, "label": l} for t, l in zip(X_test, y_test)]
    metadata = {
        "model_version": "drishtimail-nlp-v2.1",
        "model_type": "TF-IDF (max 2500 n-grams) + Calibrated LinearSVC",
        "corpus_id": "curated_eval_500",
        "corpus_name": "Curated 500-Sample Forensic Intent Benchmark",
        "total_samples": len(texts),
        "train_samples": len(X_train),
        "test_samples_count": len(X_test),
        "random_seed": 42,
        "class_distribution": {c: labels.count(c) for c in CLASSES},
        "held_out_test_set": test_data,
        "metrics": metrics,
        "explicit_limitations": (
            "This model is trained on a curated benchmark dataset of 500 forensic threat samples "
            "(150 phishing, 100 BEC, 80 malware carrier, 70 impersonation, 50 spam, 50 benign). "
            "It does NOT claim to represent private enterprise mailflows. Public and synthetic text "
            "patterns may carry vocabulary biases. High-risk actions must always be reviewed by a human analyst."
        ),
    }

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    print(f"Saved test split & metadata to: {meta_path}")

    return metrics


if __name__ == "__main__":
    train_and_save()
