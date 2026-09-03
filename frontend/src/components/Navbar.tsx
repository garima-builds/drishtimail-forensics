import React from 'react';

interface NavbarProps {
  onOpenIngest: () => void;
  onRefresh: () => void;
  onLogout?: () => void;
  activeTabTitle: string;
}

export const Navbar: React.FC<NavbarProps> = ({ onOpenIngest, onRefresh, onLogout, activeTabTitle }) => {
  return (
    <header className="navbar">
      <div className="navbar-left">
        <h1 className="navbar-title">{activeTabTitle}</h1>
      </div>

      <div className="navbar-right">
        <button className="btn btn-secondary" onClick={onRefresh} title="Refresh data">
          <span>🔄</span> Refresh
        </button>

        <button className="btn btn-primary" onClick={onOpenIngest}>
          <span>➕</span> Ingest Evidence
        </button>

        <div className="user-profile">
          <div className="user-avatar">FO</div>
          <div className="user-info">
            <span className="user-name">Forensic Analyst</span>
            <span className="user-role">Role: Investigator</span>
          </div>
          {onLogout && (
            <button
              className="btn btn-sm btn-secondary ml-2"
              onClick={onLogout}
              title="Sign Out Session"
              style={{ marginLeft: '10px' }}
            >
              Sign Out
            </button>
          )}
        </div>
      </div>
    </header>
  );
};
