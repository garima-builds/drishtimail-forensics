import React, { useState } from "react";

export function IconButton({ children, label, tone = "cream", disabled = false, size = 36, style, ...rest }) {
  const [pressed, setPressed] = useState(false);
  const tones = {
    cream: { background: pressed ? "var(--surface-card)" : "var(--canvas)", color: "var(--text-ink)", border: "1px solid var(--hairline)" },
    dark: { background: pressed ? "var(--surface-dark-soft)" : "var(--surface-dark-elevated)", color: "var(--text-on-dark)", border: "1px solid transparent" },
    bare: { background: "transparent", color: "var(--text-ink)", border: "1px solid transparent" },
  };
  return (
    <button type="button" aria-label={label} disabled={disabled} style={{
      width: size, height: size, minWidth: size, display: "inline-flex", alignItems: "center", justifyContent: "center",
      borderRadius: "var(--radius-full)", cursor: disabled ? "not-allowed" : "pointer", padding: 0,
      opacity: disabled ? 0.45 : 1, transition: "background-color 120ms ease", ...tones[tone], ...style,
    }}
      onPointerDown={() => setPressed(true)} onPointerUp={() => setPressed(false)} onPointerLeave={() => setPressed(false)} {...rest}>
      {children}
    </button>
  );
}
