import React, { useState } from "react";

export function TextInput({ label, hint, error, value, onChange, placeholder, type = "text", disabled = false, id, fullWidth = true, style, ...rest }) {
  const [focused, setFocused] = useState(false);
  const inputId = id || `ti-${label ? label.replace(/\s+/g, "-").toLowerCase() : "field"}`;
  const borderColor = error ? "var(--error)" : focused ? "var(--primary)" : "var(--hairline)";
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-xs)", width: fullWidth ? "100%" : "auto", ...style }}>
      {label && <label htmlFor={inputId} style={{ fontFamily: "var(--font-sans)", fontSize: "var(--body-sm-size)", fontWeight: 500, color: "var(--text-ink)" }}>{label}</label>}
      <input id={inputId} type={type} value={value} onChange={onChange} placeholder={placeholder} disabled={disabled}
        onFocus={() => setFocused(true)} onBlur={() => setFocused(false)}
        style={{
          height: "var(--control-height)", padding: "10px 14px", borderRadius: "var(--radius-md)",
          background: "var(--canvas)", color: disabled ? "var(--text-muted-soft)" : "var(--text-ink)",
          fontFamily: "var(--font-sans)", fontSize: "var(--body-md-size)", lineHeight: 1.55,
          border: `1px solid ${borderColor}`, boxShadow: focused && !error ? "var(--focus-ring)" : "none",
          outline: "none", width: "100%", transition: "border-color 120ms ease, box-shadow 120ms ease",
        }} {...rest} />
      {(error || hint) && (
        <span style={{ fontFamily: "var(--font-sans)", fontSize: "var(--caption-size)", color: error ? "var(--error)" : "var(--text-muted)" }}>{error || hint}</span>
      )}
    </div>
  );
}
