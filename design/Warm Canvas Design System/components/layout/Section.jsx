import React from "react";

export function Section({ children, tone = "canvas", pad = "section", maxWidth = "var(--container-max)", style, ...rest }) {
  const tones = {
    canvas: { background: "var(--canvas)", color: "var(--text-body)" },
    soft: { background: "var(--surface-soft)", color: "var(--text-body)" },
    cream: { background: "var(--surface-card)", color: "var(--text-body)" },
    creamStrong: { background: "var(--surface-cream-strong)", color: "var(--text-body)" },
    dark: { background: "var(--surface-dark)", color: "var(--text-on-dark-soft)" },
  };
  const pads = { section: "var(--space-section) var(--space-lg)", lg: "var(--space-xxl) var(--space-lg)", sm: "var(--space-xl) var(--space-lg)", none: "0" };
  return (
    <section style={{ ...tones[tone], padding: pads[pad] || pad, ...style }} {...rest}>
      <div style={{ maxWidth, margin: "0 auto" }}>{children}</div>
    </section>
  );
}
