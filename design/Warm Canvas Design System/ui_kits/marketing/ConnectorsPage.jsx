const { useState, useMemo } = React;
const N = window.WarmCanvasDesignSystem_d8b88e;
const { Section, CategoryTabs, ConnectorTile, TextInput, Badge, CtaBand, Button, TextLink } = N;

const ALL = [
  { name: "Google Drive", cat: "Files", desc: "Search and cite documents.", status: "connected" },
  { name: "Notion", cat: "Files", desc: "Read pages and databases.", status: "connected" },
  { name: "Dropbox", cat: "Files", desc: "Open shared folders." },
  { name: "GitHub", cat: "Developer", desc: "Repos, issues, pull requests.", status: "connected" },
  { name: "Sentry", cat: "Developer", desc: "Triage errors in context." },
  { name: "Linear", cat: "Developer", desc: "Read and file issues." },
  { name: "Jira", cat: "Work", desc: "Tickets, sprints, epics.", status: "connected" },
  { name: "Slack", cat: "Work", desc: "Summarise channels and threads." },
  { name: "Asana", cat: "Work", desc: "Track project status." },
  { name: "Snowflake", cat: "Data", desc: "Query warehouse tables." },
  { name: "BigQuery", cat: "Data", desc: "Run read-only analysis." },
  { name: "Stripe", cat: "Data", desc: "Look up customers and invoices." },
];
const CATS = ["All", "Files", "Developer", "Work", "Data"];

function ConnectorsPage() {
  const [cat, setCat] = useState("All");
  const [q, setQ] = useState("");
  const tiles = useMemo(() => ALL.filter((t) =>
    (cat === "All" || t.cat === cat) && t.name.toLowerCase().includes(q.toLowerCase())), [cat, q]);

  return (
    <>
      <Section tone="canvas" pad="lg">
        <div style={{ maxWidth: 660, display: "flex", flexDirection: "column", gap: "var(--space-md)" }}>
          <Badge tone="cream">Directory</Badge>
          <h1 className="ds-display-lg">Connectors</h1>
          <p className="ds-body-md" style={{ fontSize: "var(--title-md-size)", color: "var(--text-body-strong)" }}>
            Give Claude read access to the places your work already lives. Every connector honours the permissions you already have.
          </p>
        </div>
        <div style={{ display: "flex", alignItems: "flex-end", justifyContent: "space-between", gap: "var(--space-lg)", marginTop: "var(--space-xl)", flexWrap: "wrap" }}>
          <CategoryTabs tabs={CATS} value={cat} onChange={setCat} />
          <TextInput placeholder="Search connectors" value={q} onChange={(e) => setQ(e.target.value)} fullWidth={false} style={{ width: 260 }} />
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(4, minmax(0, 1fr))", gap: "var(--space-md)", marginTop: "var(--space-lg)" }}>
          {tiles.map((t) => <ConnectorTile key={t.name} name={t.name} status={t.status}>{t.desc}</ConnectorTile>)}
        </div>
        {tiles.length === 0 && (
          <p className="ds-body-md" style={{ marginTop: "var(--space-xl)", color: "var(--text-muted)" }}>
            Nothing matches “{q}”. <TextLink onClick={() => setQ("")}>Clear the search</TextLink>.
          </p>
        )}
      </Section>

      <Section tone="cream" pad="lg">
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: "var(--space-xl)", flexWrap: "wrap" }}>
          <div style={{ maxWidth: "48ch", display: "flex", flexDirection: "column", gap: "var(--space-sm)" }}>
            <h2 className="ds-display-sm">Missing something your team uses?</h2>
            <p className="ds-body-md">Any service with an MCP server works today. Build one in an afternoon, or ask us to prioritise it.</p>
          </div>
          <div style={{ display: "flex", gap: "var(--space-sm)" }}>
            <Button>Build a connector</Button>
            <Button variant="secondary">Request one</Button>
          </div>
        </div>
      </Section>

      <Section tone="canvas" pad="lg">
        <CtaBand tone="coral" title="Bring your context with you" subtitle="Connect a tool in under a minute."
          actions={<Button variant="onCoral">Open Claude</Button>} />
      </Section>
    </>
  );
}
Object.assign(window, { ConnectorsPage });
