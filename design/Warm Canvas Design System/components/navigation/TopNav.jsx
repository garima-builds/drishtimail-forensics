import React from "react";
import { Wordmark } from "../brand/Wordmark.jsx";
import { Button } from "../buttons/Button.jsx";
import { TextLink } from "../buttons/TextLink.jsx";

export function TopNav({ brand = "Claude", items = ["Product", "Solutions", "Use cases", "Pricing", "Research", "Company"], activeItem, ctaLabel = "Try Claude", signInLabel = "Sign in", onNavigate, style }) {
  return (
    <header style={{
      height: "var(--nav-height)", background: "var(--canvas)", borderBottom: "1px solid var(--hairline-soft)",
      display: "flex", alignItems: "center", ...style,
    }}>
      <nav style={{
        width: "100%", maxWidth: "var(--container-max)", margin: "0 auto", padding: "0 var(--space-lg)",
        display: "flex", alignItems: "center", gap: "var(--space-xl)",
      }}>
        <Wordmark name={brand} />
        <ul style={{ display: "flex", alignItems: "center", gap: "var(--space-lg)", listStyle: "none", margin: 0, padding: 0, flex: 1 }}>
          {items.map((item) => (
            <li key={item}>
              <a href="#" onClick={(e) => { e.preventDefault(); onNavigate && onNavigate(item); }}
                style={{
                  fontFamily: "var(--font-sans)", fontSize: "var(--nav-link-size)", fontWeight: 500, lineHeight: 1.4,
                  color: item === activeItem ? "var(--text-ink)" : "var(--text-muted)", textDecoration: "none",
                }}>{item}</a>
            </li>
          ))}
        </ul>
        <div style={{ display: "flex", alignItems: "center", gap: "var(--space-md)" }}>
          <TextLink tone="ink" size="sm">{signInLabel}</TextLink>
          <Button variant="primary">{ctaLabel}</Button>
        </div>
      </nav>
    </header>
  );
}
