import React, { useState } from 'react';
import { Message, DashboardSummary } from '../types';
import { api } from '../api';

interface QueueDashboardProps {
  summary: DashboardSummary | null;
  messages: Message[];
  loading: boolean;
  onSelectMessage: (id: string) => void;
  onOpenIngest: () => void;
  onRefresh: () => void;
}

export const QueueDashboard: React.FC<QueueDashboardProps> = ({
  summary,
  messages,
  loading,
  onSelectMessage,
  onOpenIngest,
  onRefresh,
}) => {
  const [filterVerdict, setFilterVerdict] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');

  const filteredMessages = messages.filter((m) => {
    const matchesFilter =
      filterVerdict === 'all'
        ? true
        : filterVerdict === 'new'
        ? m.status === 'New'
        : m.verdict.toLowerCase() === filterVerdict.toLowerCase();

    const matchesSearch =
      m.sender.toLowerCase().includes(searchQuery.toLowerCase()) ||
      m.subject.toLowerCase().includes(searchQuery.toLowerCase()) ||
      m.summary.toLowerCase().includes(searchQuery.toLowerCase());

    return matchesFilter && matchesSearch;
  });

  const getVerdictBadgeClass = (verdict: string) => {
    switch (verdict) {
      case 'Critical': return 'badge-critical';
      case 'High': return 'badge-high';
      case 'Elevated': return 'badge-elevated';
      default: return 'badge-low';
    }
  };

  return (
    <div className="view-container">
      {/* Metric Cards Banner */}
      <div className="metric-cards-grid">
        <div className="metric-card">
          <div className="metric-header">
            <span className="metric-label">Total Preserved Messages</span>
            <span className="metric-icon">📥</span>
          </div>
          <div className="metric-value">{summary ? summary.total_messages : messages.length}</div>
          <div className="metric-sub">RFC 5322 Preserved Artifacts</div>
        </div>

        <div className="metric-card critical">
          <div className="metric-header">
            <span className="metric-label">Critical Threat</span>
            <span className="metric-icon">🚨</span>
          </div>
          <div className="metric-value">{summary ? summary.critical : messages.filter(m => m.verdict === 'Critical').length}</div>
          <div className="metric-sub">Score ≥ 75 & Hard Threat Cues</div>
        </div>

        <div className="metric-card high">
          <div className="metric-header">
            <span className="metric-label">High Priority</span>
            <span className="metric-icon">⚠️</span>
          </div>
          <div className="metric-value">{summary ? summary.high : messages.filter(m => m.verdict === 'High').length}</div>
          <div className="metric-sub">Score 55 - 74 (High Confidence)</div>
        </div>

        <div className="metric-card elevated">
          <div className="metric-header">
            <span className="metric-label">Elevated / Suspect</span>
            <span className="metric-icon">🔍</span>
          </div>
          <div className="metric-value">{summary ? summary.elevated : messages.filter(m => m.verdict === 'Elevated').length}</div>
          <div className="metric-sub">Score 30 - 54 (Requires Review)</div>
        </div>

        <div className="metric-card neutral">
          <div className="metric-header">
            <span className="metric-label">Active Cases / Clusters</span>
            <span className="metric-icon">📁</span>
          </div>
          <div className="metric-value">{summary ? `${summary.total_cases} / ${summary.active_campaigns}` : '-'}</div>
          <div className="metric-sub">Correlation Clusters Linked</div>
        </div>
      </div>

      {/* Queue Toolbar & Filters */}
      <div className="queue-panel">
        <div className="queue-toolbar">
          <div className="search-box">
            <span className="search-icon">🔍</span>
            <input
              type="text"
              placeholder="Search by sender, subject, or indicator..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="search-input"
            />
          </div>

          <div className="verdict-filter-group">
            {['all', 'critical', 'high', 'elevated', 'low', 'new'].map((v) => (
              <button
                key={v}
                className={`filter-btn ${filterVerdict === v ? 'active' : ''}`}
                onClick={() => setFilterVerdict(v)}
              >
                {v.toUpperCase()}
              </button>
            ))}
          </div>

          <button className="btn btn-outline" onClick={onOpenIngest}>
            <span>⚡</span> Fast Ingest
          </button>
        </div>

        {/* Message Queue Table */}
        <div className="table-responsive">
          <table className="data-table">
            <thead>
              <tr>
                <th>Threat Verdict</th>
                <th>Score</th>
                <th>Sender / Claimed Entity</th>
                <th>Subject</th>
                <th>Received At</th>
                <th>Confidence</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={8} className="text-center py-6">
                    <div className="spinner"></div> Loading forensic queue...
                  </td>
                </tr>
              ) : filteredMessages.length === 0 ? (
                <tr>
                  <td colSpan={8} className="empty-table-state">
                    <div className="empty-icon">📭</div>
                    <div>No messages found matching your search and filter criteria.</div>
                    <button className="btn btn-primary mt-3" onClick={onOpenIngest}>
                      Ingest Sample Message (.EML)
                    </button>
                  </td>
                </tr>
              ) : (
                filteredMessages.map((msg) => (
                  <tr key={msg.id} className="clickable-row" onClick={() => onSelectMessage(msg.id)}>
                    <td>
                      <span className={`verdict-pill ${getVerdictBadgeClass(msg.verdict)}`}>
                        {msg.verdict}
                      </span>
                    </td>
                    <td>
                      <div className="score-meter-mini">
                        <div
                          className={`score-fill ${getVerdictBadgeClass(msg.verdict)}`}
                          style={{ width: `${Math.min(100, Math.max(8, msg.score))}%` }}
                        ></div>
                        <span className="score-number">{msg.score}/100</span>
                      </div>
                    </td>
                    <td className="font-mono text-sm">{msg.sender}</td>
                    <td className="subject-cell">{msg.subject}</td>
                    <td className="text-muted text-sm">
                      {new Date(msg.received_at).toLocaleString()}
                    </td>
                    <td>
                      <span className={`conf-badge conf-${msg.confidence.toLowerCase()}`}>
                        {msg.confidence}
                      </span>
                    </td>
                    <td>
                      <span className="status-pill">{msg.status}</span>
                    </td>
                    <td onClick={(e) => e.stopPropagation()}>
                      <div className="action-buttons">
                        <button
                          className="btn btn-sm btn-primary"
                          onClick={() => onSelectMessage(msg.id)}
                          title="Deep Dive Investigation"
                        >
                          🔬 Deep Dive
                        </button>
                        <a
                          href={api.getReportPdfUrl(msg.id)}
                          target="_blank"
                          rel="noreferrer"
                          className="btn btn-sm btn-secondary"
                          title="Download PDF Report (BSA §63)"
                        >
                          📄 PDF
                        </a>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
