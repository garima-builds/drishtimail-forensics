const { useState, useMemo } = React;
const N = window.WarmCanvasDesignSystem_d8b88e;
const { Section, CodeWindowCard, ProductMockupCard, FeatureCard, CategoryTabs, CtaBand, Button, Badge, TextLink } = N;

const SAMPLES = {
  Python: `from anthropic import Anthropic

client = Anthropic()
msg = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Summarise this diff"}],
)
print(msg.content[0].text)`,
  TypeScript: `import Anthropic from "@anthropic-ai/sdk"

const client = new Anthropic()
const msg = await client.messages.create({
  model: "claude-sonnet-4-5",
  max_tokens: 1024,
  messages: [{ role: "user", content: "Summarise this diff" }],
})
console.log(msg.content[0].text)`,
  cURL: `curl https://api.anthropic.com/v1/messages \\
  -H "x-api-key: $ANTHROPIC_API_KEY" \\
  -H "anthropic-version: 2023-06-01" \\
  -d '{"model":"claude-sonnet-4-5",
       "max_tokens":1024,
       "messages":[{"role":"user","content":"Hi"}]}'`,
};

function DevelopersPage() {
  const [lang, setLang] = useState("Python");
  return (
    <>
      <Section tone="canvas" pad="lg">
        <div style={{ display: "grid", gridTemplateColumns: "minmax(0, 5fr) minmax(0, 7fr)", gap: "var(--space-xxl)", alignItems: "center" }}>
          <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-md)", alignItems: "flex-start" }}>
            <Badge tone="coral">API</Badge>
            <h1 className="ds-display-lg">Three lines to your first response</h1>
            <p className="ds-body-md" style={{ fontSize: "var(--title-md-size)", color: "var(--text-body-strong)" }}>
              Same models, same tool use, same agent runtime the Claude apps are built on.
            </p>
            <div style={{ display: "flex", gap: "var(--space-sm)" }}>
              <Button>Get an API key</Button>
              <Button variant="secondary">Read the docs</Button>
            </div>
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-sm)" }}>
            <CategoryTabs tabs={Object.keys(SAMPLES)} value={lang} onChange={setLang} />
            <CodeWindowCard filename={lang === "Python" ? "quickstart.py" : lang === "TypeScript" ? "quickstart.ts" : "quickstart.sh"}
              code={SAMPLES[lang]} statusLeft="api reachable" statusRight="claude-sonnet-4-5"
              actions={<Button variant="secondaryOnDark">Copy</Button>} />
          </div>
        </div>
      </Section>

      <Section tone="dark">
        <div style={{ maxWidth: 640, marginBottom: "var(--space-xxl)" }}>
          <span className="ds-caption-upper" style={{ color: "var(--accent-amber)" }}>Agents</span>
          <h2 className="ds-display-lg" style={{ color: "var(--text-on-dark)", marginTop: "var(--space-sm)" }}>Long-running work, supervised</h2>
          <p className="ds-body-md" style={{ color: "var(--text-on-dark-soft)", marginTop: "var(--space-sm)" }}>
            Start a run, stream its steps, set a budget, stop it mid-flight. The runtime handles retries and tool permissions.
          </p>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "minmax(0, 1fr) minmax(0, 1fr)", gap: "var(--space-lg)" }}>
          <ProductMockupCard label="Run timeline" caption="fix-flaky-tests · acme/checkout">
            <div style={{ display: "flex", flexDirection: "column" }}>
              {[["Read repository", "14 files", "done"], ["Reproduce failure", "3 runs", "done"], ["Patch test harness", "2 files changed", "done"], ["Run test suite", "128 passing", "done"], ["Open pull request", "#4192", "active"]].map(([step, detail, state], i) => (
                <div key={step} style={{ display: "flex", alignItems: "center", gap: "var(--space-sm)", padding: "12px 16px", borderTop: i ? "1px solid var(--hairline-dark)" : "none" }}>
                  <span style={{ width: 8, height: 8, borderRadius: "50%", background: state === "active" ? "var(--accent-amber)" : "var(--accent-teal)", flexShrink: 0 }} />
                  <span style={{ fontFamily: "var(--font-sans)", fontSize: "var(--body-sm-size)", color: "var(--text-on-dark)", flex: 1 }}>{step}</span>
                  <span style={{ fontFamily: "var(--font-mono)", fontSize: "12px", color: "var(--text-on-dark-soft)" }}>{detail}</span>
                </div>
              ))}
            </div>
          </ProductMockupCard>
          <CodeWindowCard filename="run.ts" style={{ background: "var(--surface-dark-elevated)" }}
            code={`const run = await claude.agents.start("fix-flaky-tests", {\n  repo: "acme/checkout",\n  tools: ["shell", "git"],\n  budget: { minutes: 45 },\n})\n\nfor await (const step of run.stream()) {\n  logger.info(step.summary)\n}`}
            terminal={"$ npx claude run fix-flaky-tests\n→ 14 files read · 3 files changed\n→ 128 tests passing\n→ opened PR #4192 (12m 04s)"}
            statusLeft="agent finished" statusRight="45m budget · 12m used" />
        </div>
      </Section>

      <Section tone="canvas">
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3, minmax(0, 1fr))", gap: "var(--space-lg)" }}>
          <FeatureCard title="Tool use" footer={<TextLink>Tool use guide</TextLink>}>Declare a JSON schema and Claude calls your function — with parallel calls and structured results.</FeatureCard>
          <FeatureCard title="Batch and caching" footer={<TextLink>Pricing details</TextLink>}>Cache long prompts and submit batches for a fraction of the per-token cost.</FeatureCard>
          <FeatureCard title="MCP" footer={<TextLink>Build a server</TextLink>}>Expose your own systems through the Model Context Protocol and reuse them across apps.</FeatureCard>
        </div>
      </Section>

      <Section tone="canvas" pad="lg">
        <CtaBand tone="dark" title="Start with the quickstart" subtitle="Free keys, no card, rate limits that scale with usage."
          actions={<Button variant="secondaryOnDark">Open the docs</Button>}
          aside={<CodeWindowCard filename="install.sh" code={"pip install anthropic\nexport ANTHROPIC_API_KEY=sk-ant-…"} showLineNumbers={false} style={{ background: "var(--surface-dark-elevated)" }} />} />
      </Section>
    </>
  );
}
Object.assign(window, { DevelopersPage });
