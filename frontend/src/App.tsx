import React, { useEffect, useState } from 'react';
import { Sidebar, ActiveTab } from './components/Sidebar';
import { Navbar } from './components/Navbar';
import { IngestModal } from './components/IngestModal';
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

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<ActiveTab>('queue');
  const [selectedMessageId, setSelectedMessageId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [ingestModalOpen, setIngestModalOpen] = useState<boolean>(false);

  useEffect(() => {
    bootstrapSession();
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
      setMessages(msgs);
    } catch (err) {
      console.error('Refresh error:', err);
    }
  };

  const handleSelectMessage = (id: string) => {
    setSelectedMessageId(id);
    setActiveTab('investigate');
  };

  const handleIngestSuccess = async (newMessageId: string) => {
    await refreshData();
    setSelectedMessageId(newMessageId);
    setActiveTab('investigate');
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
        onSelectTab={(tab) => setActiveTab(tab)}
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
            <QueueDashboard
              summary={summary}
              messages={messages}
              loading={loading}
              onSelectMessage={handleSelectMessage}
              onOpenIngest={() => setIngestModalOpen(true)}
              onRefresh={refreshData}
            />
          )}

          {activeTab === 'investigate' && (
            <InvestigationView
              messageId={selectedMessageId}
              onBackToQueue={() => setActiveTab('queue')}
              onSelectMessage={handleSelectMessage}
            />
          )}

          {activeTab === 'cases' && (
            <CaseManagementView onSelectMessage={handleSelectMessage} />
          )}

          {activeTab === 'campaigns' && <CampaignGraphView />}

          {activeTab === 'reports' && (
            <ReportsView
              messages={messages}
              onSelectMessage={handleSelectMessage}
            />
          )}

          {activeTab === 'evaluation' && <ModelEvaluationView />}

          {(activeTab === 'ledger' || activeTab === 'admin') && <AdminLedgerView />}
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
