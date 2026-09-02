import {
  Message, DashboardSummary, AnalysisRunResult, CaseItem, CampaignItem,
  ModelRegistryItem, LedgerItem, GraphNodeItem, GraphEdgeItem
} from './types';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

function authHeaders(): Record<string, string> {
  const token = localStorage.getItem('drishtimail_token');
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export const api = {
  // Auth
  async login(email: string, password: string): Promise<string> {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) throw new Error('Invalid credentials');
    const data = await res.json();
    localStorage.setItem('drishtimail_token', data.access_token);
    return data.access_token;
  },

  logout(): void {
    localStorage.removeItem('drishtimail_token');
  },

  getToken(): string | null {
    return localStorage.getItem('drishtimail_token');
  },

  // Dashboard & Messages
  async getSummary(): Promise<DashboardSummary> {
    const res = await fetch(`${API_BASE}/dashboard/summary`);
    if (!res.ok) throw new Error('Failed to load dashboard summary');
    return res.json();
  },

  async getMessages(): Promise<Message[]> {
    const res = await fetch(`${API_BASE}/messages`);
    if (!res.ok) throw new Error('Failed to fetch messages');
    return res.json();
  },

  async getMessage(id: string): Promise<Message> {
    const res = await fetch(`${API_BASE}/messages/${id}`);
    if (!res.ok) throw new Error('Failed to fetch message');
    return res.json();
  },

  async getAnalysis(id: string): Promise<AnalysisRunResult> {
    const res = await fetch(`${API_BASE}/messages/${id}/analysis`, {
      headers: authHeaders(),
    });
    if (!res.ok) throw new Error('Failed to load forensic analysis');
    return res.json();
  },

  async runAnalysis(id: string): Promise<AnalysisRunResult> {
    const res = await fetch(`${API_BASE}/messages/${id}/analyze`, {
      method: 'POST',
      headers: authHeaders(),
    });
    if (!res.ok) throw new Error('Pipeline execution failed');
    return res.json();
  },

  // Ingestion (M1)
  async uploadEml(file: File): Promise<Message & { duplicate: boolean }> {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE}/ingest/upload`, {
      method: 'POST',
      headers: authHeaders(),
      body: formData,
    });
    if (!res.ok) throw new Error('Failed to ingest .eml message');
    return res.json();
  },

  async uploadBulkZip(file: File): Promise<Array<Message & { duplicate: boolean }>> {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE}/ingest/bulk-zip`, {
      method: 'POST',
      headers: authHeaders(),
      body: formData,
    });
    if (!res.ok) throw new Error('Failed to ingest ZIP archive');
    return res.json();
  },

  async ingestRawHeaders(headersRaw: string, sender?: string, subject?: string): Promise<Message & { duplicate: boolean }> {
    const res = await fetch(`${API_BASE}/ingest/raw-headers`, {
      method: 'POST',
      headers: { ...authHeaders(), 'Content-Type': 'application/json' },
      body: JSON.stringify({ headers_raw: headersRaw, sender, subject }),
    });
    if (!res.ok) throw new Error('Failed to ingest raw headers');
    return res.json();
  },

  // Cases (M6)
  async getCases(): Promise<CaseItem[]> {
    const res = await fetch(`${API_BASE}/cases`);
    if (!res.ok) throw new Error('Failed to load cases');
    return res.json();
  },

  async createCase(title: string, messageIds: string[]): Promise<CaseItem> {
    const res = await fetch(`${API_BASE}/cases`, {
      method: 'POST',
      headers: { ...authHeaders(), 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, message_ids: messageIds }),
    });
    if (!res.ok) throw new Error('Failed to create case');
    return res.json();
  },

  async updateCase(id: string, status?: string, note?: string): Promise<CaseItem> {
    const res = await fetch(`${API_BASE}/cases/${id}`, {
      method: 'PATCH',
      headers: { ...authHeaders(), 'Content-Type': 'application/json' },
      body: JSON.stringify({ status, note }),
    });
    if (!res.ok) throw new Error('Failed to update case');
    return res.json();
  },

  // Campaign & Graph (M5 / F6)
  async getCampaigns(): Promise<CampaignItem[]> {
    const res = await fetch(`${API_BASE}/campaigns`);
    if (!res.ok) throw new Error('Failed to load campaigns');
    return res.json();
  },

  async exploreGraph(nodeId?: string): Promise<{ nodes: GraphNodeItem[]; edges: GraphEdgeItem[] }> {
    const url = nodeId ? `${API_BASE}/graph/explore?node_id=${encodeURIComponent(nodeId)}` : `${API_BASE}/graph/explore`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to fetch graph data');
    return res.json();
  },

  // IOC Export (M5)
  getExportIocUrl(format: 'stix' | 'misp' | 'csv'): string {
    return `${API_BASE}/export/iocs?format=${format}`;
  },

  // ML Evaluation (M12 / F2)
  async getModelRegistry(): Promise<ModelRegistryItem[]> {
    const res = await fetch(`${API_BASE}/evaluation/registry`);
    if (!res.ok) throw new Error('Failed to load model registry');
    return res.json();
  },

  async runModelEvaluation(): Promise<ModelRegistryItem> {
    const res = await fetch(`${API_BASE}/evaluation/run`, {
      method: 'POST',
      headers: authHeaders(),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Model evaluation request failed');
    }
    return res.json();
  },

  async triggerEvaluation(): Promise<ModelRegistryItem> {
    return this.runModelEvaluation();
  },

  // Ledger & Verification (M7 / F7)
  async getLedgerEntries(): Promise<LedgerItem[]> {
    const res = await fetch(`${API_BASE}/ledger/entries`, {
      headers: authHeaders(),
    });
    if (!res.ok) throw new Error('Failed to load evidence ledger');
    return res.json();
  },

  async sealMerkleRoot(): Promise<{ root_hash: string; from_sequence: number; to_sequence: number }> {
    const res = await fetch(`${API_BASE}/ledger/roots`, {
      method: 'POST',
      headers: authHeaders(),
    });
    if (!res.ok) throw new Error('Failed to seal Merkle root');
    return res.json();
  },

  // Admin Config (M8)
  async getConfig(key: string): Promise<any> {
    const res = await fetch(`${API_BASE}/admin/config/${key}`);
    if (!res.ok) throw new Error(`Failed to load config ${key}`);
    return res.json();
  },

  async updateConfig(key: string, value: any): Promise<any> {
    const res = await fetch(`${API_BASE}/admin/config/${key}`, {
      method: 'PUT',
      headers: { ...authHeaders(), 'Content-Type': 'application/json' },
      body: JSON.stringify({ value }),
    });
    if (!res.ok) throw new Error(`Failed to update config ${key}`);
    return res.json();
  },

  // Reports (M6)
  getReportPdfUrl(messageId: string): string {
    return `${API_BASE}/messages/${messageId}/report.pdf`;
  },
  getReportHtmlUrl(messageId: string): string {
    return `${API_BASE}/messages/${messageId}/report`;
  },
};
