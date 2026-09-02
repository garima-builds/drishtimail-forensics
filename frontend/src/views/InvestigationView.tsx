import React, { useEffect, useState } from 'react';
import { Message, AnalysisRunResult } from '../types';
import { api } from '../api';

interface InvestigationViewProps {
  messageId: string | null;
  onBackToQueue: () => void;
  onSelectMessage: (id: string) => void;
}

export const InvestigationView: React.FC<InvestigationViewProps> = ({
  messageId,
  onBackToQueue,
  onSelectMessage,
}) => {
  const [message, setMessage] = useState<Message | null>(null);
  const [analysis, setAnalysis] = useState<AnalysisRunResult | null>(null);
  const [availableMessages, setAvailableMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'conflicts' | 'auth' | 'urls_qr' | 'hops' | 'intent'>('overview');
  const [reAnalyzing, setReAnalyzing] = useState<boolean>(false);

  useEffect(() => {
    if (messageId) {
      loadInvestigationData(messageId);
    } else {
      setLoading(true);
      api.getMessages().then((msgs) => {
        const safeMsgs = Array.isArray(msgs) ? msgs : [];
        setAvailableMessages(safeMsgs);
        if (safeMsgs.length > 0 && onSelectMessage) {
          onSelectMessage(safeMsgs[0].id);
        }
      }).catch(() => {}).finally(() => setLoading(false));
    }
  }, [messageId, onSelectMessage]);

  const loadInvestigationData = async (id: string) => {
    setLoading(true);
    setError(null);
    try {
      const [msg, anlz] = await Promise.all([
        api.getMessage(id),
        api.getAnalysis(id),
      ]);
      setMessage(msg);
      setAnalysis(anlz);
    } catch (err: any) {
      setError(err.message || 'Failed to load forensic data for message');
    } finally {
      setLoading(false);
    }
  };

  const handleReAnalyze = async () => {
    if (!messageId) return;
    setReAnalyzing(true);
    try {
      const res = await api.runAnalysis(messageId);
      setAnalysis(res);
      const msg = await api.getMessage(messageId);
      setMessage(msg);
    } catch (err: any) {
      alert(`Re-analysis failed: ${err.message}`);
    } finally {
      setReAnalyzing(false);
    }
  };

  if (!messageId) {
    return (
      <div className="view-container">
        <div className="card">
          <div className="card-header">
            <div>
              <h3>Investigation Deep Dive (M1–M11)</h3>
              <p className="card-desc">Select an ingested email message from the triage archive to inspect forensic evidence.</p>
            </div>
            <button className="btn btn-primary" onClick={onBackToQueue}>
              Go to Triage Queue
            </button>
          </div>

          {availableMessages.length > 0 ? (
            <div className="table-responsive mt-3">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Verdict</th>
                    <th>Threat Score</th>
                    <th>Sender</th>
                    <th>Subject</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {availableMessages.map((m) => (
                    <tr key={m.id}>
                      <td><span className={`verdict-tag ${(m.verdict || 'low').toLowerCase()}`}>{m.verdict}</span></td>
                      <td><strong>{m.score}/100</strong></td>
                      <td className="font-mono text-xs">{m.sender}</td>
                      <td>{m.subject}</td>
                      <td>
                        <button className="btn btn-sm btn-primary" onClick={() => onSelectMessage && onSelectMessage(m.id)}>
                          🔍 Inspect
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="empty-investigation-state">
              <div className="empty-icon">🔬</div>
              <h2>No Ingested Messages Found</h2>
              <p>Upload a preserved .eml message to begin deep dive forensic examination.</p>
              <button className="btn btn-primary" onClick={onBackToQueue}>
                Go to Triage Queue
              </button>
            </div>
          )}
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="view-container">
        <div className="loading-state">
          <div className="spinner large"></div>
          <h3>Executing Forensic Inspection Pipeline...</h3>
          <p>Extracting MIME tree, verifying protocol semantics, and evaluating evidence conflicts.</p>
        </div>
      </div>
    );
  }

  if (error || !message || !analysis) {
    return (
      <div className="view-container">
        <div className="alert-box error">
          <h4>Failed to load forensic analysis</h4>
          <p>{error || 'Message not found'}</p>
          <button className="btn btn-secondary mt-3" onClick={() => loadInvestigationData(messageId)}>
            Retry
          </button>
        </div>
      </div>
    );
  }

  const score = analysis.score;
  const auth = analysis.authentication;
  const origin = analysis.origin;
  const conflicts = analysis.conflicts || [];
  const urls = analysis.urls || [];
  const qrResults = analysis.qr_results || [];
  const hops = analysis.delivery_path || [];
  const detections = analysis.detections;

  const getVerdictClass = (v: string) => {
    switch (v) {
      case 'Critical': return 'verdict-critical';
      case 'High': return 'verdict-high';
      case 'Elevated': return 'verdict-elevated';
      default: return 'verdict-low';
    }
  };

  return (
    <div className="view-container">
      {/* Top Banner: Message Metadata & Preserved Evidence Details */}
      <div className="investigation-header-card">
        <div className="header-top-row">
          <div className="header-subject-block">
            <button className="back-link" onClick={onBackToQueue}>
              ← Back to Queue
            </button>
            <h2 className="investigation-subject">{message.subject}</h2>
            <div className="meta-row">
              <span className="meta-item"><strong>From:</strong> <code className="code-pill">{message.sender}</code></span>
              <span className="meta-item"><strong>Preserved Evidence Ref:</strong> <code className="code-pill">{message.evidence_reference.slice(0, 18)}...</code></span>
              <span className="meta-item"><strong>Received:</strong> {new Date(message.received_at).toLocaleString()}</span>
            </div>
          </div>

          <div className="header-actions">
            <button
              className="btn btn-secondary"
              onClick={handleReAnalyze}
              disabled={reAnalyzing}
            >
              {reAnalyzing ? '🔄 Re-analyzing...' : '🔄 Re-run Pipeline'}
            </button>

            <a
              href={api.getReportPdfUrl(message.id)}
              target="_blank"
              rel="noreferrer"
              className="btn btn-primary"
            >
              📄 Forensic PDF Report (BSA §63)
            </a>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="investigation-subtabs">
          <button className={`subtab-btn ${activeTab === 'overview' ? 'active' : ''}`} onClick={() => setActiveTab('overview')}>
            🧭 Overview & Scoring (M11)
          </button>
          <button className={`subtab-btn ${activeTab === 'conflicts' ? 'active' : ''}`} onClick={() => setActiveTab('conflicts')}>
            ⚡ Evidence Conflicts ({conflicts.length}) (M10)
          </button>
          <button className={`subtab-btn ${activeTab === 'auth' ? 'active' : ''}`} onClick={() => setActiveTab('auth')}>
            🔐 Auth Semantics (M3/F5)
          </button>
          <button className={`subtab-btn ${activeTab === 'urls_qr' ? 'active' : ''}`} onClick={() => setActiveTab('urls_qr')}>
            🔗 URLs & Quishing ({urls.length + qrResults.length}) (M9/F3)
          </button>
          <button className={`subtab-btn ${activeTab === 'hops' ? 'active' : ''}`} onClick={() => setActiveTab('hops')}>
            🌐 Relay Hops & Origin (M4)
          </button>
          <button className={`subtab-btn ${activeTab === 'intent' ? 'active' : ''}`} onClick={() => setActiveTab('intent')}>
            🎯 NLP Intent & Cues (M2)
          </button>
        </div>
      </div>

      {/* TAB 1: OVERVIEW & EXPLAINABLE THREAT SCORE (M11 / F8) */}
      {activeTab === 'overview' && (
        <div className="investigation-grid">
          {/* Left Column: Score Card & First Contact Guardrail */}
          <div className="card score-summary-card">
            <div className="card-header">
              <h3>Explainable Threat Score (M11 / Feature F8)</h3>
              <span className={`verdict-pill ${getVerdictClass(score.verdict)}`}>
                {score.verdict} Threat
              </span>
            </div>

            <div className="score-hero">
              <div className="score-dial">
                <span className="score-big">{score.value}</span>
                <span className="score-max">/ 100</span>
              </div>
              <div className="score-meta">
                <div className="meta-pill">Confidence: <strong>{score.confidence}</strong></div>
                <div className="meta-pill">Formula: <strong>Additive + Family Ceilings</strong></div>
              </div>
            </div>

            {/* First Contact Guardrail Notification */}
            {score.first_contact_suppressed && (
              <div className="guardrail-alert">
                <span className="guardrail-icon">🛡️</span>
                <div>
                  <strong>First-Contact Novelty Guardrail Active:</strong>
                  <div>{score.suppression_reason || 'Novelty alone cannot classify an email as high/critical threat without corroborating malicious indicators.'}</div>
                </div>
              </div>
            )}

            {/* Score Contributions Breakdown */}
            <h4 className="section-subtitle">Ranked Signal Contributions</h4>
            <div className="contributions-list">
              {score.contributions.map((c, idx) => (
                <div key={idx} className={`contribution-row ${c.points > 0 ? 'pos' : 'neg'}`}>
                  <div className="contrib-points">
                    {c.points > 0 ? `+${c.points}` : c.points}
                  </div>
                  <div className="contrib-body">
                    <div className="contrib-title">
                      <span className="signal-tag">{c.family}</span>
                      <strong>{c.signal.replace(/_/g, ' ')}</strong>
                    </div>
                    <div className="contrib-reason">{c.reason}</div>
                  </div>
                </div>
              ))}
            </div>

            <div className="score-disclaimer">
              <small>ℹ️ {score.disclaimer}</small>
            </div>
          </div>

          {/* Right Column: Key Takeaways & Conflicts Preview */}
          <div className="card summary-highlights-card">
            <div className="card-header">
              <h3>Forensic Triage Highlights</h3>
              <span className="badge-outline">Scenario: {analysis.scenario.scenario}</span>
            </div>

            <div className="scenario-box">
              <strong>Forensic Working Hypothesis:</strong>
              <p>{analysis.scenario.hypothesis}</p>
              <div className="text-muted text-xs mt-2">
                Caveat: {analysis.scenario.caveat}
              </div>
            </div>

            {/* Conflicts Card Preview */}
            <div className="highlights-section">
              <h4>Evidence Conflicts Detected ({conflicts.length})</h4>
              {conflicts.length === 0 ? (
                <div className="text-muted text-sm py-2">
                  ✓ No contradictions detected across protocols, content, or infrastructure.
                </div>
              ) : (
                <div className="conflicts-preview-list">
                  {conflicts.map((cnf, idx) => (
                    <div key={idx} className={`conflict-badge-item ${cnf.severity.toLowerCase()}`}>
                      <div className="conflict-badge-header">
                        <span className="badge-rule">{cnf.rule_id}</span>
                        <strong>{cnf.title}</strong>
                        <span className={`severity-tag ${cnf.severity.toLowerCase()}`}>{cnf.severity}</span>
                      </div>
                      <p className="conflict-badge-summary">{cnf.summary}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Origin & Auth Quick Snapshot */}
            <div className="snapshot-grid">
              <div className="snapshot-box">
                <span className="snapshot-label">Origin Network</span>
                <span className="snapshot-val">{origin.ip || 'Unknown'}</span>
                <span className="snapshot-sub">{origin.asn || 'ASN not mapped'} ({origin.country || 'Approximate'})</span>
              </div>
              <div className="snapshot-box">
                <span className="snapshot-label">Protocol Alignment</span>
                <span className="snapshot-val">
                  SPF: {auth.spf.toUpperCase()} | DKIM: {auth.dkim.toUpperCase()}
                </span>
                <span className="snapshot-sub">
                  DMARC: {auth.dmarc.toUpperCase()} ({auth.spf_aligned ? 'SPF Aligned' : 'Unaligned'})
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: EVIDENCE CONFLICT DETECTOR (M10 / F1) */}
      {activeTab === 'conflicts' && (
        <div className="card">
          <div className="card-header">
            <div>
              <h3>Evidence Conflict Detector (M10 / Feature F1)</h3>
              <p className="card-desc">
                Identifies contradictions between cryptographic validation, claimed identity, transit headers, and message payload.
              </p>
            </div>
            <span className="badge-info">{conflicts.length} Active Conflict(s)</span>
          </div>

          {conflicts.length === 0 ? (
            <div className="empty-card-state">
              <div className="empty-icon">⚖️</div>
              <h4>No Contradictory Evidence Detected</h4>
              <p>All protocol signals, delivery headers, and content vectors are mutually consistent.</p>
            </div>
          ) : (
            <div className="conflicts-full-grid">
              {conflicts.map((cnf, idx) => (
                <div key={idx} className={`conflict-card ${cnf.severity.toLowerCase()}`}>
                  <div className="conflict-card-top">
                    <div className="conflict-identity">
                      <span className="conflict-rule-chip">{cnf.rule_id}</span>
                      <h4>{cnf.title}</h4>
                    </div>
                    <span className={`severity-pill ${cnf.severity.toLowerCase()}`}>
                      {cnf.severity} Severity
                    </span>
                  </div>

                  <p className="conflict-summary-text">{cnf.summary}</p>

                  <div className="dual-citation-grid">
                    <div className="citation-box side-a">
                      <div className="citation-header">
                        <span className="citation-tag">Evidence Side A (Protocol / Claim)</span>
                      </div>
                      <div className="citation-content">{cnf.evidence_side_a}</div>
                      {cnf.evidence_ref_a_id && (
                        <div className="citation-ref">Ref: <code>{cnf.evidence_ref_a_id.slice(0, 16)}...</code></div>
                      )}
                    </div>

                    <div className="citation-box side-b">
                      <div className="citation-header">
                        <span className="citation-tag">Evidence Side B (Contradictory Signal)</span>
                      </div>
                      <div className="citation-content">{cnf.evidence_side_b}</div>
                      {cnf.evidence_ref_b_id && (
                        <div className="citation-ref">Ref: <code>{cnf.evidence_ref_b_id.slice(0, 16)}...</code></div>
                      )}
                    </div>
                  </div>

                  {cnf.investigative_guidance && (
                    <div className="guidance-box">
                      <strong>🔍 Recommended Analyst Action:</strong>
                      <p>{cnf.investigative_guidance}</p>
                    </div>
                  )}

                  {cnf.reconciliation_effect && (
                    <div className="reconciliation-box">
                      <strong>⚖️ Score Reconciliation:</strong> {cnf.reconciliation_effect} ({cnf.score_adjustment ? `${cnf.score_adjustment > 0 ? '+' : ''}${cnf.score_adjustment} pts` : 'No direct delta'})
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* TAB 3: AUTHENTICATION SEMANTICS (M3 / F5) */}
      {activeTab === 'auth' && (
        <div className="card">
          <div className="card-header">
            <div>
              <h3>Protocol Authentication Semantics (M3 / Feature F5)</h3>
              <p className="card-desc">
                Rigorous 3-part interpretation explaining what cryptographic passes establish and what they do NOT establish.
              </p>
            </div>
            <span className="semantics-badge">{auth.semantics_key}</span>
          </div>

          <div className="auth-status-bar">
            <div className="auth-stat-pill">
              <span className="stat-name">SPF</span>
              <span className={`stat-val ${auth.spf === 'pass' ? 'pass' : 'fail'}`}>{auth.spf.toUpperCase()}</span>
              <span className="stat-align">{auth.spf_aligned ? '✓ Aligned' : '✗ Unaligned'}</span>
            </div>
            <div className="auth-stat-pill">
              <span className="stat-name">DKIM</span>
              <span className={`stat-val ${auth.dkim === 'pass' ? 'pass' : 'fail'}`}>{auth.dkim.toUpperCase()}</span>
              <span className="stat-align">{auth.dkim_aligned ? '✓ Aligned' : '✗ Unaligned'}</span>
            </div>
            <div className="auth-stat-pill">
              <span className="stat-name">DMARC</span>
              <span className={`stat-val ${auth.dmarc === 'pass' ? 'pass' : 'fail'}`}>{auth.dmarc.toUpperCase()}</span>
            </div>
            <div className="auth-stat-pill">
              <span className="stat-name">ARC</span>
              <span className="stat-val neutral">{auth.arc_status.toUpperCase()}</span>
            </div>
            <div className="auth-stat-pill">
              <span className="stat-name">Forwarding Detected</span>
              <span className="stat-val neutral">{auth.forwarding_detected ? 'YES' : 'NO'}</span>
            </div>
          </div>

          {auth.is_lookalike_authenticated && (
            <div className="alert-box warning mt-4">
              <strong>⚠️ Lookalike Domain Cryptographic Validation:</strong>
              <div>This message passes SPF/DKIM/DMARC because the adversary registered and authenticated an attacker-controlled lookalike domain. A cryptographic pass confirms domain authorization, NOT human authenticity.</div>
            </div>
          )}

          {/* The 3-Part Prose Semantics Structure */}
          <div className="semantics-prose-grid mt-4">
            <div className="prose-card establishes">
              <div className="prose-header">
                <span className="prose-icon">✅</span>
                <h4>What This Establishes</h4>
              </div>
              <p>{auth.establishes}</p>
            </div>

            <div className="prose-card does-not-establish">
              <div className="prose-header">
                <span className="prose-icon">❌</span>
                <h4>What This Does NOT Establish</h4>
              </div>
              <p>{auth.does_not_establish}</p>
            </div>

            <div className="prose-card effect">
              <div className="prose-header">
                <span className="prose-icon">🎯</span>
                <h4>Forensic Investigation Effect</h4>
              </div>
              <p>{auth.investigation_effect}</p>
            </div>
          </div>
        </div>
      )}

      {/* TAB 4: URLS & QUISHING (M9 / F3) */}
      {activeTab === 'urls_qr' && (
        <div className="investigation-grid">
          {/* QR Code Analysis */}
          <div className="card">
            <div className="card-header">
              <h3>Multi-Angle Quishing / QR Detector (M9 / Feature F3)</h3>
              <span className="badge-info">{qrResults.length} QR Code(s) Found</span>
            </div>

            {qrResults.length === 0 ? (
              <div className="empty-card-state">
                <div className="empty-icon">📷</div>
                <h4>No QR Codes Detected</h4>
                <p>MIME inline images and static attachments scanned across 0°, 90°, 180°, and 270° orientations.</p>
              </div>
            ) : (
              <div className="qr-results-list">
                {qrResults.map((qr, idx) => (
                  <div key={idx} className="qr-item-card">
                    <div className="qr-top">
                      <span className="provenance-tag">{qr.provenance}</span>
                      <span className="rotation-tag">{qr.rotation || 0}° Orientation</span>
                      {qr.undecodable ? (
                        <span className="status-undecodable">⚠️ QR Present, Undecodable</span>
                      ) : (
                        <span className="status-decoded">✓ Decoded</span>
                      )}
                    </div>
                    <div className="qr-payload-box">
                      <strong>Decoded Payload URL:</strong>
                      <code className="payload-code">{qr.payload || 'Failed to decode payload (corrupt or stylized pattern)'}</code>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Extracted URLs & Mismatches */}
          <div className="card">
            <div className="card-header">
              <h3>URL Artifacts & Anchor Mismatch Detector</h3>
              <span className="badge-info">{urls.length} URL(s)</span>
            </div>

            {urls.length === 0 ? (
              <div className="empty-card-state">
                <div className="empty-icon">🔗</div>
                <h4>No URLs Found in Message Body</h4>
              </div>
            ) : (
              <div className="urls-table-wrapper">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Display Anchor</th>
                      <th>Actual Destination</th>
                      <th>Mismatch?</th>
                      <th>Provenance</th>
                    </tr>
                  </thead>
                  <tbody>
                    {urls.map((u, idx) => (
                      <tr key={idx} className={u.mismatch_flag ? 'row-warning' : ''}>
                        <td>
                          {u.anchor_text ? <span className="anchor-text">{u.anchor_text}</span> : <span className="text-muted">None</span>}
                        </td>
                        <td>
                          <code className="url-code" title={u.raw_url}>{u.destination_host || u.raw_url}</code>
                        </td>
                        <td>
                          {u.mismatch_flag ? (
                            <span className="mismatch-pill">⚠️ MISMATCH</span>
                          ) : (
                            <span className="match-pill">Match</span>
                          )}
                        </td>
                        <td className="text-xs text-muted">{u.provenance}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}

      {/* TAB 5: RELAY HOPS & ORIGIN GEOLOCATION (M4) */}
      {activeTab === 'hops' && (
        <div className="investigation-grid">
          {/* Origin Intelligence */}
          <div className="card">
            <div className="card-header">
              <h3>Origin Infrastructure Intelligence (M4)</h3>
              <span className="badge-outline">Confidence: {origin.confidence}</span>
            </div>

            <div className="origin-details-grid">
              <div className="origin-field">
                <span className="field-name">Candidate IP:</span>
                <span className="field-val font-mono">{origin.ip || 'Unknown'}</span>
              </div>
              <div className="origin-field">
                <span className="field-name">Infrastructure Type:</span>
                <span className={`infra-badge ${origin.infra_type}`}>{origin.infra_type.toUpperCase()}</span>
              </div>
              <div className="origin-field">
                <span className="field-name">Autonomous System (ASN):</span>
                <span className="field-val">{origin.asn || 'N/A'}</span>
              </div>
              <div className="origin-field">
                <span className="field-name">ISP / Host:</span>
                <span className="field-val">{origin.isp || 'N/A'}</span>
              </div>
              <div className="origin-field">
                <span className="field-name">Approximate Country:</span>
                <span className="field-val">{origin.country || 'Unknown'} ({origin.country_code || '??'})</span>
              </div>
              <div className="origin-field">
                <span className="field-name">Approximate Coordinates:</span>
                <span className="field-val">
                  {origin.latitude && origin.longitude ? `${origin.latitude.toFixed(2)}, ${origin.longitude.toFixed(2)}` : 'N/A'}
                </span>
              </div>
            </div>

            <div className="alert-box info mt-4">
              <strong>Approximate Infrastructure Intelligence Only:</strong>
              <div>{origin.caveat}</div>
            </div>
          </div>

          {/* Relay Hop Chain */}
          <div className="card">
            <div className="card-header">
              <h3>Relay Path & Trust Boundary (M3)</h3>
              <span className="badge-info">{hops.length} Hop(s)</span>
            </div>

            <div className="hops-timeline">
              {hops.map((hop) => (
                <div key={hop.hop_no} className={`hop-timeline-node ${hop.trust_status}`}>
                  <div className="hop-num">#{hop.hop_no}</div>
                  <div className="hop-content">
                    <div className="hop-header">
                      <strong>{hop.real_ip || hop.claimed_host || 'Unknown Host'}</strong>
                      <span className={`trust-tag ${hop.trust_status}`}>
                        {hop.trust_status.replace(/_/g, ' ').toUpperCase()}
                      </span>
                    </div>
                    <div className="hop-meta">
                      Claimed: <code>{hop.claimed_host || '-'}</code> | rDNS: <code>{hop.rdns || '-'}</code> | TLS: <code>{hop.tls_version || 'None'}</code>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* TAB 6: NLP INTENT & DETECTION (M2) */}
      {activeTab === 'intent' && (
        <div className="investigation-grid">
          {/* Classification Probabilities */}
          <div className="card">
            <div className="card-header">
              <h3>Six-Class Threat Probability Distribution (M2)</h3>
              <span className="badge-primary">Predicted: {detections.classification.predicted_class}</span>
            </div>

            <div className="probabilities-list">
              {Object.entries(detections.classification.probabilities).map(([clsName, prob]) => (
                <div key={clsName} className="prob-row">
                  <div className="prob-label">
                    <span>{clsName}</span>
                    <span>{(prob * 100).toFixed(1)}%</span>
                  </div>
                  <div className="prob-bar-track">
                    <div
                      className={`prob-bar-fill ${clsName.toLowerCase()}`}
                      style={{ width: `${Math.max(2, prob * 100)}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Social Engineering Cues */}
          <div className="card">
            <div className="card-header">
              <h3>Social Engineering & BEC Pattern Detections</h3>
            </div>

            <div className="detections-container">
              {detections.social_engineering.length === 0 && detections.bec_patterns.length === 0 ? (
                <div className="empty-card-state">
                  <p>No high-confidence social engineering or BEC intent patterns detected.</p>
                </div>
              ) : (
                <>
                  {detections.social_engineering.map((se, idx) => (
                    <div key={idx} className="detection-item se">
                      <span className="det-category">{se.category}</span>
                      <strong>{se.title}</strong>
                      <p>{se.description}</p>
                    </div>
                  ))}
                  {detections.bec_patterns.map((bec, idx) => (
                    <div key={idx} className="detection-item bec">
                      <span className="det-category">BEC / Financial Fraud</span>
                      <strong>{bec.title}</strong>
                      <p>{bec.description}</p>
                    </div>
                  ))}
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
