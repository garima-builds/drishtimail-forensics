import React from "react";

export function CategoryTabs({ tabs = [], value, onChange, style }) {
  return (
    <div role="tablist" style={{ display: "flex", flexWrap: "wrap", gap: "var(--space-xs)", ...style }}>
      {tabs.map((tab) => {
        const active = tab === value;
        return (
          <button key={tab} role="tab" aria-selected={active} onClick={() => onChange && onChange(tab)}
            style={{
              padding: "8px 14px", borderRadius: "var(--radius-md)", border: "1px solid transparent", cursor: "pointer",
              background: active ? "var(--surface-card)" : "transparent",
              color: active ? "var(--text-ink)" : "var(--text-muted)",
              fontFamily: "var(--font-sans)", fontSize: "var(--nav-link-size)", fontWeight: 500, lineHeight: 1.4,
            }}>{tab}</button>
        );
      })}
    </div>
  );
}
