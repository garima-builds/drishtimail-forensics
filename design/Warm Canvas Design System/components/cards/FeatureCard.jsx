import React from "react";

export function FeatureCard({ title, children, icon, eyebrow, tone = "cream", footer, style, ...rest }) {
  const dark = tone === "dark";
  return (
    <article style={{
      display: "flex", flexDirection: "column", gap: "var(--space-sm)",
      background: dark ? "var(--surface-dark)" : "var(--surface-card)",
      color: dark ? "var(--text-on-dark-soft)" : "var(--text-body)",
      borderRadius: "var(--radius-lg)", padding: "var(--space-xl)", ...style,
    }} {...rest}>
      {icon && <div style={{ marginBottom: "var(--space-xs)", color: dark ? "var(--text-on-dark)" : "var(--text-ink)", display: "flex" }}>{icon}</div>}
      {eyebrow && <span className="ds-caption-upper" style={{ color: dark ? "var(--accent-amber)" : "var(--text-muted)" }}>{eyebrow}</span>}
      <h4 style={{ fontFamily: "var(--font-sans)", fontSize: "var(--title-md-size)", lineHeight: "var(--title-md-lh)", fontWeight: 500, color: dark ? "var(--text-on-dark)" : "var(--text-ink)" }}>{title}</h4>
      <p style={{ fontFamily: "var(--font-sans)", fontSize: "var(--body-md-size)", lineHeight: "var(--body-md-lh)", margin: 0, textWrap: "pretty" }}>{children}</p>
      {footer && <div style={{ marginTop: "var(--space-md)" }}>{footer}</div>}
    </article>
  );
}
