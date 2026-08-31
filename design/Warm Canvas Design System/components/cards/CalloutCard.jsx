import React from "react";

export function CalloutCard({ title, children, actions, align = "left", style, ...rest }) {
  return (
    <section style={{
      background: "var(--primary)", color: "var(--on-primary)", borderRadius: "var(--radius-lg)",
      padding: "var(--space-xxl)", display: "flex", flexDirection: "column",
      alignItems: align === "center" ? "center" : "flex-start", textAlign: align,
      gap: "var(--space-md)", ...style,
    }} {...rest}>
      {title && <h3 style={{ fontFamily: "var(--font-display)", fontWeight: 400, fontSize: "var(--display-sm-size)", lineHeight: "var(--display-sm-lh)", letterSpacing: "var(--display-sm-ls)", color: "var(--on-primary)", margin: 0, maxWidth: "24ch" }}>{title}</h3>}
      {children && <p style={{ fontFamily: "var(--font-sans)", fontSize: "var(--title-md-size)", lineHeight: 1.5, color: "rgba(255,255,255,0.88)", margin: 0, maxWidth: "52ch" }}>{children}</p>}
      {actions && <div style={{ display: "flex", gap: "var(--space-sm)", marginTop: "var(--space-xs)" }}>{actions}</div>}
    </section>
  );
}
