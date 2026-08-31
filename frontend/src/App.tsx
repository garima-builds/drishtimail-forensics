import { useEffect, useState } from 'react'

type Message = { id: string; sender: string; subject: string; received_at: string; verdict: string; score: number; confidence: string; status: string; summary: string }
type Summary = { total_messages: number; critical: number; high: number; elevated: number; new: number }
const api = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

const fallback: Message[] = [
  { id: 'demo-1', sender: 'accounts@micros0ft-support.example', subject: 'Action required: M365 account verification', received_at: new Date().toISOString(), verdict: 'Critical', score: 92, confidence: 'High', status: 'New', summary: 'Lookalike sender, DMARC misalignment, and a QR-originated redirect require review.' },
  { id: 'demo-2', sender: 'registrar@university.edu', subject: 'Updated academic calendar', received_at: new Date(Date.now() - 86400000).toISOString(), verdict: 'Low', score: 12, confidence: 'High', status: 'Closed', summary: 'Authenticated institutional sender with no material anomalies.' }
]

function App() {
  const [messages, setMessages] = useState<Message[]>(fallback)
  const [summary, setSummary] = useState<Summary>({ total_messages: 2, critical: 1, high: 0, elevated: 0, new: 1 })
  const [selected, setSelected] = useState<Message>(fallback[0])
  const [online, setOnline] = useState(false)
  const [token, setToken] = useState<string | null>(localStorage.getItem('drishtimail_token'))
  const [showLogin, setShowLogin] = useState(false)
  const [authError, setAuthError] = useState('')
  const [uploadState, setUploadState] = useState('')

  useEffect(() => { Promise.all([fetch(`${api}/messages`), fetch(`${api}/dashboard/summary`)]).then(async ([m, s]) => {
    if (!m.ok || !s.ok) throw new Error('API unavailable')
    const incoming = await m.json() as Message[]
    setMessages(incoming); setSelected(incoming[0] || fallback[0]); setSummary(await s.json()); setOnline(true)
  }).catch(() => setOnline(false)) }, [])

  async function login(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault(); setAuthError('')
    const form = new FormData(event.currentTarget)
    const response = await fetch(`${api}/auth/login`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ email: form.get('email'), password: form.get('password') }) })
    if (!response.ok) { setAuthError('Unable to sign in. Check your credentials.'); return }
    const result = await response.json() as { access_token: string }
    localStorage.setItem('drishtimail_token', result.access_token); setToken(result.access_token); setShowLogin(false)
  }

  async function upload(file: File) {
    if (!token) { setShowLogin(true); return }
    setUploadState('Preserving evidence…')
    const form = new FormData(); form.append('file', file)
    const response = await fetch(`${api}/ingest/upload`, { method: 'POST', headers: { Authorization: `Bearer ${token}` }, body: form })
    if (!response.ok) { setUploadState('Upload failed. Ensure the API and evidence store are running.'); return }
    const message = await response.json() as Message & { duplicate: boolean }
    setMessages(current => message.duplicate ? current : [message, ...current]); setSelected(message)
    setUploadState(message.duplicate ? 'This message was already preserved.' : 'Message preserved and added to the queue.')
  }

  async function analyzeSelected() {
    if (!token) { setShowLogin(true); return }
    if (selected.id.startsWith('demo-')) { setUploadState('Upload a preserved .eml message to run the forensic pipeline.'); return }
    setUploadState('Running offline forensic analysis…')
    const response = await fetch(`${api}/messages/${selected.id}/analyze`, { method: 'POST', headers: { Authorization: `Bearer ${token}` } })
    if (!response.ok) { setUploadState('Analysis failed. Check that the API is running.'); return }
    const result = await response.json() as { score: { value: number; verdict: string; confidence: string; disclaimer: string } }
    const updated = { ...selected, score: result.score.value, verdict: result.score.verdict, confidence: result.score.confidence, summary: result.score.disclaimer }
    setSelected(updated); setMessages(current => current.map(message => message.id === updated.id ? updated : message)); setUploadState('Analysis complete. The evidence-linked result is ready for review.')
  }

  return <div className="shell">
    <aside><div className="brand"><span>◈</span> DrishtiMail</div><p className="workspace">FORENSICS WORKSPACE</p>
      {['Investigation queue', 'Cases', 'Campaign graph', 'Reports', 'Administration'].map((item, i) => <button className={i === 0 ? 'nav active' : 'nav'} key={item}>{item}</button>)}
      <div className="evidence"><strong>Evidence integrity</strong><span>Ledger protected</span><small>Append-only audit trail</small></div>
    </aside>
    <main><header><div><p className="eyebrow">ANALYST QUEUE</p><h1>Prioritise what needs attention.</h1><p className="sub">Every conclusion is linked to preserved evidence.</p></div><div className="actions"><label className="upload">Preserve .eml<input type="file" accept=".eml,message/rfc822" onChange={event => { const file = event.target.files?.[0]; if (file) void upload(file); event.currentTarget.value = '' }} /></label><button className="signin" onClick={() => token ? (localStorage.removeItem('drishtimail_token'), setToken(null)) : setShowLogin(true)}>{token ? 'Sign out' : 'Sign in'}</button><div className={online ? 'status online' : 'status'}><i />{online ? 'API connected' : 'Demo data'}</div></div></header>
      {showLogin && <form className="login" onSubmit={login}><strong>Analyst sign in</strong><input name="email" type="email" defaultValue="admin@drishtimail.local" required /><input name="password" type="password" placeholder="Password" required /><button>Continue</button>{authError && <small>{authError}</small>}</form>}
      {uploadState && <p className="upload-state">{uploadState}</p>}
      <section className="metrics"><Metric value={summary.new} label="Awaiting review" /><Metric value={summary.critical} label="Critical verdicts" accent="danger" /><Metric value={summary.high + summary.elevated} label="Elevated risk" accent="warning" /><Metric value={summary.total_messages} label="Messages indexed" /></section>
      <div className="content"><section className="queue"><div className="section-title"><div><p className="eyebrow">INCOMING</p><h2>Message queue</h2></div><button className="filter">All verdicts ▾</button></div>
        <div className="table-head"><span>MESSAGE</span><span>VERDICT</span><span>SCORE</span><span>STATUS</span></div>
        {messages.map(m => <button className={selected.id === m.id ? 'message selected' : 'message'} key={m.id} onClick={() => setSelected(m)}><div><strong>{m.subject}</strong><span>{m.sender} · {new Date(m.received_at).toLocaleDateString()}</span></div><Verdict value={m.verdict} /><b>{m.score}</b><span className="new">{m.status}</span></button>)}</section>
        <aside className="detail"><p className="eyebrow">FORENSIC SNAPSHOT</p><h2>{selected.subject}</h2><p className="sender">From {selected.sender}</p><div className="score"><div><span>THREAT SCORE</span><strong>{selected.score}<small>/100</small></strong></div><Verdict value={selected.verdict} /></div><p className="summary">{selected.summary}</p><div className="finding"><span>AUTHENTICATION SEMANTICS</span><strong>Evidence needs review</strong><p>DMARC alignment does not establish message legitimacy when sender identity signals diverge.</p></div><div className="finding"><span>EVIDENCE REFERENCE</span><strong>Preserved and linked</strong><p>Every displayed finding is bound to a source byte range and the append-only ledger.</p></div><button className="open" onClick={() => void analyzeSelected()}>Run forensic analysis →</button></aside>
      </div></main>
  </div>
}

function Metric({ value, label, accent = '' }: { value: number; label: string; accent?: string }) { return <div className={`metric ${accent}`}><strong>{value}</strong><span>{label}</span></div> }
function Verdict({ value }: { value: string }) { return <span className={`verdict ${value.toLowerCase()}`}>{value}</span> }
export default App
