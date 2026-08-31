import React from "react";
import { Button } from "../buttons/Button.jsx";

export function PricingTierCard({ name, price, cadence, blurb, features = [], ctaLabel = "Get started", featured = false, badge, onCta, style, ...rest }) {
  const fg = featured ? "var(--text-on-dark)" : "var(--text-ink)";
  const body = featured ? "var(--text-on-dark-soft)" : "var(--text-body)";
  return (
    <article style={{
      background: featured ? "var(--surface-dark)" : "var(--canvas)",
      border: featured ? "1px solid transparent" : "1px solid var(--hairline)",
      borderRadius: "var(--radius-lg)", padding: "var(--space-xl)",
      display: "flex", flexDirection: "column", gap: "var(--space-md)", ...style,
    }} {...rest}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: "var(--space-sm)" }}>
        <h4 style={{ fontFamily: "var(--font-sans)", fontSize: "var(--title-lg-size)", lineHeight: "var(--title-lg-lh)", fontWeight: 500, color: fg }}>{name}</h4>
        {badge}
      </div>
      <div style={{ display: "flex", alignItems: "baseline", gap: "8px" }}>
        <span style={{ fontFamily: "var(--font-display)", fontWeight: 400, fontSize: "var(--display-sm-size)", lineHeight: "var(--display-sm-lh)", letterSpacing: "var(--display-sm-ls)", color: fg }}>{price}</span>
        {cadence && <span style={{ fontFamily: "var(--font-sans)", fontSize: "var(--body-sm-size)", color: featured ? "var(--text-on-dark-soft)" : "var(--text-muted)" }}>{cadence}</span>}
      </div>
      {blurb && <p style={{ fontFamily: "var(--font-sans)", fontSize: "var(--body-sm-size)", lineHeight: 1.55, color: body, margin: 0 }}>{blurb}</p>}
      <Button variant={featured ? "secondaryOnDark" : "primary"} fullWidth onClick={onCta} style={{ marginTop: "var(--space-xs)" }}>{ctaLabel}</Button>
      <ul style={{
        listStyle: "none", margin: "var(--space-xs) 0 0", padding: "var(--space-md) 0 0",
        borderTop: `1px solid ${featured ? "var(--hairline-dark)" : "var(--hairline-soft)"}`,
        display: "flex", flexDirection: "column", gap: "var(--space-sm)",
      }}>
        {features.map((f) => (
          <li key={f} style={{ display: "flex", gap: "var(--space-sm)", fontFamily: "var(--font-sans)", fontSize: "var(--body-md-size)", lineHeight: 1.45, color: body }}>
            <span aria-hidden="true" style={{ color: featured ? "var(--accent-teal)" : "var(--primary)", flexShrink: 0 }}>—</span>{f}
          </li>
        ))}
      </ul>
    </article>
  );
}
