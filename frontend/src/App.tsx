import React, { useEffect, useState } from 'react';
import { Sidebar, ActiveTab } from './components/Sidebar';
import { Navbar } from './components/Navbar';
import { IngestModal } from './components/IngestModal';
import { ErrorBoundary } from './components/ErrorBoundary';
import { QueueDashboard } from './views/QueueDashboard';
import { InvestigationView } from './views/InvestigationView';
import { CampaignGraphView } from './views/CampaignGraphView';
import { CaseManagementView } from './views/CaseManagementView';
import { ReportsView } from './views/ReportsView';
import { ModelEvaluationView } from './views/ModelEvaluationView';
import { AdminLedgerView } from './views/AdminLedgerView';
import { api } from './api';
import { Message, DashboardSummary } from './types';
import './styles.css';

export const parseTabFromHash = (rawHash: string): ActiveTab => {
  const clean = (rawHash || '')
    .replace(/^#+/, '')
    .replace(/^\/+/, '')
    .replace(/\/+$/, '')
    .split('?')[0]
    .split('/')[0]
    .trim()
    .toLowerCase();

  switch (clean) {
    case 'cases':
    case 'case':
    case 'dossier':
    case 'dossiers':
      return 'cases';
    case 'campaigns':
    case 'campaign':
    case 'graph':
    case 'correlation':
      return 'campaigns';
    case 'reports':
    case 'report':
    case 'pdf':
      return 'reports';
    case 'investigate':
    case 'investigation':
    case 'inspect':
      return 'investigate';
    case 'evaluation':
    case 'eval':
    case 'model':
    case 'registry':
      return 'evaluation';
    case 'ledger':
    case 'evidence':
    case 'merkle':
      return 'ledger';
    case 'admin':
    case 'administration':
    case 'settings':
    case 'config':
      return 'admin';
    case 'queue':
    case 'triage':
    case 'inbox':
    case '':
    default:
      return 'queue';
  }
};

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<ActiveTab>(() =>
    parseTabFromHash(window.location.hash)
  );
  const [selectedMessageId, setSelectedMessageId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [ingestModalOpen, setIngestModalOpen] = useState<boolean>(false);

  useEffect(() => {
    bootstrapSession();

    const handleHashSync = () => {
      const targetTab = parseTabFromHash(window.location.hash);
      setActiveTab((prev) => (prev !== targetTab ? targetTab : prev));
    };

    window.addEventListener('hashchange', handleHashSync);
    window.addEventListener('popstate', handleHashSync);

    // Initial check to ensure hash is set if empty
    if (!window.location.hash) {
      window.location.hash = '#/queue';
    } else {
      handleHashSync();
    }

    return () => {
      window.removeEventListener('hashchange', handleHashSync);
      window.removeEventListener('popstate', handleHashSync);
    };
  }, []);

  const bootstrapSession = async () => {
    setLoading(true);
    try {
      if (!api.getToken()) {
        await api.login('admin@drishtimail.local', 'ChangeMe!2026').catch(() => {
          // fallback token if login fails
        });
      }
      await refreshData();
    } catch (err) {
      console.error('Session bootstrap error:', err);
    } finally {
      setLoading(false);
    }
  };

  const refreshData = async () => {
    try {
      const [sum, msgs] = await Promise.all([
        api.getSummary().catch(() => null),
        api.getMessages().catch(() => []),
      ]);
      if (sum) setSummary(sum);
      setMessages(Array.isArray(msgs) ? msgs : []);
    } catch (err) {
      console.error('Refresh error:', err);
    }
  };

  const handleNavigate = (tab: ActiveTab) => {
    setActiveTab(tab);
    const targetHash = `#/${tab}`;
    if (window.location.hash !== targetHash) {
      window.location.hash = targetHash;
    }
  };

  const handleSelectMessage = (id: string) => {
    setSelectedMessageId(id);
    handleNavigate('investigate');
  };

  const handleIngestSuccess = async (newMessageId: string) => {
    await refreshData();
    setSelectedMessageId(newMessageId);
    handleNavigate('investigate');
  };

  const getTabTitle = () => {
    switch (activeTab) {
      case 'queue': return 'Investigation Queue';
      case 'investigate': return 'Investigation Deep Dive';
      case 'cases': return 'Forensic Case Management';
      case 'campaigns': return 'Campaign Correlation & Graph Intelligence';
      case 'reports': return 'Forensic Reports & BSA §63 Metadata';
      case 'evaluation': return 'ML Model Registry & Evaluation';
      case 'ledger': return 'Evidence Ledger & Cryptographic Verification';
      case 'admin': return 'Platform Security Administration';
    }
  };

  return (
    <div className="app-layout">
      <Sidebar
        activeTab={activeTab}
        onSelectTab={handleNavigate}
        selectedMessageId={selectedMessageId}
      />

      <div className="main-content">
        <Navbar
          activeTabTitle={getTabTitle()}
          onOpenIngest={() => setIngestModalOpen(true)}
          onRefresh={refreshData}
        />

        <main className="content-body">
          {activeTab === 'queue' && (
            <ErrorBoundary fallbackTitle="Investigation Queue Error" onReset={refreshData}>
              <QueueDashboard
                summary={summary}
                messages={messages}
                loading={loading}
                onSelectMessage={handleSelectMessage}
                onOpenIngest={() => setIngestModalOpen(true)}
                onRefresh={refreshData}
              />
            </ErrorBoundary>
          )}

          {activeTab === 'investigate' && (
            <ErrorBoundary fallbackTitle="Investigation Deep Dive Error">
              <InvestigationView
                messageId={selectedMessageId}
                onBackToQueue={() => handleNavigate('queue')}
                onSelectMessage={handleSelectMessage}
              />
            </ErrorBoundary>
          )}

          {activeTab === 'cases' && (
            <ErrorBoundary fallbackTitle="Cases View Error">
              <CaseManagementView onSelectMessage={handleSelectMessage} />
            </ErrorBoundary>
          )}

          {activeTab === 'campaigns' && (
            <ErrorBoundary fallbackTitle="Campaign Graph Error">
              <CampaignGraphView />
            </ErrorBoundary>
          )}

          {activeTab === 'reports' && (
            <ErrorBoundary fallbackTitle="Reports View Error">
              <ReportsView
                messages={messages}
                onSelectMessage={handleSelectMessage}
              />
            </ErrorBoundary>
          )}

          {activeTab === 'evaluation' && (
            <ErrorBoundary fallbackTitle="ML Model Validation Error">
              <ModelEvaluationView />
            </ErrorBoundary>
          )}

          {(activeTab === 'ledger' || activeTab === 'admin') && (
            <ErrorBoundary fallbackTitle="Admin & Ledger Error">
              <AdminLedgerView initialTab={activeTab === 'admin' ? 'config' : 'ledger'} />
            </ErrorBoundary>
          )}
        </main>
      </div>

      <IngestModal
        isOpen={ingestModalOpen}
        onClose={() => setIngestModalOpen(false)}
        onSuccess={handleIngestSuccess}
      />
    </div>
  );
};

export default App;
