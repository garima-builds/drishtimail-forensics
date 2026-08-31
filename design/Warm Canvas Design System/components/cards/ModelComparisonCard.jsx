import React from "react";

export function ModelComparisonCard({ name, tagline, children, meta = [], link, badge, style, ...rest }) {
  return (
    <article style={{
      background: "var(--canvas)", border: "1px solid var(--hairline)", borderRadius: "var(--radius-lg)",
      padding: "var(--space-xl)", display: "flex", flexDirection: "column", gap: "var(--space-md)", ...style,
    }} {...rest}>
      <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: "var(--space-sm)" }}>
        <h3 style={{ fontFamily: "var(--font-display)", fontWeight: 400, fontSize: "var(--display-md-size)", lineHeight: "var(--display-md-lh)", letterSpacing: "var(--display-md-ls)", color: "var(--text-ink)", margin: 0 }}>{name}</h3>
        {badge}
      </div>
      {tagline && <p style={{ fontFamily: "var(--font-sans)", fontSize: "var(--title-sm-size)", fontWeight: 500, color: "var(--text-body-strong)", margin: 0 }}>{tagline}</p>}
      {children && <p style={{ fontFamily: "var(--font-sans)", fontSize: "var(--body-md-size)", lineHeight: "var(--body-md-lh)", color: "var(--text-body)", margin: 0, textWrap: "pretty" }}>{children}</p>}
      {meta.length > 0 && (
        <dl style={{ margin: 0, display: "flex", flexDirection: "column", gap: "var(--space-xs)", borderTop: "1px solid var(--hairline-soft)", paddingTop: "var(--space-md)" }}>
          {meta.map((row) => (
            <div key={row.label} style={{ display: "flex", justifyContent: "space-between", gap: "var(--space-md)" }}>
              <dt style={{ fontFamily: "var(--font-sans)", fontSize: "var(--body-sm-size)", color: "var(--text-muted)" }}>{row.label}</dt>
              <dd style={{ fontFamily: "var(--font-mono)", fontSize: "var(--body-sm-size)", color: "var(--text-ink)", margin: 0 }}>{row.value}</dd>
            </div>
          ))}
        </dl>
      )}
      {link && <div style={{ marginTop: "auto", paddingTop: "var(--space-xs)" }}>{link}</div>}
    </article>
  );
}
