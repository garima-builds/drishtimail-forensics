"""Backend ML Model & Evaluation Verification Tests (M2 / M12).

Tests:
1. Model artifact loading from model.joblib.
2. Prediction on sample texts across all 6 threat classes.
3. Probability distribution validation (sum to ~1.0, non-negative).
4. Real held-out evaluation runner execution and metrics computation.
5. Graceful heuristic fallback when ML model artifact is unavailable.
"""
import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import Base, engine, SessionLocal
from app.detection.classifier import (
    classify_message_intent, get_trained_model, reset_model_cache, CLASSES
)
from app.evaluation.runner import run_model_evaluation, load_model_and_test_set
from app.evaluation.metrics import compute_multiclass_metrics


class TestMLEvaluation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)

    def setUp(self):
        self.db = SessionLocal()

    def tearDown(self):
        self.db.rollback()
        self.db.close()
        reset_model_cache()

    def test_01_model_artifact_loads(self):
        """Verify that model.joblib loads as a trained scikit-learn Pipeline."""
        model = get_trained_model()
        self.assertIsNotNone(model, "Trained model pipeline should not be None")
        self.assertTrue(hasattr(model, "predict"), "Model should implement predict()")
        self.assertTrue(hasattr(model, "predict_proba"), "Model should implement predict_proba()")

    def test_02_predict_across_classes(self):
        """Verify prediction produces one of the 6 valid classes with valid probabilities."""
        test_samples = [
            ("Microsoft 365 Account Suspension: Verify credentials at http://login-phish.com", "phishing"),
            ("Please wire $50,000 to vendor immediately for acquisition closing", "bec_fraud"),
            ("Scan attached invoice.zip and run the viewer", "malware_carrier"),
            ("Executive Directive from the Vice Chancellor to all faculty", "impersonation"),
            ("Claim your 70% discount on B2B email lists today", "spam"),
            ("Weekly engineering team meeting minutes and agenda notes", "benign"),
        ]

        for text, expected in test_samples:
            res = classify_message_intent(full_text=text)
            self.assertIn(res.predicted_class, CLASSES)
            self.assertEqual(res.engine_type, "trained_ml")
            self.assertIn(res.primary_threat_confidence, ["High", "Medium", "Low"])

            # Verify probabilities sum to ~1.0
            probs = res.probabilities
            prob_sum = sum(probs.values())
            self.assertAlmostEqual(prob_sum, 1.0, delta=0.01)
            for cls_name in CLASSES:
                self.assertIn(cls_name, probs)
                self.assertGreaterEqual(probs[cls_name], 0.0)

    def test_03_evaluation_runner_actual_predictions(self):
        """Verify that evaluation is executed against real held-out test split."""
        model, X_test, y_test, metadata = load_model_and_test_set()
        self.assertEqual(len(X_test), 100, "Held-out test set should have 100 samples")
        self.assertEqual(len(y_test), 100)

        result = run_model_evaluation(self.db, "drishtimail-nlp-v2.1")
        self.assertIn("metrics", result)
        metrics = result["metrics"]
        self.assertIn("accuracy", metrics)
        self.assertIn("macro_f1", metrics)
        self.assertIn("confusion_matrix", metrics)
        self.assertGreater(metrics["accuracy"], 0.80)
        self.assertGreater(metrics["macro_f1"], 0.80)

    def test_04_heuristic_fallback_when_model_missing(self):
        """Verify fallback to heuristic logit accumulator when model is unavailable."""
        # Test fallback with explicit indicators and no text
        res = classify_message_intent(
            full_text="",
            lookalike_findings=[{"domain": "micros0ft.com"}],
            auth_status="none",
        )
        self.assertEqual(res.engine_type, "heuristic_fallback")
        self.assertIn("Lookalike Domain Detected", res.top_contributing_signals)
        self.assertEqual(res.predicted_class, "phishing")


if __name__ == "__main__":
    unittest.main()
