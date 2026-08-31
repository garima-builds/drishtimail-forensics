import React from "react";

export function CtaBand({ tone = "coral", title, subtitle, actions, aside, style, ...rest }) {
  const coral = tone === "coral";
  return (
    <section style={{
      background: coral ? "var(--primary)" : "var(--surface-dark)",
      borderRadius: "var(--radius-lg)", padding: "64px",
      display: "grid", gridTemplateColumns: aside ? "minmax(0, 1fr) minmax(0, 1fr)" : "minmax(0, 1fr)",
      gap: "var(--space-xxl)", alignItems: "center", ...style,
    }} {...rest}>
      <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-md)", alignItems: "flex-start" }}>
        <h2 style={{
          fontFamily: "var(--font-display)", fontWeight: 400, fontSize: "var(--display-sm-size)",
          lineHeight: "var(--display-sm-lh)", letterSpacing: "var(--display-sm-ls)",
          color: coral ? "var(--on-primary)" : "var(--text-on-dark)", margin: 0, maxWidth: "26ch",
        }}>{title}</h2>
        {subtitle && <p style={{ fontFamily: "var(--font-sans)", fontSize: "var(--body-md-size)", lineHeight: 1.55, color: coral ? "rgba(255,255,255,0.85)" : "var(--text-on-dark-soft)", margin: 0, maxWidth: "50ch" }}>{subtitle}</p>}
        {actions && <div style={{ display: "flex", flexWrap: "wrap", gap: "var(--space-sm)", marginTop: "var(--space-xs)" }}>{actions}</div>}
      </div>
      {aside && <div style={{ minWidth: 0 }}>{aside}</div>}
    </section>
  );
}
