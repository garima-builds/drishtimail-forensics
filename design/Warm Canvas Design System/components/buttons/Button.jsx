import React, { useState } from "react";

const base = {
  display: "inline-flex", alignItems: "center", justifyContent: "center", gap: "8px",
  fontFamily: "var(--font-sans)", fontSize: "var(--button-size)", fontWeight: 500, lineHeight: 1,
  height: "var(--control-height)", padding: "12px 20px", borderRadius: "var(--radius-md)",
  border: "1px solid transparent", cursor: "pointer", textDecoration: "none",
  whiteSpace: "nowrap", transition: "background-color 120ms ease, color 120ms ease",
};

const variants = {
  primary: {
    rest: { background: "var(--primary)", color: "var(--on-primary)" },
    active: { background: "var(--primary-active)" },
    disabled: { background: "var(--primary-disabled)", color: "var(--text-muted)" },
  },
  secondary: {
    rest: { background: "var(--canvas)", color: "var(--text-ink)", borderColor: "var(--hairline)" },
    active: { background: "var(--surface-card)" },
    disabled: { background: "var(--canvas)", color: "var(--text-muted-soft)", borderColor: "var(--hairline-soft)" },
  },
  secondaryOnDark: {
    rest: { background: "var(--surface-dark-elevated)", color: "var(--text-on-dark)" },
    active: { background: "var(--surface-dark-soft)" },
    disabled: { background: "var(--surface-dark-soft)", color: "var(--text-on-dark-soft)" },
  },
  onCoral: {
    rest: { background: "var(--canvas)", color: "var(--text-ink)" },
    active: { background: "var(--surface-card)" },
    disabled: { background: "var(--surface-card)", color: "var(--text-muted)" },
  },
  text: {
    rest: { background: "transparent", color: "var(--text-ink)", padding: "12px 8px" },
    active: { color: "var(--primary-active)" },
    disabled: { color: "var(--text-muted-soft)" },
  },
  textOnDark: {
    rest: { background: "transparent", color: "var(--text-on-dark)", padding: "12px 8px" },
    active: { color: "var(--text-on-dark-soft)" },
    disabled: { color: "var(--text-on-dark-soft)" },
  },
};

export function Button({ variant = "primary", children, disabled = false, href, iconLeft, iconRight, fullWidth = false, style, ...rest }) {
  const [pressed, setPressed] = useState(false);
  const v = variants[variant] || variants.primary;
  const s = {
    ...base, ...v.rest,
    ...(pressed && !disabled ? v.active : null),
    ...(disabled ? { ...v.disabled, cursor: "not-allowed" } : null),
    ...(fullWidth ? { width: "100%" } : null),
    ...style,
  };
  const handlers = disabled ? {} : {
    onPointerDown: () => setPressed(true),
    onPointerUp: () => setPressed(false),
    onPointerLeave: () => setPressed(false),
  };
  const content = (<>{iconLeft}{children}{iconRight}</>);
  if (href && !disabled) return (<a href={href} style={s} {...handlers} {...rest}>{content}</a>);
  return (<button type="button" style={s} disabled={disabled} {...handlers} {...rest}>{content}</button>);
}
