import React, { useEffect, useState } from 'react';
import { ModelRegistryItem } from '../types';
import { api } from '../api';

export const ModelEvaluationView: React.FC = () => {
  const [models, setModels] = useState<ModelRegistryItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [evaluating, setEvaluating] = useState<boolean>(false);
  const [selectedModel, setSelectedModel] = useState<ModelRegistryItem | null>(null);

  useEffect(() => {
    loadRegistry();
  }, []);

  const loadRegistry = async () => {
    setLoading(true);
    try {
      const data = await api.getModelRegistry();
      setModels(data);
      if (data.length > 0) setSelectedModel(data[0]);
    } catch (err) {
      console.error('Failed to load model registry:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRunEvaluation = async () => {
    setEvaluating(true);
    try {
      const result = await api.runModelEvaluation();
      setSelectedModel(result);
      await loadRegistry();
      alert('ML model validation benchmark completed successfully!');
    } catch (err: any) {
      alert(`Model evaluation failed: ${err.message}`);
    } finally {
      setEvaluating(false);
    }
  };

  return (
    <div className="view-container">
      <div className="card">
        <div className="card-header">
          <div>
            <h3>Machine Learning Model Registry & Validation (M12 / Feature F2)</h3>
            <p className="card-desc">
              Transparent multi-class performance evaluation, per-class F1 breakdown, confusion matrices, and explicit corpus limitations disclosures.
            </p>
          </div>
          <button
            className="btn btn-primary"
            onClick={handleRunEvaluation}
            disabled={evaluating}
          >
            {evaluating ? '🔄 Running Benchmark...' : '▶ Run Evaluation Benchmark'}
          </button>
        </div>
      </div>

      {loading ? (
        <div className="spinner mt-4"></div>
      ) : !selectedModel ? (
        <div className="empty-card-state mt-4">
          <p>No model registry entries found.</p>
        </div>
      ) : (
        <div className="investigation-grid mt-4">
          {/* Left Column: Overall Metrics & Per-Class Breakdown */}
          <div className="card">
            <div className="card-header">
              <div>
                <h4>{selectedModel.model_name}</h4>
                <span className="text-muted text-xs">Version: {selectedModel.version} • Evaluated: {new Date(selectedModel.trained_at).toLocaleDateString()}</span>
              </div>
              <span className="badge-primary">Active Ingest Classifier</span>
            </div>

            {/* Top Stat Meters */}
            <div className="metric-cards-grid two-col mt-3">
              <div className="metric-card">
                <span className="metric-label">Macro F1 Score</span>
                <span className="metric-value">{(selectedModel.macro_f1 * 100).toFixed(1)}%</span>
                <span className="metric-sub">Multi-Class Balanced Metric</span>
              </div>
              <div className="metric-card">
                <span className="metric-label">Overall Accuracy</span>
                <span className="metric-value">{(selectedModel.accuracy * 100).toFixed(1)}%</span>
                <span className="metric-sub">Held-Out Test Partition</span>
              </div>
            </div>

            {/* Per-Class Metrics Table */}
            <h4 className="section-subtitle mt-4">Per-Class Precision, Recall & F1</h4>
            <div className="table-responsive">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Threat Class</th>
                    <th>Precision</th>
                    <th>Recall</th>
                    <th>F1-Score</th>
                    <th>Support</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(selectedModel.per_class_metrics).map(([clsName, metrics]) => (
                    <tr key={clsName}>
                      <td><strong>{clsName}</strong></td>
                      <td>{(metrics.precision * 100).toFixed(1)}%</td>
                      <td>{(metrics.recall * 100).toFixed(1)}%</td>
                      <td>
                        <span className="font-bold text-accent">
                          {(metrics.f1 * 100).toFixed(1)}%
                        </span>
                      </td>
                      <td className="text-muted">{metrics.support}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Right Column: Confusion Matrix & Disclosures */}
          <div className="card">
            <div className="card-header">
              <h4>Multi-Class Confusion Matrix</h4>
              <span className="badge-outline">Actual vs Predicted</span>
            </div>

            <div className="matrix-table-wrapper">
              <table className="matrix-table">
                <thead>
                  <tr>
                    <th className="matrix-header-corner">Actual \ Pred</th>
                    {Object.keys(selectedModel.confusion_matrix).map((k) => (
                      <th key={k} className="matrix-col-header">{k.slice(0, 4)}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(selectedModel.confusion_matrix).map(([actual, row]) => (
                    <tr key={actual}>
                      <td className="matrix-row-header"><strong>{actual}</strong></td>
                      {Object.entries(row).map(([pred, count]) => {
                        const isDiagonal = actual === pred;
                        return (
                          <td
                            key={pred}
                            className={`matrix-cell ${isDiagonal ? 'cell-diagonal' : count > 0 ? 'cell-misclassified' : 'cell-zero'}`}
                          >
                            {count}
                          </td>
                        );
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Corpus Limitations Disclosure */}
            <div className="limitations-box mt-4">
              <h4>⚠️ Corpus Limitations & Boundary Conditions</h4>
              <ul className="limitations-list">
                {selectedModel.limitations_disclosure.map((disc, idx) => (
                  <li key={idx}>{disc}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
