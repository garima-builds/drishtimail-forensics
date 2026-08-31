import React from "react";

export function HeroBand({ eyebrow, title, subtitle, actions, note, artifact, style, ...rest }) {
  return (
    <section style={{ background: "var(--canvas)", padding: "var(--space-section) var(--space-lg)", ...style }} {...rest}>
      <div style={{
        maxWidth: "var(--container-max)", margin: "0 auto", display: "grid",
        gridTemplateColumns: artifact ? "minmax(0, 1fr) minmax(0, 1fr)" : "minmax(0, 720px)",
        gap: "var(--space-xxl)", alignItems: "center",
      }}>
        <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-lg)" }}>
          {eyebrow && <div>{eyebrow}</div>}
          <h1 style={{
            fontFamily: "var(--font-display)", fontWeight: 400, fontSize: "var(--display-xl-size)",
            lineHeight: "var(--display-xl-lh)", letterSpacing: "var(--display-xl-ls)",
            color: "var(--text-ink)", margin: 0, textWrap: "pretty",
          }}>{title}</h1>
          {subtitle && <p style={{ fontFamily: "var(--font-sans)", fontSize: "var(--title-md-size)", lineHeight: 1.5, color: "var(--text-body-strong)", margin: 0, maxWidth: "44ch", textWrap: "pretty" }}>{subtitle}</p>}
          {actions && <div style={{ display: "flex", flexWrap: "wrap", gap: "var(--space-sm)", marginTop: "var(--space-xs)" }}>{actions}</div>}
          {note && <span style={{ fontFamily: "var(--font-sans)", fontSize: "var(--caption-size)", color: "var(--text-muted-soft)" }}>{note}</span>}
        </div>
        {artifact && <div style={{ minWidth: 0 }}>{artifact}</div>}
      </div>
    </section>
  );
}
