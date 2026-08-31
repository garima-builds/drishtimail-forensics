import React from "react";

export function HeroIllustrationCard({ children, tone = "cream", caption, style, ...rest }) {
  const dark = tone === "dark";
  return (
    <div style={{
      background: dark ? "var(--surface-dark)" : "var(--canvas)",
      border: dark ? "1px solid transparent" : "1px solid var(--hairline)",
      borderRadius: "var(--radius-xl)", padding: "var(--space-lg)", minHeight: 320,
      display: "flex", flexDirection: "column", gap: "var(--space-sm)", justifyContent: "center", ...style,
    }} {...rest}>
      {children}
      {caption && <span style={{ fontFamily: "var(--font-sans)", fontSize: "var(--caption-size)", color: dark ? "var(--text-on-dark-soft)" : "var(--text-muted)" }}>{caption}</span>}
    </div>
  );
}
