import React, { useState } from 'react';
import { api } from '../api';

interface IngestModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (messageId: string) => void;
}

export const IngestModal: React.FC<IngestModalProps> = ({ isOpen, onClose, onSuccess }) => {
  const [ingestType, setIngestType] = useState<'single_eml' | 'bulk_zip' | 'raw_headers'>('single_eml');
  const [file, setFile] = useState<File | null>(null);
  const [rawHeaders, setRawHeaders] = useState<string>('');
  const [sender, setSender] = useState<string>('');
  const [subject, setSubject] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [successInfo, setSuccessInfo] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccessInfo(null);

    try {
      if (ingestType === 'single_eml') {
        if (!file) {
          setError('Please select an .eml message file');
          setLoading(false);
          return;
        }
        const res = await api.uploadEml(file);
        setSuccessInfo(res.duplicate ? 'Duplicate message recognized and retrieved' : 'Message ingested & forensic pipeline completed');
        setTimeout(() => {
          onSuccess(res.id);
          onClose();
        }, 800);
      } else if (ingestType === 'bulk_zip') {
        if (!file) {
          setError('Please select a .zip archive of emails');
          setLoading(false);
          return;
        }
        const list = await api.uploadBulkZip(file);
        setSuccessInfo(`Bulk ingestion successful: processed ${list.length} message(s)`);
        setTimeout(() => {
          if (list.length > 0) onSuccess(list[0].id);
          onClose();
        }, 1200);
      } else {
        if (!rawHeaders.trim() || rawHeaders.trim().length < 10) {
          setError('Please paste valid email headers (minimum 10 characters)');
          setLoading(false);
          return;
        }
        const res = await api.ingestRawHeaders(rawHeaders, sender || undefined, subject || undefined);
        setSuccessInfo(res.duplicate ? 'Duplicate headers detected and retrieved' : 'Headers ingested & forensic pipeline completed');
        setTimeout(() => {
          onSuccess(res.id);
          onClose();
        }, 800);
      }
    } catch (err: any) {
      setError(err.message || 'Ingestion failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-dialog" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3>Ingest Email Forensic Evidence (M1)</h3>
          <button className="modal-close-btn" onClick={onClose}>✕</button>
        </div>

        <form onSubmit={handleSubmit} className="modal-body">
          <div className="ingest-tabs">
            <button
              type="button"
              className={`tab-btn ${ingestType === 'single_eml' ? 'active' : ''}`}
              onClick={() => { setIngestType('single_eml'); setFile(null); setError(null); }}
            >
              📄 Single .EML Upload
            </button>
            <button
              type="button"
              className={`tab-btn ${ingestType === 'bulk_zip' ? 'active' : ''}`}
              onClick={() => { setIngestType('bulk_zip'); setFile(null); setError(null); }}
            >
              📦 Bulk .ZIP Archive
            </button>
            <button
              type="button"
              className={`tab-btn ${ingestType === 'raw_headers' ? 'active' : ''}`}
              onClick={() => { setIngestType('raw_headers'); setFile(null); setError(null); }}
            >
              📋 Raw Header Paste
            </button>
          </div>

          {error && <div className="alert-box error">{error}</div>}
          {successInfo && <div className="alert-box success">{successInfo}</div>}

          {ingestType === 'single_eml' && (
            <div className="form-group">
              <label>Select preserved RFC 5322 .eml file:</label>
              <input
                type="file"
                accept=".eml,.msg,.txt"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
                className="file-input"
              />
              <p className="form-hint">
                Preserves exact raw byte offsets, MIME part hierarchy, and original SHA-256 for non-repudiation.
              </p>
            </div>
          )}

          {ingestType === 'bulk_zip' && (
            <div className="form-group">
              <label>Select ZIP Archive (.zip) containing .eml files:</label>
              <input
                type="file"
                accept=".zip"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
                className="file-input"
              />
              <p className="form-hint">
                Safely unpacks with path-traversal safeguards and executes pipeline analysis across the batch.
              </p>
            </div>
          )}

          {ingestType === 'raw_headers' && (
            <div className="form-group">
              <label>Paste RFC 5322 Raw Header Block:</label>
              <textarea
                className="code-textarea"
                rows={8}
                placeholder={"Received: from ... by ...\nAuthentication-Results: ...\nFrom: sender@domain.com\nTo: victim@inst.ac.in\nSubject: ..."}
                value={rawHeaders}
                onChange={(e) => setRawHeaders(e.target.value)}
              />
              <div className="row-inputs">
                <input
                  type="text"
                  placeholder="Optional Sender override"
                  value={sender}
                  onChange={(e) => setSender(e.target.value)}
                  className="text-input"
                />
                <input
                  type="text"
                  placeholder="Optional Subject override"
                  value={subject}
                  onChange={(e) => setSubject(e.target.value)}
                  className="text-input"
                />
              </div>
            </div>
          )}

          <div className="modal-footer">
            <button type="button" className="btn btn-secondary" onClick={onClose} disabled={loading}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Ingesting & Analyzing...' : 'Start Forensic Ingestion'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
