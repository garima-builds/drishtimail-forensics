import React from "react";

export function TextLink({ href = "#", children, tone = "coral", size = "md", style, ...rest }) {
  const tones = { coral: "var(--text-link)", ink: "var(--text-ink)", onDark: "var(--text-on-dark)", muted: "var(--text-muted)" };
  return (
    <a href={href} style={{
      color: tones[tone], fontFamily: "var(--font-sans)",
      fontSize: size === "sm" ? "var(--body-sm-size)" : "var(--body-md-size)",
      fontWeight: tone === "coral" ? 400 : 500, textDecoration: "none", ...style,
    }} {...rest}>{children}</a>
  );
}
