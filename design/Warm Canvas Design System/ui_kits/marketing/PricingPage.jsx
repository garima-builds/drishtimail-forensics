const { useState, useMemo } = React;
const N = window.WarmCanvasDesignSystem_d8b88e;
const { Section, PricingTierCard, CategoryTabs, Badge, TextInput, Button, CtaBand, FeatureCard } = N;

const TIERS = {
  Individual: [
    { name: "Free", price: "$0", cadence: "forever", blurb: "Try Claude in the web app.", features: ["Chat on web, iOS and Android", "Ask about attached files", "Standard usage limits"], cta: "Start free" },
    { name: "Pro", price: "$20", cadence: "/ month", blurb: "For daily, serious use.", features: ["5× the usage of Free", "Access to Opus", "Projects and connectors", "Claude Code in the terminal"], cta: "Get Pro", featured: true, badge: <Badge tone="coral">Popular</Badge> },
    { name: "Max", price: "$100", cadence: "/ month", blurb: "For heavy agent workloads.", features: ["20× the usage of Pro", "Priority capacity", "Longer agent budgets"], cta: "Get Max" },
  ],
  Teams: [
    { name: "Team", price: "$30", cadence: "/ person / mo", blurb: "For teams standardising on Claude.", features: ["Everything in Pro", "Central billing and admin", "Shared projects", "Minimum 5 seats"], cta: "Start a trial", featured: true },
    { name: "Enterprise", price: "Custom", cadence: "", blurb: "For organisations with review requirements.", features: ["SSO and SCIM", "Audit logs and data controls", "Expanded context windows", "Dedicated support"], cta: "Contact sales" },
    { name: "API", price: "Usage", cadence: "per million tokens", blurb: "Build Claude into your product.", features: ["Opus, Sonnet and Haiku", "Batch and streaming", "Tool use and agents", "Volume discounts"], cta: "Get an API key" },
  ],
};

function PricingPage() {
  const [audience, setAudience] = useState("Individual");
  const tiers = TIERS[audience];
  return (
    <>
      <Section tone="canvas" pad="lg">
        <div style={{ maxWidth: 680, display: "flex", flexDirection: "column", gap: "var(--space-md)" }}>
          <span className="ds-caption-upper" style={{ color: "var(--text-muted)" }}>Pricing</span>
          <h1 className="ds-display-lg">Pick a plan that matches how much you think</h1>
          <p className="ds-body-md" style={{ fontSize: "var(--title-md-size)", color: "var(--text-body-strong)" }}>Every plan includes the full model family. What changes is how much you can use it.</p>
        </div>
        <div style={{ marginTop: "var(--space-xl)" }}>
          <CategoryTabs tabs={Object.keys(TIERS)} value={audience} onChange={setAudience} />
        </div>
        <div style={{ display: "grid", gridTemplateColumns: `repeat(${tiers.length}, minmax(0, 1fr))`, gap: "var(--space-lg)", marginTop: "var(--space-lg)", alignItems: "start" }}>
          {tiers.map((t) => (
            <PricingTierCard key={t.name} name={t.name} price={t.price} cadence={t.cadence} blurb={t.blurb}
              features={t.features} ctaLabel={t.cta} featured={t.featured} badge={t.badge} />
          ))}
        </div>
      </Section>

      <Section tone="cream">
        <div style={{ display: "grid", gridTemplateColumns: "minmax(0, 5fr) minmax(0, 7fr)", gap: "var(--space-xxl)", alignItems: "start" }}>
          <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-md)" }}>
            <h2 className="ds-display-md">Not sure which plan fits?</h2>
            <p className="ds-body-md">Tell us how your team works and we'll come back with a recommendation — usually within a day.</p>
            <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-sm)", maxWidth: 360, marginTop: "var(--space-xs)" }}>
              <TextInput label="Work email" placeholder="you@company.com" />
              <TextInput label="Team size" placeholder="e.g. 40" hint="Rough is fine." />
              <Button style={{ alignSelf: "flex-start", marginTop: "var(--space-xs)" }}>Request a recommendation</Button>
            </div>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "var(--space-md)" }}>
            <FeatureCard title="Usage, explained" style={{ background: "var(--canvas)", border: "1px solid var(--hairline)" }}>Limits are measured in messages and agent minutes, not tokens. The plan page shows your current draw.</FeatureCard>
            <FeatureCard title="Switch any time" style={{ background: "var(--canvas)", border: "1px solid var(--hairline)" }}>Upgrades apply immediately and prorate. Downgrades take effect at the end of the period.</FeatureCard>
            <FeatureCard title="Your data" style={{ background: "var(--canvas)", border: "1px solid var(--hairline)" }}>Business plans exclude your content from model training by default. No setting to remember.</FeatureCard>
            <FeatureCard title="Education and non-profit" style={{ background: "var(--canvas)", border: "1px solid var(--hairline)" }}>Discounted seats are available for accredited institutions and registered charities.</FeatureCard>
          </div>
        </div>
      </Section>

      <Section tone="canvas" pad="lg">
        <CtaBand tone="dark" title="Ready to build on the API?" subtitle="Keys are free to create; you only pay for what you use."
          actions={<Button variant="secondaryOnDark">Get an API key</Button>} />
      </Section>
    </>
  );
}
Object.assign(window, { PricingPage });
