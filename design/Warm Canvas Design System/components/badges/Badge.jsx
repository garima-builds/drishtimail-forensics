import React from "react";

export function Badge({ children, tone = "cream", style, ...rest }) {
  const tones = {
    cream: { background: "var(--surface-card)", color: "var(--text-ink)", font: "caption" },
    coral: { background: "var(--primary)", color: "var(--on-primary)", font: "upper" },
    amber: { background: "var(--accent-amber)", color: "var(--text-ink)", font: "upper" },
    teal: { background: "var(--accent-teal)", color: "var(--text-ink)", font: "upper" },
    outline: { background: "transparent", color: "var(--text-muted)", font: "caption", border: "1px solid var(--hairline)" },
    onDark: { background: "var(--surface-dark-elevated)", color: "var(--text-on-dark)", font: "caption" },
  };
  const t = tones[tone] || tones.cream;
  const upper = t.font === "upper";
  return (
    <span style={{
      display: "inline-flex", alignItems: "center", gap: "6px", padding: "4px 12px",
      borderRadius: "var(--radius-pill)", background: t.background, color: t.color, border: t.border || "1px solid transparent",
      fontFamily: "var(--font-sans)", fontWeight: 500, lineHeight: 1.4,
      fontSize: upper ? "var(--caption-upper-size)" : "var(--caption-size)",
      letterSpacing: upper ? "var(--caption-upper-ls)" : 0,
      textTransform: upper ? "uppercase" : "none", ...style,
    }} {...rest}>{children}</span>
  );
}
