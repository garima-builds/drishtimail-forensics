import React from "react";
import { Button } from "../buttons/Button.jsx";

export function CookieConsentCard({ title = "Cookies", children, acceptLabel = "Accept all", rejectLabel = "Reject all", onAccept, onReject, style, ...rest }) {
  return (
    <aside style={{
      background: "var(--surface-dark)", borderRadius: "var(--radius-lg)", padding: "var(--space-lg)",
      maxWidth: 380, display: "flex", flexDirection: "column", gap: "var(--space-sm)", ...style,
    }} {...rest}>
      {title && <span style={{ fontFamily: "var(--font-sans)", fontSize: "var(--title-sm-size)", fontWeight: 500, color: "var(--text-on-dark)" }}>{title}</span>}
      <p style={{ fontFamily: "var(--font-sans)", fontSize: "var(--body-sm-size)", lineHeight: 1.55, color: "var(--text-on-dark-soft)", margin: 0 }}>{children}</p>
      <div style={{ display: "flex", gap: "var(--space-xs)", marginTop: "var(--space-xs)" }}>
        <Button variant="secondaryOnDark" onClick={onAccept}>{acceptLabel}</Button>
        <Button variant="textOnDark" onClick={onReject}>{rejectLabel}</Button>
      </div>
    </aside>
  );
}
