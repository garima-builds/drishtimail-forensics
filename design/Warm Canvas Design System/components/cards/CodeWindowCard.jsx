import React from "react";

const KEYWORDS = /\b(const|let|var|function|return|import|from|export|async|await|if|else|for|while|new|class|def|print|True|False|None|self|try|except|with|as)\b/;

function highlight(line) {
  if (/^\s*(#|\/\/)/.test(line)) return [{ t: line, c: "var(--code-comment)" }];
  const parts = [];
  const re = /("[^"]*"|'[^']*'|`[^`]*`)|(\b\d+(?:\.\d+)?\b)|([A-Za-z_$][\w$]*)(?=\()|([A-Za-z_$][\w$]*)|([^A-Za-z_$"'`\d]+)/g;
  let m;
  while ((m = re.exec(line))) {
    if (m[1]) parts.push({ t: m[1], c: "var(--code-string)" });
    else if (m[2]) parts.push({ t: m[2], c: "var(--code-num)" });
    else if (m[3]) parts.push({ t: m[3], c: KEYWORDS.test(m[3]) ? "var(--code-keyword)" : "var(--code-fn)" });
    else if (m[4]) parts.push({ t: m[4], c: KEYWORDS.test(m[4]) ? "var(--code-keyword)" : "var(--code-plain)" });
    else parts.push({ t: m[5], c: "var(--code-plain)" });
  }
  return parts;
}

export function CodeWindowCard({ filename = "main.py", code = "", showLineNumbers = true, statusLeft, statusRight, actions, terminal, style, ...rest }) {
  const lines = code.replace(/\n$/, "").split("\n");
  return (
    <section style={{
      background: "var(--surface-dark)", borderRadius: "var(--radius-lg)", padding: "var(--space-lg)",
      display: "flex", flexDirection: "column", gap: "var(--space-md)", ...style,
    }} {...rest}>
      <header style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: "var(--space-md)" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "var(--space-sm)" }}>
          <span style={{ display: "flex", gap: "6px" }}>
            {["#3a3733", "#3a3733", "#3a3733"].map((c, i) => <span key={i} style={{ width: 9, height: 9, borderRadius: "50%", background: c }} />)}
          </span>
          <span style={{ fontFamily: "var(--font-mono)", fontSize: "var(--caption-size)", color: "var(--text-on-dark-soft)" }}>{filename}</span>
        </div>
        {actions}
      </header>
      <pre style={{
        margin: 0, background: "var(--surface-dark-soft)", borderRadius: "var(--radius-md)",
        border: "1px solid var(--hairline-dark)", padding: "var(--space-md)", overflowX: "auto",
        fontFamily: "var(--font-mono)", fontSize: "var(--code-size)", lineHeight: "var(--code-lh)",
        color: "var(--code-plain)",
      }}>
        <code>
          {lines.map((line, i) => (
            <div key={i} style={{ display: "flex", gap: "var(--space-md)", whiteSpace: "pre" }}>
              {showLineNumbers && <span style={{ color: "var(--code-gutter)", userSelect: "none", minWidth: 18, textAlign: "right" }}>{i + 1}</span>}
              <span>{highlight(line).map((p, j) => <span key={j} style={{ color: p.c }}>{p.t}</span>)}</span>
            </div>
          ))}
        </code>
      </pre>
      {terminal && (
        <pre style={{
          margin: 0, background: "#121110", borderRadius: "var(--radius-md)", border: "1px solid var(--hairline-dark)",
          padding: "var(--space-md)", overflowX: "auto", fontFamily: "var(--font-mono)",
          fontSize: "var(--code-size)", lineHeight: "var(--code-lh)", color: "var(--text-on-dark-soft)", whiteSpace: "pre",
        }}>{terminal}</pre>
      )}
      {(statusLeft || statusRight) && (
        <footer style={{
          display: "flex", alignItems: "center", justifyContent: "space-between",
          background: "var(--surface-dark-elevated)", borderRadius: "var(--radius-sm)", padding: "6px 12px",
          fontFamily: "var(--font-mono)", fontSize: "12px", color: "var(--text-on-dark-soft)",
        }}>
          <span style={{ display: "inline-flex", alignItems: "center", gap: "8px" }}>
            <span style={{ width: 7, height: 7, borderRadius: "50%", background: "var(--accent-teal)" }} />{statusLeft}
          </span>
          <span>{statusRight}</span>
        </footer>
      )}
    </section>
  );
}
