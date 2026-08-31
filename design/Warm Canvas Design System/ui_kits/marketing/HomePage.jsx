const { useState, useMemo } = React;
const N = window.WarmCanvasDesignSystem_d8b88e;
const { HeroBand, HeroIllustrationCard, Section, FeatureCard, ModelComparisonCard, CtaBand, CodeWindowCard, Button, Badge, TextLink, ConnectorTile } = N;

const heroCode = `from anthropic import Anthropic

client = Anthropic()
run = client.agents.start(
    "review-pull-request",
    repo="acme/checkout",
)
for step in run.stream():
    print(step.summary)`;

function HomePage({ onNavigate }) {
  return (
    <>
      <HeroBand
        eyebrow={<Badge tone="coral">Claude Sonnet 4.5</Badge>}
        title="Meet your thinking partner"
        subtitle="Claude helps your team reason through the work that actually matters — research, code, analysis, and the messy problems in between."
        note="No credit card required."
        actions={<><Button onClick={() => onNavigate && onNavigate("Pricing")}>Try Claude</Button><Button variant="secondary">Talk to sales</Button></>}
        artifact={
          <HeroIllustrationCard tone="dark" caption="Agent run · acme/checkout">
            <CodeWindowCard filename="review.py" code={heroCode} statusLeft="connected" statusRight="claude-sonnet-4-5" style={{ padding: 0, background: "transparent" }} />
          </HeroIllustrationCard>
        }
      />

      <Section tone="cream">
        <div style={{ maxWidth: 620, marginBottom: "var(--space-xxl)" }}>
          <span className="ds-caption-upper" style={{ color: "var(--text-muted)" }}>Why Claude</span>
          <h2 className="ds-display-lg" style={{ marginTop: "var(--space-sm)" }}>Built for the work that takes real thought</h2>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3, minmax(0, 1fr))", gap: "var(--space-lg)" }}>
          <FeatureCard title="Connect your tools" tone="cream" style={{ background: "var(--canvas)", border: "1px solid var(--hairline)" }} footer={<TextLink>Browse connectors</TextLink>}>
            Claude reads the systems your team already works in — drives, wikis, tickets, repos — with permissions intact.
          </FeatureCard>
          <FeatureCard title="Think, then answer" tone="cream" style={{ background: "var(--canvas)", border: "1px solid var(--hairline)" }} footer={<TextLink>How extended thinking works</TextLink>}>
            Extended thinking works a problem through step by step and hands back the reasoning alongside the answer.
          </FeatureCard>
          <FeatureCard title="Work that runs itself" tone="cream" style={{ background: "var(--canvas)", border: "1px solid var(--hairline)" }} footer={<TextLink>See agent examples</TextLink>}>
            Give Claude a goal and the tools to reach it. Agents run for hours, check their work, and report back.
          </FeatureCard>
        </div>
      </Section>

      <Section tone="dark">
        <div style={{ display: "grid", gridTemplateColumns: "minmax(0, 5fr) minmax(0, 7fr)", gap: "var(--space-xxl)", alignItems: "center" }}>
          <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-md)", alignItems: "flex-start" }}>
            <Badge tone="onDark">Claude Code</Badge>
            <h2 className="ds-display-lg" style={{ color: "var(--text-on-dark)" }}>It ships code, not suggestions</h2>
            <p className="ds-body-md" style={{ color: "var(--text-on-dark-soft)", maxWidth: "42ch" }}>
              Claude works in your terminal and your repo: reads the codebase, writes the change, runs the tests, opens the pull request.
            </p>
            <Button variant="secondaryOnDark">Read the docs</Button>
          </div>
          <CodeWindowCard
            filename="agent.ts"
            style={{ background: "var(--surface-dark-elevated)" }}
            code={`const run = await claude.agents.start("fix-flaky-tests", {\n  repo: "acme/checkout",\n  budget: { minutes: 45 },\n})\n\nawait run.wait()\nconsole.log(run.pullRequest.url)`}
            terminal={"$ npx claude run fix-flaky-tests\n→ 14 files read · 3 files changed\n→ 128 tests passing\n→ opened PR #4192"}
            statusLeft="agent finished" statusRight="45m budget · 12m used"
          />
        </div>
      </Section>

      <Section tone="canvas">
        <div style={{ display: "flex", alignItems: "flex-end", justifyContent: "space-between", gap: "var(--space-lg)", marginBottom: "var(--space-xxl)" }}>
          <h2 className="ds-display-lg" style={{ maxWidth: "20ch" }}>Which problem are you up against?</h2>
          <TextLink>Compare all models</TextLink>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3, minmax(0, 1fr))", gap: "var(--space-lg)" }}>
          <ModelComparisonCard name="Opus" tagline="The hardest problems" badge={<Badge tone="coral">New</Badge>}
            meta={[{ label: "Context", value: "200K" }, { label: "Best for", value: "research" }]}
            link={<TextLink>Read the model guide</TextLink>}>
            Deep reasoning over long documents and multi-step agent runs where getting it right matters more than speed.
          </ModelComparisonCard>
          <ModelComparisonCard name="Sonnet" tagline="Everyday work, at pace"
            meta={[{ label: "Context", value: "200K" }, { label: "Best for", value: "coding" }]}
            link={<TextLink>Read the model guide</TextLink>}>
            The default for product work — fast enough to sit inside a loop, strong enough to trust with a codebase.
          </ModelComparisonCard>
          <ModelComparisonCard name="Haiku" tagline="Volume and latency"
            meta={[{ label: "Context", value: "200K" }, { label: "Best for", value: "classify" }]}
            link={<TextLink>Read the model guide</TextLink>}>
            Near-instant responses for classification, extraction and the high-throughput edges of a pipeline.
          </ModelComparisonCard>
        </div>
      </Section>

      <Section tone="soft">
        <div style={{ display: "flex", alignItems: "flex-end", justifyContent: "space-between", gap: "var(--space-lg)", marginBottom: "var(--space-xl)" }}>
          <div>
            <span className="ds-caption-upper" style={{ color: "var(--text-muted)" }}>Connectors</span>
            <h2 className="ds-display-md" style={{ marginTop: "var(--space-sm)" }}>Bring your context with you</h2>
          </div>
          <TextLink>View the directory</TextLink>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(4, minmax(0, 1fr))", gap: "var(--space-md)" }}>
          <ConnectorTile name="Drive" status="connected">Search and cite documents.</ConnectorTile>
          <ConnectorTile name="Jira" status="connected">Read tickets and sprints.</ConnectorTile>
          <ConnectorTile name="GitHub">Repos, issues, pull requests.</ConnectorTile>
          <ConnectorTile name="Snowflake">Query warehouse tables.</ConnectorTile>
        </div>
      </Section>

      <Section tone="canvas" pad="lg">
        <CtaBand tone="coral" title="Start with Claude today" subtitle="Free to try. Bring your team when you're ready."
          actions={<><Button variant="onCoral" onClick={() => onNavigate && onNavigate("Pricing")}>See pricing</Button><Button variant="textOnDark" style={{ color: "var(--on-primary)" }}>Talk to sales</Button></>} />
      </Section>
    </>
  );
}
Object.assign(window, { HomePage });
