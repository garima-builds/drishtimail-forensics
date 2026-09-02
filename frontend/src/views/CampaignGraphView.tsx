import React, { useEffect, useState } from 'react';
import { CampaignItem, GraphNodeItem, GraphEdgeItem } from '../types';
import { api } from '../api';

export const CampaignGraphView: React.FC = () => {
  const [campaigns, setCampaigns] = useState<CampaignItem[]>([]);
  const [graph, setGraph] = useState<{ nodes: GraphNodeItem[]; edges: GraphEdgeItem[] }>({ nodes: [], edges: [] });
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedCampaign, setSelectedCampaign] = useState<CampaignItem | null>(null);

  useEffect(() => {
    loadGraphData();
  }, []);

  const loadGraphData = async () => {
    setLoading(true);
    try {
      const [camps, gData] = await Promise.all([
        api.getCampaigns(),
        api.exploreGraph(),
      ]);
      setCampaigns(camps);
      setGraph(gData);
      if (camps.length > 0) setSelectedCampaign(camps[0]);
    } catch (err: any) {
      console.error('Failed to load campaign graph data:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="view-container">
      {/* Top Banner & IOC Export Links */}
      <div className="card">
        <div className="card-header">
          <div>
            <h3>Campaign Correlation & Infrastructure Graph (M5 / Feature F6)</h3>
            <p className="card-desc">
              Uncovers coordinated spear-phishing campaigns via shared IP infrastructure, lookalike domains, and structural HTML skeleton fingerprints.
            </p>
          </div>
          <div className="export-actions">
            <span className="export-label">Export Threat IOCs:</span>
            <a href={api.getExportIocUrl('stix')} target="_blank" rel="noreferrer" className="btn btn-sm btn-secondary">
              📦 STIX 2.1
            </a>
            <a href={api.getExportIocUrl('misp')} target="_blank" rel="noreferrer" className="btn btn-sm btn-secondary">
              🛡️ MISP JSON
            </a>
            <a href={api.getExportIocUrl('csv')} target="_blank" rel="noreferrer" className="btn btn-sm btn-secondary">
              📑 CSV
            </a>
          </div>
        </div>
      </div>

      <div className="investigation-grid mt-4">
        {/* Left Column: Discovered Campaign Clusters */}
        <div className="card">
          <div className="card-header">
            <h4>Correlated Campaigns ({campaigns.length})</h4>
            <button className="btn btn-sm btn-outline" onClick={loadGraphData}>
              🔄 Refresh Clusters
            </button>
          </div>

          {loading ? (
            <div className="spinner"></div>
          ) : campaigns.length === 0 ? (
            <div className="empty-card-state">
              <p>No multi-message campaign clusters formed yet.</p>
            </div>
          ) : (
            <div className="campaigns-list">
              {campaigns.map((camp) => (
                <div
                  key={camp.id}
                  className={`campaign-item ${selectedCampaign?.id === camp.id ? 'active' : ''}`}
                  onClick={() => setSelectedCampaign(camp)}
                >
                  <div className="campaign-top">
                    <strong>{camp.name}</strong>
                    <span className="badge-critical">{camp.message_count} message(s)</span>
                  </div>
                  <div className="campaign-stats">
                    <span>Shared IPs: <strong>{camp.shared_ip_count}</strong></span>
                    <span>Shared Domains: <strong>{camp.shared_domain_count}</strong></span>
                    <span>Confidence: <strong>{camp.confidence}</strong></span>
                  </div>
                  <div className="campaign-date">
                    First Seen: {new Date(camp.first_seen).toLocaleDateString()} • Last Seen: {new Date(camp.last_seen).toLocaleDateString()}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Right Column: Interactive Correlation Graph Representation */}
        <div className="card">
          <div className="card-header">
            <h4>Graph Neighborhood Explorer ({graph.nodes.length} Nodes, {graph.edges.length} Edges)</h4>
            <span className="badge-outline">Property Graph Clustering</span>
          </div>

          <div className="graph-visualizer-canvas">
            {graph.nodes.length === 0 ? (
              <div className="empty-card-state">
                <div className="empty-icon">🕸️</div>
                <p>Ingest messages to populate graph correlation nodes.</p>
              </div>
            ) : (
              <div className="graph-nodes-cloud">
                {graph.nodes.map((node) => (
                  <div key={node.id} className={`graph-node-chip ${node.node_type}`}>
                    <span className="node-type-label">{node.node_type}</span>
                    <span className="node-val">{node.value}</span>
                    <span className="node-sighting">×{node.sighting_count}</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="graph-legend mt-3">
            <span className="legend-item"><span className="dot dot-msg"></span> Message</span>
            <span className="legend-item"><span className="dot dot-ip"></span> IP Address</span>
            <span className="legend-item"><span className="dot dot-domain"></span> Domain</span>
            <span className="legend-item"><span className="dot dot-skel"></span> HTML Skeleton Hash</span>
            <span className="legend-item"><span className="dot dot-email"></span> Sender Email</span>
          </div>
        </div>
      </div>
    </div>
  );
};
