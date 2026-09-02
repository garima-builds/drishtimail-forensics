import React from 'react';
import { Message } from '../types';
import { api } from '../api';

interface ReportsViewProps {
  messages: Message[];
  onSelectMessage: (id: string) => void;
}

export const ReportsView: React.FC<ReportsViewProps> = ({ messages, onSelectMessage }) => {
  return (
    <div className="view-container">
      <div className="card">
        <div className="card-header">
          <div>
            <h3>Forensic Investigation Reports & BSA Section 63 Metadata Hub (M6)</h3>
            <p className="card-desc">
              Generate, preview, and download formal technical investigation dossiers documenting cryptographic hash chains, evidence provenance, protocol validation, and triage verdicts.
            </p>
          </div>
          <span className="badge-info">{messages.length} Available Report(s)</span>
        </div>
        <div className="alert-box info mt-2">
          <strong>Notice on BSA Section 63 Metadata:</strong>
          <div>
            Reports contain an evidence/report metadata section documenting cryptographic integrity, SHA-256 provenance hashes, and tool verification status as an objective forensic record.
          </div>
        </div>
      </div>

      <div className="card mt-4">
        <div className="card-header">
          <h4>Generated Preserved Evidence Reports</h4>
        </div>

        {messages.length === 0 ? (
          <div className="empty-card-state">
            <p>No messages available to generate reports. Please ingest evidence first.</p>
          </div>
        ) : (
          <div className="table-responsive">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Verdict</th>
                  <th>Threat Score</th>
                  <th>Sender</th>
                  <th>Subject</th>
                  <th>Preserved Evidence Reference</th>
                  <th>Report Downloads</th>
                </tr>
              </thead>
              <tbody>
                {messages.map((msg) => (
                  <tr key={msg.id}>
                    <td>
                      <span className={`verdict-pill ${msg.verdict === 'Critical' ? 'verdict-critical' : msg.verdict === 'High' ? 'verdict-high' : msg.verdict === 'Elevated' ? 'verdict-elevated' : 'verdict-low'}`}>
                        {msg.verdict}
                      </span>
                    </td>
                    <td>
                      <strong>{msg.score}/100</strong>
                    </td>
                    <td className="font-mono text-xs">{msg.sender}</td>
                    <td className="subject-cell">{msg.subject}</td>
                    <td>
                      <code className="code-pill text-xs">{msg.evidence_reference ? `${msg.evidence_reference.slice(0, 18)}...` : 'N/A'}</code>
                    </td>
                    <td>
                      <div className="action-buttons">
                        <a
                          href={api.getReportPdfUrl(msg.id)}
                          target="_blank"
                          rel="noreferrer"
                          className="btn btn-sm btn-primary"
                          title="Download Official PDF Report (BSA §63)"
                        >
                          📄 PDF Report
                        </a>
                        <a
                          href={api.getReportHtmlUrl(msg.id)}
                          target="_blank"
                          rel="noreferrer"
                          className="btn btn-sm btn-secondary"
                          title="Open HTML Report View"
                        >
                          🌐 HTML View
                        </a>
                        <button
                          className="btn btn-sm btn-outline"
                          onClick={() => onSelectMessage(msg.id)}
                          title="Open Deep Dive Workspace"
                        >
                          🔬 Inspect
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
