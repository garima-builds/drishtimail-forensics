import React, { useEffect, useState } from 'react';
import { CaseItem } from '../types';
import { api } from '../api';

interface CaseManagementViewProps {
  onSelectMessage: (id: string) => void;
}

export const CaseManagementView: React.FC<CaseManagementViewProps> = ({ onSelectMessage }) => {
  const [cases, setCases] = useState<CaseItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedCase, setSelectedCase] = useState<CaseItem | null>(null);
  const [newCaseTitle, setNewCaseTitle] = useState<string>('');
  const [newNote, setNewNote] = useState<string>('');
  const [showCreateModal, setShowCreateModal] = useState<boolean>(false);
  const [updating, setUpdating] = useState<boolean>(false);

  useEffect(() => {
    loadCases();
  }, []);

  const loadCases = async () => {
    setLoading(true);
    try {
      const data = await api.getCases();
      // Ensure notes and message_ids are arrays
      const sanitized = (data || []).map((c) => ({
        ...c,
        notes: Array.isArray(c.notes) ? c.notes : [],
        message_ids: Array.isArray(c.message_ids) ? c.message_ids : [],
      }));
      setCases(sanitized);
      if (sanitized.length > 0 && !selectedCase) {
        setSelectedCase(sanitized[0]);
      } else if (selectedCase) {
        const refreshed = sanitized.find((c) => c.id === selectedCase.id);
        if (refreshed) setSelectedCase(refreshed);
      }
    } catch (err) {
      console.error('Failed to load cases:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateCase = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newCaseTitle.trim()) return;
    try {
      const created = await api.createCase(newCaseTitle.trim(), []);
      setNewCaseTitle('');
      setShowCreateModal(false);
      await loadCases();
      setSelectedCase({
        ...created,
        notes: Array.isArray(created.notes) ? created.notes : [],
        message_ids: Array.isArray(created.message_ids) ? created.message_ids : [],
      });
    } catch (err: any) {
      alert(`Failed to create case: ${err.message}`);
    }
  };

  const handleAddNote = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedCase || !newNote.trim()) return;
    setUpdating(true);
    try {
      const updated = await api.updateCase(selectedCase.id, undefined, newNote.trim());
      const cleanUpdated = {
        ...updated,
        notes: Array.isArray(updated.notes) ? updated.notes : [],
        message_ids: Array.isArray(updated.message_ids) ? updated.message_ids : [],
      };
      setNewNote('');
      setSelectedCase(cleanUpdated);
      await loadCases();
    } catch (err: any) {
      alert(`Failed to add note: ${err.message}`);
    } finally {
      setUpdating(false);
    }
  };

  const handleStatusChange = async (newStatus: string) => {
    if (!selectedCase) return;
    setUpdating(true);
    try {
      const updated = await api.updateCase(selectedCase.id, newStatus, undefined);
      const cleanUpdated = {
        ...updated,
        notes: Array.isArray(updated.notes) ? updated.notes : [],
        message_ids: Array.isArray(updated.message_ids) ? updated.message_ids : [],
      };
      setSelectedCase(cleanUpdated);
      await loadCases();
    } catch (err: any) {
      alert(`Failed to update status: ${err.message}`);
    } finally {
      setUpdating(false);
    }
  };

  const linkedMessages = selectedCase && Array.isArray(selectedCase.message_ids) ? selectedCase.message_ids : [];
  const notesList = selectedCase && Array.isArray(selectedCase.notes) ? selectedCase.notes : [];

  return (
    <div className="view-container">
      <div className="cases-header-card">
        <div className="card-header">
          <div>
            <h3>Forensic Case Dossiers & Incident Management (M6)</h3>
            <p className="card-desc">
              Organize related phishing incidents into trackable case files with audit logging, analyst notes, and chain-of-custody tracking.
            </p>
          </div>
          <button className="btn btn-primary" onClick={() => setShowCreateModal(true)}>
            ➕ Create New Case
          </button>
        </div>
      </div>

      <div className="investigation-grid mt-4">
        {/* Cases List */}
        <div className="card">
          <div className="card-header">
            <h4>Case Dossiers ({cases.length})</h4>
            <button className="btn btn-sm btn-outline" onClick={loadCases}>
              🔄 Refresh
            </button>
          </div>

          {loading ? (
            <div className="spinner"></div>
          ) : cases.length === 0 ? (
            <div className="empty-card-state">
              <p>No cases created yet.</p>
              <button className="btn btn-secondary mt-2" onClick={() => setShowCreateModal(true)}>
                Create First Case
              </button>
            </div>
          ) : (
            <div className="cases-list">
              {cases.map((c) => (
                <div
                  key={c.id}
                  className={`case-list-item ${selectedCase?.id === c.id ? 'active' : ''}`}
                  onClick={() => setSelectedCase(c)}
                >
                  <div className="case-item-title">
                    <strong>{c.title}</strong>
                    <span className="status-pill">{c.status}</span>
                  </div>
                  <div className="case-item-meta">
                    <span>{(c.message_ids || []).length} Associated Evidence Item(s)</span>
                    <span>Created: {new Date(c.created_at).toLocaleDateString()}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Selected Case Workspace */}
        <div className="card">
          {selectedCase ? (
            <div>
              <div className="card-header">
                <div>
                  <h3>{selectedCase.title}</h3>
                  <span className="text-muted text-xs font-mono">ID: {selectedCase.id}</span>
                </div>
                <div className="status-selector">
                  <label>Status:</label>
                  <select
                    value={selectedCase.status}
                    onChange={(e) => handleStatusChange(e.target.value)}
                    disabled={updating}
                    className="select-input"
                  >
                    <option value="New">New</option>
                    <option value="Triage">Triage</option>
                    <option value="In Investigation">In Investigation</option>
                    <option value="Closed - True Positive">Closed - True Positive</option>
                    <option value="Closed - Benign">Closed - Benign</option>
                  </select>
                </div>
              </div>

              {/* Linked Evidence Messages */}
              <div className="case-section">
                <h4>Associated Preserved Evidence ({linkedMessages.length})</h4>
                {linkedMessages.length === 0 ? (
                  <p className="text-muted text-sm">No email evidence messages linked to this case yet.</p>
                ) : (
                  <div className="linked-messages-list">
                    {linkedMessages.map((msgId) => (
                      <div key={msgId} className="linked-msg-row">
                        <code className="font-mono text-xs">{msgId}</code>
                        <div className="action-buttons">
                          <button
                            className="btn btn-sm btn-primary"
                            onClick={() => onSelectMessage(msgId)}
                          >
                            🔬 Inspect
                          </button>
                          <a
                            href={api.getReportPdfUrl(msgId)}
                            target="_blank"
                            rel="noreferrer"
                            className="btn btn-sm btn-secondary"
                          >
                            📄 PDF
                          </a>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Analyst Investigation Notes Timeline */}
              <div className="case-section mt-4">
                <h4>Analyst Notes & Audit Log</h4>
                <div className="notes-timeline">
                  {notesList.length === 0 ? (
                    <p className="text-muted text-sm">No notes recorded yet.</p>
                  ) : (
                    notesList.map((n, idx) => (
                      <div key={idx} className="note-card">
                        <div className="note-timestamp">
                          {n.at ? new Date(n.at).toLocaleString() : 'Recent'}
                        </div>
                        <div className="note-text">{n.text}</div>
                      </div>
                    ))
                  )}
                </div>

                <form onSubmit={handleAddNote} className="add-note-form mt-3">
                  <textarea
                    className="text-input"
                    rows={3}
                    placeholder="Add forensic observation, investigation findings, or disposition rationale..."
                    value={newNote}
                    onChange={(e) => setNewNote(e.target.value)}
                  />
                  <button type="submit" className="btn btn-primary mt-2" disabled={updating || !newNote.trim()}>
                    {updating ? 'Saving Note...' : 'Add Note to Dossier'}
                  </button>
                </form>
              </div>
            </div>
          ) : (
            <div className="empty-card-state">
              <p>Select a case dossier from the left to view notes and linked evidence.</p>
            </div>
          )}
        </div>
      </div>

      {/* Create Case Modal */}
      {showCreateModal && (
        <div className="modal-overlay" onClick={() => setShowCreateModal(false)}>
          <div className="modal-dialog" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Create Forensic Case Dossier</h3>
              <button className="modal-close-btn" onClick={() => setShowCreateModal(false)}>✕</button>
            </div>
            <form onSubmit={handleCreateCase} className="modal-body">
              <div className="form-group">
                <label>Case Title / Incident Name:</label>
                <input
                  type="text"
                  placeholder="e.g., Executive Impersonation & Quishing Campaign - Q3"
                  value={newCaseTitle}
                  onChange={(e) => setNewCaseTitle(e.target.value)}
                  className="text-input"
                  required
                />
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => setShowCreateModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary" disabled={!newCaseTitle.trim()}>
                  Create Dossier
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
