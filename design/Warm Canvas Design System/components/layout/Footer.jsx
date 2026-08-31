import React from "react";
import { Wordmark } from "../brand/Wordmark.jsx";

export function Footer({ brand = "Anthropic", columns = [], legal = "© 2026 Anthropic PBC", meta = [], style, ...rest }) {
  return (
    <footer style={{ background: "var(--surface-dark)", color: "var(--text-on-dark-soft)", padding: "64px var(--space-lg)", ...style }} {...rest}>
      <div style={{ maxWidth: "var(--container-max)", margin: "0 auto", display: "flex", flexDirection: "column", gap: "var(--space-xxl)" }}>
        <Wordmark name={brand} tone="onDark" size={18} />
        <div style={{ display: "grid", gridTemplateColumns: "repeat(4, minmax(0, 1fr))", gap: "var(--space-xl)" }}>
          {columns.map((col) => (
            <div key={col.title} style={{ display: "flex", flexDirection: "column", gap: "var(--space-sm)" }}>
              <span style={{ fontFamily: "var(--font-sans)", fontSize: "var(--body-sm-size)", fontWeight: 500, color: "var(--text-on-dark)" }}>{col.title}</span>
              {col.links.map((l) => (
                <a key={l} href="#" style={{ fontFamily: "var(--font-sans)", fontSize: "var(--body-sm-size)", lineHeight: 1.55, color: "var(--text-on-dark-soft)", textDecoration: "none" }}>{l}</a>
              ))}
            </div>
          ))}
        </div>
        <div style={{ display: "flex", flexWrap: "wrap", gap: "var(--space-lg)", justifyContent: "space-between", borderTop: "1px solid var(--hairline-dark)", paddingTop: "var(--space-lg)" }}>
          <span style={{ fontFamily: "var(--font-sans)", fontSize: "var(--caption-size)", color: "var(--text-on-dark-soft)" }}>{legal}</span>
          <div style={{ display: "flex", gap: "var(--space-lg)" }}>
            {meta.map((m) => <a key={m} href="#" style={{ fontFamily: "var(--font-sans)", fontSize: "var(--caption-size)", color: "var(--text-on-dark-soft)", textDecoration: "none" }}>{m}</a>)}
          </div>
        </div>
      </div>
    </footer>
  );
}
