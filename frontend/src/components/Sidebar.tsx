import React from 'react';

export type ActiveTab = 'queue' | 'investigate' | 'cases' | 'campaigns' | 'reports' | 'evaluation' | 'ledger' | 'admin';

interface SidebarProps {
  activeTab: ActiveTab;
  onSelectTab: (tab: ActiveTab) => void;
  selectedMessageId: string | null;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, onSelectTab, selectedMessageId }) => {
  const handleClick = (e: React.MouseEvent, tab: ActiveTab) => {
    e.preventDefault();
    onSelectTab(tab);
  };

  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="brand-logo">
          <span className="brand-icon">🛡️</span>
          <div>
            <div className="brand-title">DrishtiMail</div>
            <div className="brand-sub">Forensics Platform</div>
          </div>
        </div>
      </div>

      <div className="sidebar-section-title">CORE INVESTIGATION</div>
      <nav className="sidebar-nav">
        <a
          href="#/queue"
          data-tab="queue"
          className={`nav-btn ${activeTab === 'queue' ? 'active' : ''}`}
          onClick={(e) => handleClick(e, 'queue')}
        >
          <span className="nav-icon">📥</span>
          <span>Investigation Queue</span>
        </a>

        <a
          href="#/investigate"
          data-tab="investigate"
          className={`nav-btn ${activeTab === 'investigate' ? 'active' : ''}`}
          onClick={(e) => handleClick(e, 'investigate')}
        >
          <span className="nav-icon">🔬</span>
          <span>Investigation Deep Dive</span>
          {selectedMessageId && <span className="nav-badge">Active</span>}
        </a>

        <a
          href="#/cases"
          data-tab="cases"
          className={`nav-btn ${activeTab === 'cases' ? 'active' : ''}`}
          onClick={(e) => handleClick(e, 'cases')}
        >
          <span className="nav-icon">📁</span>
          <span>Cases</span>
        </a>
      </nav>

      <div className="sidebar-section-title">INTELLIGENCE & REPORTING</div>
      <nav className="sidebar-nav">
        <a
          href="#/campaigns"
          data-tab="campaigns"
          className={`nav-btn ${activeTab === 'campaigns' ? 'active' : ''}`}
          onClick={(e) => handleClick(e, 'campaigns')}
        >
          <span className="nav-icon">🕸️</span>
          <span>Campaign Graph</span>
        </a>

        <a
          href="#/reports"
          data-tab="reports"
          className={`nav-btn ${activeTab === 'reports' ? 'active' : ''}`}
          onClick={(e) => handleClick(e, 'reports')}
        >
          <span className="nav-icon">📄</span>
          <span>Reports & BSA §63</span>
        </a>
      </nav>

      <div className="sidebar-section-title">ASSURANCE & CONFIG</div>
      <nav className="sidebar-nav">
        <a
          href="#/evaluation"
          data-tab="evaluation"
          className={`nav-btn ${activeTab === 'evaluation' ? 'active' : ''}`}
          onClick={(e) => handleClick(e, 'evaluation')}
        >
          <span className="nav-icon">📊</span>
          <span>ML Evaluation (F2)</span>
        </a>

        <a
          href="#/ledger"
          data-tab="ledger"
          className={`nav-btn ${activeTab === 'ledger' ? 'active' : ''}`}
          onClick={(e) => handleClick(e, 'ledger')}
        >
          <span className="nav-icon">⛓️</span>
          <span>Evidence Ledger (F7)</span>
        </a>

        <a
          href="#/admin"
          data-tab="admin"
          className={`nav-btn ${activeTab === 'admin' ? 'active' : ''}`}
          onClick={(e) => handleClick(e, 'admin')}
        >
          <span className="nav-icon">⚙️</span>
          <span>Administration</span>
        </a>
      </nav>

      <div className="sidebar-footer">
        <div className="system-status-indicator">
          <span className="status-dot online"></span>
          <span className="status-text">Core Local Analysis: Online</span>
        </div>
        <div className="system-version">SIH26106 • Arch v2</div>
      </div>
    </aside>
  );
};
