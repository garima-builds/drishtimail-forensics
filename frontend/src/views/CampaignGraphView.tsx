import React, { useEffect, useRef, useState, useCallback } from 'react';
import cytoscape from 'cytoscape';
import type { Core, EventObject } from 'cytoscape';
import { CampaignItem, GraphNodeItem, GraphEdgeItem } from '../types';
import { api } from '../api';

const NODE_COLORS: Record<string, { bg: string; border: string; shape: string }> = {
  MESSAGE: { bg: '#2563eb', border: '#60a5fa', shape: 'diamond' },
  SENDER_EMAIL: { bg: '#9333ea', border: '#c084fc', shape: 'ellipse' },
  DOMAIN: { bg: '#0891b2', border: '#22d3ee', shape: 'round-rectangle' },
  IP: { bg: '#d97706', border: '#fcd34d', shape: 'rectangle' },
  URL: { bg: '#dc2626', border: '#f87171', shape: 'round-diamond' },
  STRUCTURAL_HASH: { bg: '#059669', border: '#34d399', shape: 'hexagon' },
  STRUCTURAL_FINGERPRINT: { bg: '#059669', border: '#34d399', shape: 'hexagon' },
  FILE_HASH: { bg: '#db2777', border: '#f472b6', shape: 'octagon' },
  DEFAULT: { bg: '#475569', border: '#94a3b8', shape: 'ellipse' },
};

