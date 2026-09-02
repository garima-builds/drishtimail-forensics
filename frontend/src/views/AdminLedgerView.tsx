import React, { useEffect, useState } from 'react';
import { LedgerItem } from '../types';
import { api } from '../api';

interface AdminLedgerViewProps {
  initialTab?: 'ledger' | 'config';
}

export const AdminLedgerView: React.FC<AdminLedgerViewProps> = ({ initialTab = 'ledger' }) => {
  const [activeSubTab, setActiveSubTab] = useState<'ledger' | 'config'>(initialTab);
  const [entries, setEntries] = useState<LedgerItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [sealing, setSealing] = useState<boolean>(false);
  const [sealResult, setSealResult] = useState<string | null>(null);

  // Sync with initialTab prop if it changes
  useEffect(() => {
    if (initialTab) {
      setActiveSubTab(initialTab);
    }
  }, [initialTab]);

  // Config States
  const [trustedMtas, setTrustedMtas] = useState<string>('');
  const [vips, setVips] = useState<string>('');
  const [domains, setDomains] = useState<string>('');
  const [savingConfig, setSavingConfig] = useState<boolean>(false);

  useEffect(() => {
    loadLedgerData();
    loadConfigs();
  }, []);

  const loadLedgerData = async () => {
    setLoading(true);
    try {
      const data = await api.getLedgerEntries().catch(() => []);
      setEntries(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error('Failed to load ledger:', err);
      setEntries([]);
    } finally {
      setLoading(false);
    }
  };

  const loadConfigs = async () => {
    try {
      const [mtas, vipData, domData] = await Promise.all([
        api.getConfig('trusted_mtas').catch(() => ({ value: {} })),
        api.getConfig('protected_identities').catch(() => ({ value: {} })),
        api.getConfig('institutional_domains').catch(() => ({ value: {} })),
      ]);
      setTrustedMtas(JSON.stringify(mtas.value || {}, null, 2));
      setVips(JSON.stringify(vipData.value || {}, null, 2));
      setDomains(JSON.stringify(domData.value || {}, null, 2));
    } catch (err) {
      console.error('Failed to load platform configs:', err);
    }
  };

  const handleSealMerkleRoot = async () => {
    setSealing(true);
    setSealResult(null);
    try {
      const res = await api.sealMerkleRoot();
      setSealResult(`Merkle root sealed: ${res.root_hash.slice(0, 24)}... across entries #${res.from_sequence} - #${res.to_sequence}`);
      await loadLedgerData();
    } catch (err: any) {
      alert(`Merkle root sealing failed: ${err.message}`);
    } finally {
      setSealing(false);
    }
  };

  const handleSaveConfig = async (key: string, rawJson: string) => {
    setSavingConfig(true);
    try {
      const parsed = JSON.parse(rawJson);
      await api.updateConfig(key, parsed);
      alert(`Config '${key}' updated successfully!`);
      await loadConfigs();
    } catch (err: any) {
      alert(`Failed to save config: ${err.message}`);
    } finally {
      setSavingConfig(false);
    }
  };

  return (
    <div className="view-container">
      {/* Header Tabs */}
      <div className="card">
        <div className="card-header">
          <div>
            <h3>Evidence Ledger Integrity & Platform Admin (M7 / M8 / F7)</h3>
            <p className="card-desc">
              Append-only cryptographic chain-of-custody tracking with Merkle root anchoring and institutional security policy registry.
            </p>
          </div>
          <div className="subtab-toggle">
            <button
              className={`filter-btn ${activeSubTab === 'ledger' ? 'active' : ''}`}
              onClick={() => setActiveSubTab('ledger')}
            >
              ⛓️ Immutable Ledger
            </button>
            <button
              className={`filter-btn ${activeSubTab === 'config' ? 'active' : ''}`}
              onClick={() => setActiveSubTab('config')}
            >
              ⚙️ Platform Config
            </button>
          </div>
        </div>
      </div>

      {activeSubTab === 'ledger' && (
        <div className="card mt-4">
          <div className="card-header">
            <div>
              <h4>Cryptographic Evidence Chain ({entries.length} Ledger Entries)</h4>
              <span className="text-muted text-xs">Append-only • Non-repudiation assured via SHA-256 state hashes</span>
            </div>
            <div className="header-actions">
              <button className="btn btn-sm btn-outline" onClick={loadLedgerData}>
                🔄 Refresh
              </button>
              <button
                className="btn btn-sm btn-primary"
                onClick={handleSealMerkleRoot}
                disabled={sealing}
              >
                {sealing ? 'Sealing Root...' : '🔒 Seal Merkle Root'}
              </button>
            </div>
          </div>

          {sealResult && <div className="alert-box success mt-3">{sealResult}</div>}

          {loading ? (
            <div className="spinner mt-4"></div>
          ) : (
            <div className="table-responsive mt-3">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Seq #</th>
                    <th>Event Type</th>
                    <th>Subject ID</th>
                    <th>Entry Hash (SHA-256)</th>
                    <th>Previous Hash</th>
                    <th>Recorded At</th>
                  </tr>
                </thead>
                <tbody>
                  {entries.map((ent) => (
                    <tr key={ent.sequence}>
                      <td><strong>#{ent.sequence}</strong></td>
                      <td><span className="badge-outline">{ent.event_type}</span></td>
                      <td><code className="code-pill text-xs">{ent.subject_id.slice(0, 16)}...</code></td>
                      <td><code className="font-mono text-xs text-accent">{ent.entry_hash.slice(0, 24)}...</code></td>
                      <td>
                        <code className="font-mono text-xs text-muted">
                          {ent.previous_hash ? `${ent.previous_hash.slice(0, 16)}...` : 'GENESIS'}
                        </code>
                      </td>
                      <td className="text-muted text-xs">{new Date(ent.created_at).toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {activeSubTab === 'config' && (
        <div className="investigation-grid mt-4">
          {/* Trusted MTAs Config */}
          <div className="card">
            <div className="card-header">
              <h4>Trusted MTA Perimeter (M3)</h4>
              <button
                className="btn btn-sm btn-primary"
                onClick={() => handleSaveConfig('trusted_mtas', trustedMtas)}
                disabled={savingConfig}
              >
                Save
              </button>
            </div>
            <p className="card-desc">Subnets and hostnames recognized as internal perimeter boundaries.</p>
            <textarea
              className="code-textarea"
              rows={8}
              value={trustedMtas}
              onChange={(e) => setTrustedMtas(e.target.value)}
            />
          </div>

          {/* Protected VIP Identities */}
          <div className="card">
            <div className="card-header">
              <h4>Protected VIP Identities (M2)</h4>
              <button
                className="btn btn-sm btn-primary"
                onClick={() => handleSaveConfig('protected_identities', vips)}
                disabled={savingConfig}
              >
                Save
              </button>
            </div>
            <p className="card-desc">Executive names, board members, and dignitaries monitored for impersonation.</p>
            <textarea
              className="code-textarea"
              rows={8}
              value={vips}
              onChange={(e) => setVips(e.target.value)}
            />
          </div>

          {/* Institutional Domains */}
          <div className="card">
            <div className="card-header">
              <h4>Institutional Domains (M2/M3)</h4>
              <button
                className="btn btn-sm btn-primary"
                onClick={() => handleSaveConfig('institutional_domains', domains)}
                disabled={savingConfig}
              >
                Save
              </button>
            </div>
            <p className="card-desc">Legitimate internal organizational domain names monitored for lookalikes.</p>
            <textarea
              className="code-textarea"
              rows={8}
              value={domains}
              onChange={(e) => setDomains(e.target.value)}
            />
          </div>
        </div>
      )}
    </div>
  );
};
