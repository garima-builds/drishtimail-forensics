import React from "react";

export function ConnectorTile({ name, children, logo, status, style, ...rest }) {
  return (
    <a href="#" style={{
      background: "var(--canvas)", border: "1px solid var(--hairline)", borderRadius: "var(--radius-lg)",
      padding: "20px", display: "flex", flexDirection: "column", gap: "var(--space-sm)",
      textDecoration: "none", color: "inherit", ...style,
    }} {...rest}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: "var(--space-sm)" }}>
        <span style={{
          width: 36, height: 36, borderRadius: "var(--radius-md)", background: "var(--surface-card)",
          display: "inline-flex", alignItems: "center", justifyContent: "center", color: "var(--text-ink)",
          fontFamily: "var(--font-sans)", fontSize: "var(--body-sm-size)", fontWeight: 500, overflow: "hidden",
        }}>{logo || (name ? name.slice(0, 1) : "")}</span>
        {status === "connected" && <span style={{ width: 8, height: 8, borderRadius: "50%", background: "var(--accent-teal)" }} title="Connected" />}
      </div>
      <span style={{ fontFamily: "var(--font-sans)", fontSize: "var(--title-sm-size)", lineHeight: "var(--title-sm-lh)", fontWeight: 500, color: "var(--text-ink)" }}>{name}</span>
      <span style={{ fontFamily: "var(--font-sans)", fontSize: "var(--body-sm-size)", lineHeight: 1.5, color: "var(--text-muted)" }}>{children}</span>
    </a>
  );
}
