"""F2 / M12: Evaluation Metrics Calculator.

Computes precision, recall, F1 score, and confusion matrix per class.
"""
from typing import Any


def compute_multiclass_metrics(
    y_true: list[str],
    y_pred: list[str],
    classes: list[str],
) -> dict[str, Any]:
    """Compute per-class and macro precision, recall, and F1."""
    confusion_matrix: dict[str, dict[str, int]] = {c: {c2: 0 for c2 in classes} for c in classes}

    for t, p in zip(y_true, y_pred):
        if t in confusion_matrix and p in confusion_matrix[t]:
            confusion_matrix[t][p] += 1

    per_class_metrics: dict[str, dict[str, float]] = {}
    f1_sum = 0.0
    prec_sum = 0.0
    rec_sum = 0.0

    for c in classes:
        tp = confusion_matrix[c][c]
        fp = sum(confusion_matrix[other][c] for other in classes if other != c)
        fn = sum(confusion_matrix[c][other] for other in classes if other != c)

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        per_class_metrics[c] = {
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
            "support": sum(confusion_matrix[c].values()),
        }
        f1_sum += f1
        prec_sum += precision
        rec_sum += recall

    n = len(classes) if classes else 1
    macro_f1 = round(f1_sum / n, 4)
    macro_precision = round(prec_sum / n, 4)
    macro_recall = round(rec_sum / n, 4)
    accuracy = round(sum(1 for t, p in zip(y_true, y_pred) if t == p) / len(y_true), 4) if y_true else 0.0

    return {
        "accuracy": accuracy,
        "macro_f1": macro_f1,
        "macro_precision": macro_precision,
        "macro_recall": macro_recall,
        "per_class": per_class_metrics,
        "confusion_matrix": confusion_matrix,
    }