export const CampaignGraphView: React.FC = () => {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const cyRef = useRef<Core | null>(null);

  const [campaigns, setCampaigns] = useState<CampaignItem[]>([]);
  const [graphData, setGraphData] = useState<{ nodes: GraphNodeItem[]; edges: GraphEdgeItem[] }>({ nodes: [], edges: [] });
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedCampaign, setSelectedCampaign] = useState<CampaignItem | null>(null);
  const [selectedNode, setSelectedNode] = useState<GraphNodeItem | null>(null);
  const [layoutName, setLayoutName] = useState<'cose' | 'concentric' | 'circle'>('cose');

  const loadGraph = useCallback(async (pivotNodeId?: string) => {
    setLoading(true);
    try {
      const [camps, gData] = await Promise.all([
        api.getCampaigns().catch(() => []),
        api.exploreGraph(pivotNodeId).catch(() => ({ nodes: [], edges: [] })),
      ]);
      const validCamps = Array.isArray(camps) ? camps : [];
      const validGraph = {
        nodes: Array.isArray(gData?.nodes) ? gData.nodes : [],
        edges: Array.isArray(gData?.edges) ? gData.edges : [],
      };
      setCampaigns(validCamps);
      setGraphData(validGraph);
      if (validCamps.length > 0 && !selectedCampaign) {
        setSelectedCampaign(validCamps[0]);
      }
    } catch (err: any) {
      console.error('Failed to load campaign graph data:', err);
    } finally {
      setLoading(false);
    }
  }, [selectedCampaign]);

  useEffect(() => {
    loadGraph();
  }, [loadGraph]);

  // Initialize and update Cytoscape instance
  useEffect(() => {
    if (!containerRef.current) return;

    const elements: cytoscape.ElementDefinition[] = [];

    // Transform backend nodes
    (graphData.nodes || []).forEach((n) => {
      const typeKey = (n.node_type || '').toUpperCase();
      const styleConfig = NODE_COLORS[typeKey] || NODE_COLORS.DEFAULT;
      elements.push({
        group: 'nodes',
        data: {
          id: n.id,
          label: n.value.length > 24 ? `${n.value.slice(0, 22)}…` : n.value,
          fullValue: n.value,
          nodeType: typeKey,
          sightingCount: n.sighting_count || 1,
          firstSeen: n.first_seen || new Date().toISOString(),
          bgColor: styleConfig.bg,
          borderColor: styleConfig.border,
          shape: styleConfig.shape,
        },
      });
    });

    // Transform backend edges
    (graphData.edges || []).forEach((e, idx) => {
      const sourceId = e.source || e.from_node;
      const targetId = e.target || e.to_node;
      if (sourceId && targetId) {
        elements.push({
          group: 'edges',
          data: {
            id: e.id || `edge-${sourceId}-${targetId}-${idx}`,
            source: sourceId,
            target: targetId,
            label: (e.edge_type || '').replace(/_/g, ' '),
            edgeType: e.edge_type || 'linked',
          },
        });
      }
    });

    // Destroy existing instance before creating new one
    if (cyRef.current) {
      cyRef.current.destroy();
    }

    if (elements.length === 0) return;

    const cy = cytoscape({
      container: containerRef.current,
      elements,
      style: [
        {
          selector: 'node',
          style: {
            'background-color': 'data(bgColor)',
            'border-color': 'data(borderColor)',
            'border-width': 2,
            'shape': 'data(shape)' as any,
            'label': 'data(label)',
            'color': '#f8fafc',
            'font-size': '11px',
            'font-family': 'monospace',
            'text-valign': 'bottom',
            'text-margin-y': 6,
            'text-background-color': '#090d16',
            'text-background-opacity': 0.85,
            'text-background-padding': '3px',
            'text-background-shape': 'roundrectangle',
            'width': '38px',
            'height': '38px',
            'transition-property': 'background-color, border-color, width, height',
            'transition-duration': 0.2,
          },
        },
        {
          selector: 'node:selected',
          style: {
            'border-color': '#38bdf8',
            'border-width': 4,
            'width': '46px',
            'height': '46px',
          },
        },
        {
          selector: 'edge',
          style: {
            'width': 2,
            'line-color': '#475569',
            'target-arrow-color': '#94a3b8',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            'arrow-scale': 1.1,
            'label': 'data(label)',
            'color': '#94a3b8',
            'font-size': '9px',
            'font-family': 'monospace',
            'text-rotation': 'autorotate',
            'text-background-color': '#0f172a',
            'text-background-opacity': 0.8,
            'text-background-padding': '2px',
          },
        },
        {
          selector: 'edge:selected',
          style: {
            'line-color': '#38bdf8',
            'target-arrow-color': '#38bdf8',
            'width': 3,
          },
        },
      ],
      layout: {
        name: layoutName,
        animate: true,
        animationDuration: 500,
        padding: 40,
      } as any,
      minZoom: 0.2,
      maxZoom: 3.0,
      wheelSensitivity: 0.25,
    });

    cy.on('tap', 'node', (evt: EventObject) => {
      const node = evt.target;
      const data = node.data();
      setSelectedNode({
        id: data.id,
        node_type: data.nodeType,
        value: data.fullValue,
        sighting_count: data.sightingCount,
        first_seen: data.firstSeen,
      });
    });

    cy.on('tap', (evt: EventObject) => {
      if (evt.target === cy) {
        setSelectedNode(null);
      }
    });

    cyRef.current = cy;

    return () => {
      if (cyRef.current) {
        cyRef.current.destroy();
        cyRef.current = null;
      }
    };
  }, [graphData, layoutName]);

  const handleFit = () => {
    if (cyRef.current) {
      cyRef.current.fit(undefined, 30);
    }
  };

  const handleZoom = (delta: number) => {
    if (cyRef.current) {
      const currentZoom = cyRef.current.zoom();
      cyRef.current.zoom(currentZoom * delta);
    }
  };

  const handlePivot = (nodeId: string) => {
    loadGraph(nodeId);
  };

  const handleResetGraph = () => {
    setSelectedNode(null);
    loadGraph();
  };

  const nodesCount = graphData.nodes?.length || 0;
  const edgesCount = graphData.edges?.length || 0;

  return (
    <div className="view-container">
      {/* Top Banner & Threat Intel Export Links */}
      <div className="card">
        <div className="card-header">
          <div>
            <h3>Campaign Memory & Correlation Graph (M5 / Feature F6)</h3>
            <p className="card-desc">
              Multi-dimensional property graph tracking structural HTML skeletons, lookalike domains, sender infrastructure, and cross-incident correlation.
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
        {/* Left Column: Correlated Campaigns */}
        <div className="card">
          <div className="card-header">
            <h4>Correlated Campaigns ({campaigns.length})</h4>
            <button className="btn btn-sm btn-outline" onClick={() => loadGraph()}>
              🔄 Refresh
            </button>
          </div>

          {loading && campaigns.length === 0 ? (
            <div className="spinner"></div>
          ) : campaigns.length === 0 ? (
            <div className="empty-card-state">
              <p>No campaign clusters found.</p>
            </div>
          ) : (
            <div className="campaigns-list">
              {campaigns.map((camp) => (
                <div
                  key={camp.id}
                  className={`campaign-item ${selectedCampaign?.id === camp.id ? 'active' : ''}`}
                  onClick={() => {
                    setSelectedCampaign(camp);
                    if (camp.id && camp.id !== 'single-incident-cluster') {
                      handlePivot(camp.id);
                    }
                  }}
                >
                  <div className="campaign-top">
                    <strong>{camp.name}</strong>
                    <span className={`badge-pill ${(camp.message_count || 1) > 1 ? 'badge-critical' : 'badge-low'}`}>
                      {camp.message_count || 1} Incident(s)
                    </span>
                  </div>
                  <div className="campaign-stats mt-2">
                    <span>Threat Score: <strong>{camp.score ? Math.round(camp.score) : 70}/100</strong></span>
                    <span>Status: <strong>{camp.status || 'Active'}</strong></span>
                  </div>
                  <div className="campaign-date mt-1">
                    Confidence: <strong>{camp.confidence}</strong>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Right Column: Visual Cytoscape Graph & Interactive Node Inspector */}
        <div className="card graph-card-wrapper">
          <div className="card-header">
            <div>
              <h4>Graph Neighborhood Explorer ({nodesCount} Nodes, {edgesCount} Edges)</h4>
              <span className="text-muted text-xs">Interactive Cytoscape.js Property Graph Visualizer</span>
            </div>
            <div className="graph-toolbar">
              <button className="btn btn-sm btn-outline" onClick={() => handleZoom(1.2)} title="Zoom In">➕</button>
              <button className="btn btn-sm btn-outline" onClick={() => handleZoom(0.8)} title="Zoom Out">➖</button>
              <button className="btn btn-sm btn-outline" onClick={handleFit} title="Fit to Canvas">🎯 Fit</button>
              <select
                value={layoutName}
                onChange={(e) => setLayoutName(e.target.value as any)}
                className="select-input select-sm"
                title="Graph Layout Algorithm"
              >
                <option value="cose">Force-Directed (CoSE)</option>
                <option value="concentric">Concentric Rings</option>
                <option value="circle">Circular Layout</option>
              </select>
              <button className="btn btn-sm btn-secondary" onClick={handleResetGraph} title="Reset to Root">
                Reset View
              </button>
            </div>
          </div>

          {/* Graph Visualizer Canvas */}
          <div className="graph-viewport-container">
            {nodesCount === 0 ? (
              <div className="empty-card-state" style={{ height: '440px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
                <div className="empty-icon" style={{ fontSize: '36px' }}>🕸️</div>
                <p>Ingest email messages to populate graph correlation nodes and edges.</p>
              </div>
            ) : (
              <div ref={containerRef} className="cytoscape-canvas" style={{ width: '100%', height: '460px', backgroundColor: '#090d16', borderRadius: '8px' }} />
            )}

            {/* Selected Node Floating Details Drawer */}
            {selectedNode && (
              <div className="node-detail-drawer">
                <div className="drawer-header">
                  <div>
                    <span className="badge-primary text-xs">{selectedNode.node_type}</span>
                    <h5 className="mt-1 font-mono text-xs">{selectedNode.value}</h5>
                  </div>
                  <button className="btn-close text-xs" onClick={() => setSelectedNode(null)}>✕</button>
                </div>
                <div className="drawer-body mt-2">
                  <div className="detail-row">
                    <span className="text-muted">Sightings:</span>
                    <strong>{selectedNode.sighting_count || 1} occurrence(s)</strong>
                  </div>
                  <div className="detail-row mt-1">
                    <span className="text-muted">First Observed:</span>
                    <span>{new Date(selectedNode.first_seen || Date.now()).toLocaleString()}</span>
                  </div>
                  <div className="drawer-actions mt-3">
                    <button
                      className="btn btn-sm btn-primary w-full"
                      onClick={() => handlePivot(selectedNode.id)}
                    >
                      🔍 Pivot on this Node
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Legend */}
          <div className="graph-legend mt-3">
            <span className="legend-item"><span className="legend-dot" style={{ backgroundColor: '#2563eb' }}></span> Message</span>
            <span className="legend-item"><span className="legend-dot" style={{ backgroundColor: '#9333ea' }}></span> Sender Email</span>
            <span className="legend-item"><span className="legend-dot" style={{ backgroundColor: '#0891b2' }}></span> Domain</span>
            <span className="legend-item"><span className="legend-dot" style={{ backgroundColor: '#d97706' }}></span> IP / Network</span>
            <span className="legend-item"><span className="legend-dot" style={{ backgroundColor: '#dc2626' }}></span> URL</span>
            <span className="legend-item"><span className="legend-dot" style={{ backgroundColor: '#059669' }}></span> Structural Fingerprint</span>
            <span className="legend-item"><span className="legend-dot" style={{ backgroundColor: '#db2777' }}></span> File Hash</span>
          </div>
        </div>
      </div>
    </div>
  );
};
