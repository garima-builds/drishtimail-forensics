import React from "react";

export function ProductMockupCard({ label, caption, children, style, ...rest }) {
  return (
    <section style={{
      background: "var(--surface-dark)", borderRadius: "var(--radius-lg)", padding: "var(--space-xl)",
      display: "flex", flexDirection: "column", gap: "var(--space-lg)", ...style,
    }} {...rest}>
      {(label || caption) && (
        <header style={{ display: "flex", flexDirection: "column", gap: "var(--space-xs)" }}>
          {label && <span style={{ fontFamily: "var(--font-sans)", fontSize: "var(--title-md-size)", fontWeight: 500, color: "var(--text-on-dark)" }}>{label}</span>}
          {caption && <span style={{ fontFamily: "var(--font-sans)", fontSize: "var(--body-sm-size)", lineHeight: 1.55, color: "var(--text-on-dark-soft)" }}>{caption}</span>}
        </header>
      )}
      <div style={{ background: "var(--surface-dark-soft)", borderRadius: "var(--radius-md)", border: "1px solid var(--hairline-dark)", overflow: "hidden" }}>{children}</div>
    </section>
  );
}
