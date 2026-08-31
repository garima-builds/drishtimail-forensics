import React from "react";

/**
 * Text-only wordmark. No logo asset was supplied with this system, so the brand
 * name is set in the display serif — never redraw a mark from memory.
 */
export function Wordmark({ name = "Claude", tone = "ink", size = 20, style, ...rest }) {
  const color = tone === "onDark" ? "var(--text-on-dark)" : "var(--text-ink)";
  return (
    <span style={{
      display: "inline-flex", alignItems: "baseline", gap: "8px",
      fontFamily: "var(--font-display)", fontWeight: 500, fontSize: size,
      letterSpacing: "-0.4px", color, ...style,
    }} {...rest}>{name}</span>
  );
}
