/* @ds-bundle: {"format":4,"namespace":"WarmCanvasDesignSystem_d8b88e","components":[{"name":"Badge","sourcePath":"components/badges/Badge.jsx"},{"name":"Wordmark","sourcePath":"components/brand/Wordmark.jsx"},{"name":"Button","sourcePath":"components/buttons/Button.jsx"},{"name":"IconButton","sourcePath":"components/buttons/IconButton.jsx"},{"name":"TextLink","sourcePath":"components/buttons/TextLink.jsx"},{"name":"CalloutCard","sourcePath":"components/cards/CalloutCard.jsx"},{"name":"CodeWindowCard","sourcePath":"components/cards/CodeWindowCard.jsx"},{"name":"ConnectorTile","sourcePath":"components/cards/ConnectorTile.jsx"},{"name":"CookieConsentCard","sourcePath":"components/cards/CookieConsentCard.jsx"},{"name":"FeatureCard","sourcePath":"components/cards/FeatureCard.jsx"},{"name":"ModelComparisonCard","sourcePath":"components/cards/ModelComparisonCard.jsx"},{"name":"PricingTierCard","sourcePath":"components/cards/PricingTierCard.jsx"},{"name":"ProductMockupCard","sourcePath":"components/cards/ProductMockupCard.jsx"},{"name":"TextInput","sourcePath":"components/forms/TextInput.jsx"},{"name":"CtaBand","sourcePath":"components/layout/CtaBand.jsx"},{"name":"Footer","sourcePath":"components/layout/Footer.jsx"},{"name":"HeroBand","sourcePath":"components/layout/HeroBand.jsx"},{"name":"HeroIllustrationCard","sourcePath":"components/layout/HeroIllustrationCard.jsx"},{"name":"Section","sourcePath":"components/layout/Section.jsx"},{"name":"CategoryTabs","sourcePath":"components/navigation/CategoryTabs.jsx"},{"name":"TopNav","sourcePath":"components/navigation/TopNav.jsx"}],"sourceHashes":{"components/badges/Badge.jsx":"ffa594a8ff1d","components/brand/Wordmark.jsx":"8fadf892b3a0","components/buttons/Button.jsx":"374c42ba4ef4","components/buttons/IconButton.jsx":"e3efb89a593c","components/buttons/TextLink.jsx":"ebc1c657f50c","components/cards/CalloutCard.jsx":"f8f1991d539e","components/cards/CodeWindowCard.jsx":"640488654f99","components/cards/ConnectorTile.jsx":"d7c5e09f1d11","components/cards/CookieConsentCard.jsx":"7e2e45129aeb","components/cards/FeatureCard.jsx":"8b08dc2daa09","components/cards/ModelComparisonCard.jsx":"d0ac3f7a7612","components/cards/PricingTierCard.jsx":"7707eeacbf44","components/cards/ProductMockupCard.jsx":"1b52a5d4455a","components/forms/TextInput.jsx":"f9522b9f583a","components/layout/CtaBand.jsx":"5247ec1cb92d","components/layout/Footer.jsx":"96e80a4ac11d","components/layout/HeroBand.jsx":"cf7e447d8ef3","components/layout/HeroIllustrationCard.jsx":"6336253cef9e","components/layout/Section.jsx":"e1c9d6f3135a","components/navigation/CategoryTabs.jsx":"5968a90377f4","components/navigation/TopNav.jsx":"60b1e9dfef86","ui_kits/marketing/ConnectorsPage.jsx":"b16dd541acb1","ui_kits/marketing/DevelopersPage.jsx":"3063453e1e7f","ui_kits/marketing/HomePage.jsx":"a19c8343b852","ui_kits/marketing/PricingPage.jsx":"434a83d24c3a"},"inlinedExternals":[],"unexposedExports":[]} */

(() => {

const __ds_ns = (window.WarmCanvasDesignSystem_d8b88e = window.WarmCanvasDesignSystem_d8b88e || {});

const __ds_scope = {};

(__ds_ns.__errors = __ds_ns.__errors || []);

// components/badges/Badge.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
function Badge({
  children,
  tone = "cream",
  style,
  ...rest
}) {
  const tones = {
    cream: {
      background: "var(--surface-card)",
      color: "var(--text-ink)",
      font: "caption"
    },
    coral: {
      background: "var(--primary)",
      color: "var(--on-primary)",
      font: "upper"
    },
    amber: {
      background: "var(--accent-amber)",
      color: "var(--text-ink)",
      font: "upper"
    },
    teal: {
      background: "var(--accent-teal)",
      color: "var(--text-ink)",
      font: "upper"
    },
    outline: {
      background: "transparent",
      color: "var(--text-muted)",
      font: "caption",
      border: "1px solid var(--hairline)"
    },
    onDark: {
      background: "var(--surface-dark-elevated)",
      color: "var(--text-on-dark)",
      font: "caption"
    }
  };
  const t = tones[tone] || tones.cream;
  const upper = t.font === "upper";
  return /*#__PURE__*/React.createElement("span", _extends({
    style: {
      display: "inline-flex",
      alignItems: "center",
      gap: "6px",
      padding: "4px 12px",
      borderRadius: "var(--radius-pill)",
      background: t.background,
      color: t.color,
      border: t.border || "1px solid transparent",
      fontFamily: "var(--font-sans)",
      fontWeight: 500,
      lineHeight: 1.4,
      fontSize: upper ? "var(--caption-upper-size)" : "var(--caption-size)",
      letterSpacing: upper ? "var(--caption-upper-ls)" : 0,
      textTransform: upper ? "uppercase" : "none",
      ...style
    }
  }, rest), children);
}
Object.assign(__ds_scope, { Badge });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/badges/Badge.jsx", error: String((e && e.message) || e) }); }

// components/brand/Wordmark.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/**
 * Text-only wordmark. No logo asset was supplied with this system, so the brand
 * name is set in the display serif — never redraw a mark from memory.
 */
function Wordmark({
  name = "Claude",
  tone = "ink",
  size = 20,
  style,
  ...rest
}) {
  const color = tone === "onDark" ? "var(--text-on-dark)" : "var(--text-ink)";
  return /*#__PURE__*/React.createElement("span", _extends({
    style: {
      display: "inline-flex",
      alignItems: "baseline",
      gap: "8px",
      fontFamily: "var(--font-display)",
      fontWeight: 500,
      fontSize: size,
      letterSpacing: "-0.4px",
      color,
      ...style
    }
  }, rest), name);
}
Object.assign(__ds_scope, { Wordmark });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/brand/Wordmark.jsx", error: String((e && e.message) || e) }); }

// components/buttons/Button.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const {
  useState
} = React;
const base = {
  display: "inline-flex",
  alignItems: "center",
  justifyContent: "center",
  gap: "8px",
  fontFamily: "var(--font-sans)",
  fontSize: "var(--button-size)",
  fontWeight: 500,
  lineHeight: 1,
  height: "var(--control-height)",
  padding: "12px 20px",
  borderRadius: "var(--radius-md)",
  border: "1px solid transparent",
  cursor: "pointer",
  textDecoration: "none",
  whiteSpace: "nowrap",
  transition: "background-color 120ms ease, color 120ms ease"
};
const variants = {
  primary: {
    rest: {
      background: "var(--primary)",
      color: "var(--on-primary)"
    },
    active: {
      background: "var(--primary-active)"
    },
    disabled: {
      background: "var(--primary-disabled)",
      color: "var(--text-muted)"
    }
  },
  secondary: {
    rest: {
      background: "var(--canvas)",
      color: "var(--text-ink)",
      borderColor: "var(--hairline)"
    },
    active: {
      background: "var(--surface-card)"
    },
    disabled: {
      background: "var(--canvas)",
      color: "var(--text-muted-soft)",
      borderColor: "var(--hairline-soft)"
    }
  },
  secondaryOnDark: {
    rest: {
      background: "var(--surface-dark-elevated)",
      color: "var(--text-on-dark)"
    },
    active: {
      background: "var(--surface-dark-soft)"
    },
    disabled: {
      background: "var(--surface-dark-soft)",
      color: "var(--text-on-dark-soft)"
    }
  },
  onCoral: {
    rest: {
      background: "var(--canvas)",
      color: "var(--text-ink)"
    },
    active: {
      background: "var(--surface-card)"
    },
    disabled: {
      background: "var(--surface-card)",
      color: "var(--text-muted)"
    }
  },
  text: {
    rest: {
      background: "transparent",
      color: "var(--text-ink)",
      padding: "12px 8px"
    },
    active: {
      color: "var(--primary-active)"
    },
    disabled: {
      color: "var(--text-muted-soft)"
    }
  },
  textOnDark: {
    rest: {
      background: "transparent",
      color: "var(--text-on-dark)",
      padding: "12px 8px"
    },
    active: {
      color: "var(--text-on-dark-soft)"
    },
    disabled: {
      color: "var(--text-on-dark-soft)"
    }
  }
};
function Button({
  variant = "primary",
  children,
  disabled = false,
  href,
  iconLeft,
  iconRight,
  fullWidth = false,
  style,
  ...rest
}) {
  const [pressed, setPressed] = useState(false);
  const v = variants[variant] || variants.primary;
  const s = {
    ...base,
    ...v.rest,
    ...(pressed && !disabled ? v.active : null),
    ...(disabled ? {
      ...v.disabled,
      cursor: "not-allowed"
    } : null),
    ...(fullWidth ? {
      width: "100%"
    } : null),
    ...style
  };
  const handlers = disabled ? {} : {
    onPointerDown: () => setPressed(true),
    onPointerUp: () => setPressed(false),
    onPointerLeave: () => setPressed(false)
  };
  const content = /*#__PURE__*/React.createElement(React.Fragment, null, iconLeft, children, iconRight);
  if (href && !disabled) return /*#__PURE__*/React.createElement("a", _extends({
    href: href,
    style: s
  }, handlers, rest), content);
  return /*#__PURE__*/React.createElement("button", _extends({
    type: "button",
    style: s,
    disabled: disabled
  }, handlers, rest), content);
}
Object.assign(__ds_scope, { Button });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/buttons/Button.jsx", error: String((e && e.message) || e) }); }

// components/buttons/IconButton.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const {
  useState
} = React;
function IconButton({
  children,
  label,
  tone = "cream",
  disabled = false,
  size = 36,
  style,
  ...rest
}) {
  const [pressed, setPressed] = useState(false);
  const tones = {
    cream: {
      background: pressed ? "var(--surface-card)" : "var(--canvas)",
      color: "var(--text-ink)",
      border: "1px solid var(--hairline)"
    },
    dark: {
      background: pressed ? "var(--surface-dark-soft)" : "var(--surface-dark-elevated)",
      color: "var(--text-on-dark)",
      border: "1px solid transparent"
    },
    bare: {
      background: "transparent",
      color: "var(--text-ink)",
      border: "1px solid transparent"
    }
  };
  return /*#__PURE__*/React.createElement("button", _extends({
    type: "button",
    "aria-label": label,
    disabled: disabled,
    style: {
      width: size,
      height: size,
      minWidth: size,
      display: "inline-flex",
      alignItems: "center",
      justifyContent: "center",
      borderRadius: "var(--radius-full)",
      cursor: disabled ? "not-allowed" : "pointer",
      padding: 0,
      opacity: disabled ? 0.45 : 1,
      transition: "background-color 120ms ease",
      ...tones[tone],
      ...style
    },
    onPointerDown: () => setPressed(true),
    onPointerUp: () => setPressed(false),
    onPointerLeave: () => setPressed(false)
  }, rest), children);
}
Object.assign(__ds_scope, { IconButton });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/buttons/IconButton.jsx", error: String((e && e.message) || e) }); }

// components/buttons/TextLink.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
function TextLink({
  href = "#",
  children,
  tone = "coral",
  size = "md",
  style,
  ...rest
}) {
  const tones = {
    coral: "var(--text-link)",
    ink: "var(--text-ink)",
    onDark: "var(--text-on-dark)",
    muted: "var(--text-muted)"
  };
  return /*#__PURE__*/React.createElement("a", _extends({
    href: href,
    style: {
      color: tones[tone],
      fontFamily: "var(--font-sans)",
      fontSize: size === "sm" ? "var(--body-sm-size)" : "var(--body-md-size)",
      fontWeight: tone === "coral" ? 400 : 500,
      textDecoration: "none",
      ...style
    }
  }, rest), children);
}
Object.assign(__ds_scope, { TextLink });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/buttons/TextLink.jsx", error: String((e && e.message) || e) }); }

// components/cards/CalloutCard.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
function CalloutCard({
  title,
  children,
  actions,
  align = "left",
  style,
  ...rest
}) {
  return /*#__PURE__*/React.createElement("section", _extends({
    style: {
      background: "var(--primary)",
      color: "var(--on-primary)",
      borderRadius: "var(--radius-lg)",
      padding: "var(--space-xxl)",
      display: "flex",
      flexDirection: "column",
      alignItems: align === "center" ? "center" : "flex-start",
      textAlign: align,
      gap: "var(--space-md)",
      ...style
    }
  }, rest), title && /*#__PURE__*/React.createElement("h3", {
    style: {
      fontFamily: "var(--font-display)",
      fontWeight: 400,
      fontSize: "var(--display-sm-size)",
      lineHeight: "var(--display-sm-lh)",
      letterSpacing: "var(--display-sm-ls)",
      color: "var(--on-primary)",
      margin: 0,
      maxWidth: "24ch"
    }
  }, title), children && /*#__PURE__*/React.createElement("p", {
    style: {
      fontFamily: "var(--font-sans)",
      fontSize: "var(--title-md-size)",
      lineHeight: 1.5,
      color: "rgba(255,255,255,0.88)",
      margin: 0,
      maxWidth: "52ch"
    }
  }, children), actions && /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      gap: "var(--space-sm)",
      marginTop: "var(--space-xs)"
    }
  }, actions));
}
Object.assign(__ds_scope, { CalloutCard });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/cards/CalloutCard.jsx", error: String((e && e.message) || e) }); }

// components/cards/CodeWindowCard.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const KEYWORDS = /\b(const|let|var|function|return|import|from|export|async|await|if|else|for|while|new|class|def|print|True|False|None|self|try|except|with|as)\b/;
function highlight(line) {
  if (/^\s*(#|\/\/)/.test(line)) return [{
    t: line,
    c: "var(--code-comment)"
  }];
  const parts = [];
  const re = /("[^"]*"|'[^']*'|`[^`]*`)|(\b\d+(?:\.\d+)?\b)|([A-Za-z_$][\w$]*)(?=\()|([A-Za-z_$][\w$]*)|([^A-Za-z_$"'`\d]+)/g;
  let m;
  while (m = re.exec(line)) {
    if (m[1]) parts.push({
      t: m[1],
      c: "var(--code-string)"
    });else if (m[2]) parts.push({
      t: m[2],
      c: "var(--code-num)"
    });else if (m[3]) parts.push({
      t: m[3],
      c: KEYWORDS.test(m[3]) ? "var(--code-keyword)" : "var(--code-fn)"
    });else if (m[4]) parts.push({
      t: m[4],
      c: KEYWORDS.test(m[4]) ? "var(--code-keyword)" : "var(--code-plain)"
    });else parts.push({
      t: m[5],
      c: "var(--code-plain)"
    });
  }
  return parts;
}
function CodeWindowCard({
  filename = "main.py",
  code = "",
  showLineNumbers = true,
  statusLeft,
  statusRight,
  actions,
  terminal,
  style,
  ...rest
}) {
  const lines = code.replace(/\n$/, "").split("\n");
  return /*#__PURE__*/React.createElement("section", _extends({
    style: {
      background: "var(--surface-dark)",
      borderRadius: "var(--radius-lg)",
      padding: "var(--space-lg)",
      display: "flex",
      flexDirection: "column",
      gap: "var(--space-md)",
      ...style
    }
  }, rest), /*#__PURE__*/React.createElement("header", {
    style: {
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      gap: "var(--space-md)"
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      alignItems: "center",
      gap: "var(--space-sm)"
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      display: "flex",
      gap: "6px"
    }
  }, ["#3a3733", "#3a3733", "#3a3733"].map((c, i) => /*#__PURE__*/React.createElement("span", {
    key: i,
    style: {
      width: 9,
      height: 9,
      borderRadius: "50%",
      background: c
    }
  }))), /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: "var(--font-mono)",
      fontSize: "var(--caption-size)",
      color: "var(--text-on-dark-soft)"
    }
  }, filename)), actions), /*#__PURE__*/React.createElement("pre", {
    style: {
      margin: 0,
      background: "var(--surface-dark-soft)",
      borderRadius: "var(--radius-md)",
      border: "1px solid var(--hairline-dark)",
      padding: "var(--space-md)",
      overflowX: "auto",
      fontFamily: "var(--font-mono)",
      fontSize: "var(--code-size)",
      lineHeight: "var(--code-lh)",
      color: "var(--code-plain)"
    }
  }, /*#__PURE__*/React.createElement("code", null, lines.map((line, i) => /*#__PURE__*/React.createElement("div", {
    key: i,
    style: {
      display: "flex",
      gap: "var(--space-md)",
      whiteSpace: "pre"
    }
  }, showLineNumbers && /*#__PURE__*/React.createElement("span", {
    style: {
      color: "var(--code-gutter)",
      userSelect: "none",
      minWidth: 18,
      textAlign: "right"
    }
  }, i + 1), /*#__PURE__*/React.createElement("span", null, highlight(line).map((p, j) => /*#__PURE__*/React.createElement("span", {
    key: j,
    style: {
      color: p.c
    }
  }, p.t))))))), terminal && /*#__PURE__*/React.createElement("pre", {
    style: {
      margin: 0,
      background: "#121110",
      borderRadius: "var(--radius-md)",
      border: "1px solid var(--hairline-dark)",
      padding: "var(--space-md)",
      overflowX: "auto",
      fontFamily: "var(--font-mono)",
      fontSize: "var(--code-size)",
      lineHeight: "var(--code-lh)",
      color: "var(--text-on-dark-soft)",
      whiteSpace: "pre"
    }
  }, terminal), (statusLeft || statusRight) && /*#__PURE__*/React.createElement("footer", {
    style: {
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      background: "var(--surface-dark-elevated)",
      borderRadius: "var(--radius-sm)",
      padding: "6px 12px",
      fontFamily: "var(--font-mono)",
      fontSize: "12px",
      color: "var(--text-on-dark-soft)"
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      display: "inline-flex",
      alignItems: "center",
      gap: "8px"
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      width: 7,
      height: 7,
      borderRadius: "50%",
      background: "var(--accent-teal)"
    }
  }), statusLeft), /*#__PURE__*/React.createElement("span", null, statusRight)));
}
Object.assign(__ds_scope, { CodeWindowCard });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/cards/CodeWindowCard.jsx", error: String((e && e.message) || e) }); }

// components/cards/ConnectorTile.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
function ConnectorTile({
  name,
  children,
  logo,
  status,
  style,
  ...rest
}) {
  return /*#__PURE__*/React.createElement("a", _extends({
    href: "#",
    style: {
      background: "var(--canvas)",
      border: "1px solid var(--hairline)",
      borderRadius: "var(--radius-lg)",
      padding: "20px",
      display: "flex",
      flexDirection: "column",
      gap: "var(--space-sm)",
      textDecoration: "none",
      color: "inherit",
      ...style
    }
  }, rest), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      gap: "var(--space-sm)"
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      width: 36,
      height: 36,
      borderRadius: "var(--radius-md)",
      background: "var(--surface-card)",
      display: "inline-flex",
      alignItems: "center",
      justifyContent: "center",
      color: "var(--text-ink)",
      fontFamily: "var(--font-sans)",
      fontSize: "var(--body-sm-size)",
      fontWeight: 500,
      overflow: "hidden"
    }
  }, logo || (name ? name.slice(0, 1) : "")), status === "connected" && /*#__PURE__*/React.createElement("span", {
    style: {
      width: 8,
      height: 8,
      borderRadius: "50%",
      background: "var(--accent-teal)"
    },
    title: "Connected"
  })), /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: "var(--font-sans)",
      fontSize: "var(--title-sm-size)",
      lineHeight: "var(--title-sm-lh)",
      fontWeight: 500,
      color: "var(--text-ink)"
    }
  }, name), /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: "var(--font-sans)",
      fontSize: "var(--body-sm-size)",
      lineHeight: 1.5,
      color: "var(--text-muted)"
    }
  }, children));
}
Object.assign(__ds_scope, { ConnectorTile });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/cards/ConnectorTile.jsx", error: String((e && e.message) || e) }); }

// components/cards/CookieConsentCard.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
function CookieConsentCard({
  title = "Cookies",
  children,
  acceptLabel = "Accept all",
  rejectLabel = "Reject all",
  onAccept,
  onReject,
  style,
  ...rest
}) {
  return /*#__PURE__*/React.createElement("aside", _extends({
    style: {
      background: "var(--surface-dark)",
      borderRadius: "var(--radius-lg)",
      padding: "var(--space-lg)",
      maxWidth: 380,
      display: "flex",
      flexDirection: "column",
      gap: "var(--space-sm)",
      ...style
    }
  }, rest), title && /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: "var(--font-sans)",
      fontSize: "var(--title-sm-size)",
      fontWeight: 500,
      color: "var(--text-on-dark)"
    }
  }, title), /*#__PURE__*/React.createElement("p", {
    style: {
      fontFamily: "var(--font-sans)",
      fontSize: "var(--body-sm-size)",
      lineHeight: 1.55,
      color: "var(--text-on-dark-soft)",
      margin: 0
    }
  }, children), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      gap: "var(--space-xs)",
      marginTop: "var(--space-xs)"
    }
  }, /*#__PURE__*/React.createElement(__ds_scope.Button, {
    variant: "secondaryOnDark",
    onClick: onAccept
  }, acceptLabel), /*#__PURE__*/React.createElement(__ds_scope.Button, {
    variant: "textOnDark",
    onClick: onReject
  }, rejectLabel)));
}
Object.assign(__ds_scope, { CookieConsentCard });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/cards/CookieConsentCard.jsx", error: String((e && e.message) || e) }); }

// components/cards/FeatureCard.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
function FeatureCard({
  title,
  children,
  icon,
  eyebrow,
  tone = "cream",
  footer,
  style,
  ...rest
}) {
  const dark = tone === "dark";
  return /*#__PURE__*/React.createElement("article", _extends({
    style: {
      display: "flex",
      flexDirection: "column",
      gap: "var(--space-sm)",
      background: dark ? "var(--surface-dark)" : "var(--surface-card)",
      color: dark ? "var(--text-on-dark-soft)" : "var(--text-body)",
      borderRadius: "var(--radius-lg)",
      padding: "var(--space-xl)",
      ...style
    }
  }, rest), icon && /*#__PURE__*/React.createElement("div", {
    style: {
      marginBottom: "var(--space-xs)",
      color: dark ? "var(--text-on-dark)" : "var(--text-ink)",
      display: "flex"
    }
  }, icon), eyebrow && /*#__PURE__*/React.createElement("span", {
    className: "ds-caption-upper",
    style: {
      color: dark ? "var(--accent-amber)" : "var(--text-muted)"
    }
  }, eyebrow), /*#__PURE__*/React.createElement("h4", {
    style: {
      fontFamily: "var(--font-sans)",
      fontSize: "var(--title-md-size)",
      lineHeight: "var(--title-md-lh)",
      fontWeight: 500,
      color: dark ? "var(--text-on-dark)" : "var(--text-ink)"
    }
  }, title), /*#__PURE__*/React.createElement("p", {
    style: {
      fontFamily: "var(--font-sans)",
      fontSize: "var(--body-md-size)",
      lineHeight: "var(--body-md-lh)",
      margin: 0,
      textWrap: "pretty"
    }
  }, children), footer && /*#__PURE__*/React.createElement("div", {
    style: {
      marginTop: "var(--space-md)"
    }
  }, footer));
}
Object.assign(__ds_scope, { FeatureCard });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/cards/FeatureCard.jsx", error: String((e && e.message) || e) }); }

// components/cards/ModelComparisonCard.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
function ModelComparisonCard({
  name,
  tagline,
  children,
  meta = [],
  link,
  badge,
  style,
  ...rest
}) {
  return /*#__PURE__*/React.createElement("article", _extends({
    style: {
      background: "var(--canvas)",
      border: "1px solid var(--hairline)",
      borderRadius: "var(--radius-lg)",
      padding: "var(--space-xl)",
      display: "flex",
      flexDirection: "column",
      gap: "var(--space-md)",
      ...style
    }
  }, rest), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      alignItems: "flex-start",
      justifyContent: "space-between",
      gap: "var(--space-sm)"
    }
  }, /*#__PURE__*/React.createElement("h3", {
    style: {
      fontFamily: "var(--font-display)",
      fontWeight: 400,
      fontSize: "var(--display-md-size)",
      lineHeight: "var(--display-md-lh)",
      letterSpacing: "var(--display-md-ls)",
      color: "var(--text-ink)",
      margin: 0
    }
  }, name), badge), tagline && /*#__PURE__*/React.createElement("p", {
    style: {
      fontFamily: "var(--font-sans)",
      fontSize: "var(--title-sm-size)",
      fontWeight: 500,
      color: "var(--text-body-strong)",
      margin: 0
    }
  }, tagline), children && /*#__PURE__*/React.createElement("p", {
    style: {
      fontFamily: "var(--font-sans)",
      fontSize: "var(--body-md-size)",
      lineHeight: "var(--body-md-lh)",
      color: "var(--text-body)",
      margin: 0,
      textWrap: "pretty"
    }
  }, children), meta.length > 0 && /*#__PURE__*/React.createElement("dl", {
    style: {
      margin: 0,
      display: "flex",
      flexDirection: "column",
      gap: "var(--space-xs)",
      borderTop: "1px solid var(--hairline-soft)",
      paddingTop: "var(--space-md)"
    }
  }, meta.map(row => /*#__PURE__*/React.createElement("div", {
    key: row.label,
    style: {
      display: "flex",
      justifyContent: "space-between",
      gap: "var(--space-md)"
    }
  }, /*#__PURE__*/React.createElement("dt", {
    style: {
      fontFamily: "var(--font-sans)",
      fontSize: "var(--body-sm-size)",
      color: "var(--text-muted)"
    }
  }, row.label), /*#__PURE__*/React.createElement("dd", {
    style: {
      fontFamily: "var(--font-mono)",
      fontSize: "var(--body-sm-size)",
      color: "var(--text-ink)",
      margin: 0
    }
  }, row.value)))), link && /*#__PURE__*/React.createElement("div", {
    style: {
      marginTop: "auto",
      paddingTop: "var(--space-xs)"
    }
  }, link));
}
Object.assign(__ds_scope, { ModelComparisonCard });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/cards/ModelComparisonCard.jsx", error: String((e && e.message) || e) }); }

// components/cards/PricingTierCard.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
function PricingTierCard({
  name,
  price,
  cadence,
  blurb,
  features = [],
  ctaLabel = "Get started",
  featured = false,
  badge,
  onCta,
  style,
  ...rest
}) {
  const fg = featured ? "var(--text-on-dark)" : "var(--text-ink)";
  const body = featured ? "var(--text-on-dark-soft)" : "var(--text-body)";
  return /*#__PURE__*/React.createElement("article", _extends({
    style: {
      background: featured ? "var(--surface-dark)" : "var(--canvas)",
      border: featured ? "1px solid transparent" : "1px solid var(--hairline)",
      borderRadius: "var(--radius-lg)",
      padding: "var(--space-xl)",
      display: "flex",
      flexDirection: "column",
      gap: "var(--space-md)",
      ...style
    }
  }, rest), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      gap: "var(--space-sm)"
    }
  }, /*#__PURE__*/React.createElement("h4", {
    style: {
      fontFamily: "var(--font-sans)",
      fontSize: "var(--title-lg-size)",
      lineHeight: "var(--title-lg-lh)",
      fontWeight: 500,
      color: fg
    }
  }, name), badge), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      alignItems: "baseline",
      gap: "8px"
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: "var(--font-display)",
      fontWeight: 400,
      fontSize: "var(--display-sm-size)",
      lineHeight: "var(--display-sm-lh)",
      letterSpacing: "var(--display-sm-ls)",
      color: fg
    }
  }, price), cadence && /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: "var(--font-sans)",
      fontSize: "var(--body-sm-size)",
      color: featured ? "var(--text-on-dark-soft)" : "var(--text-muted)"
    }
  }, cadence)), blurb && /*#__PURE__*/React.createElement("p", {
    style: {
      fontFamily: "var(--font-sans)",
      fontSize: "var(--body-sm-size)",
      lineHeight: 1.55,
      color: body,
      margin: 0
    }
  }, blurb), /*#__PURE__*/React.createElement(__ds_scope.Button, {
    variant: featured ? "secondaryOnDark" : "primary",
    fullWidth: true,
    onClick: onCta,
    style: {
      marginTop: "var(--space-xs)"
    }
  }, ctaLabel), /*#__PURE__*/React.createElement("ul", {
    style: {
      listStyle: "none",
      margin: "var(--space-xs) 0 0",
      padding: "var(--space-md) 0 0",
      borderTop: `1px solid ${featured ? "var(--hairline-dark)" : "var(--hairline-soft)"}`,
      display: "flex",
      flexDirection: "column",
      gap: "var(--space-sm)"
    }
  }, features.map(f => /*#__PURE__*/React.createElement("li", {
    key: f,
    style: {
      display: "flex",
      gap: "var(--space-sm)",
      fontFamily: "var(--font-sans)",
      fontSize: "var(--body-md-size)",
      lineHeight: 1.45,
      color: body
    }
  }, /*#__PURE__*/React.createElement("span", {
    "aria-hidden": "true",
    style: {
      color: featured ? "var(--accent-teal)" : "var(--primary)",
      flexShrink: 0
    }
  }, "\u2014"), f))));
}
Object.assign(__ds_scope, { PricingTierCard });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/cards/PricingTierCard.jsx", error: String((e && e.message) || e) }); }

// components/cards/ProductMockupCard.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
function ProductMockupCard({
  label,
  caption,
  children,
  style,
  ...rest
}) {
  return /*#__PURE__*/React.createElement("section", _extends({
    style: {
      background: "var(--surface-dark)",
      borderRadius: "var(--radius-lg)",
      padding: "var(--space-xl)",
      display: "flex",
      flexDirection: "column",
      gap: "var(--space-lg)",
      ...style
    }
  }, rest), (label || caption) && /*#__PURE__*/React.createElement("header", {
    style: {
      display: "flex",
      flexDirection: "column",
      gap: "var(--space-xs)"
    }
  }, label && /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: "var(--font-sans)",
      fontSize: "var(--title-md-size)",
      fontWeight: 500,
      color: "var(--text-on-dark)"
    }
  }, label), caption && /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: "var(--font-sans)",
      fontSize: "var(--body-sm-size)",
      lineHeight: 1.55,
      color: "var(--text-on-dark-soft)"
    }
  }, caption)), /*#__PURE__*/React.createElement("div", {
    style: {
      background: "var(--surface-dark-soft)",
      borderRadius: "var(--radius-md)",
      border: "1px solid var(--hairline-dark)",
      overflow: "hidden"
    }
  }, children));
}
Object.assign(__ds_scope, { ProductMockupCard });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/cards/ProductMockupCard.jsx", error: String((e && e.message) || e) }); }

// components/forms/TextInput.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const {
  useState
} = React;
function TextInput({
  label,
  hint,
  error,
  value,
  onChange,
  placeholder,
  type = "text",
  disabled = false,
  id,
  fullWidth = true,
  style,
  ...rest
}) {
  const [focused, setFocused] = useState(false);
  const inputId = id || `ti-${label ? label.replace(/\s+/g, "-").toLowerCase() : "field"}`;
  const borderColor = error ? "var(--error)" : focused ? "var(--primary)" : "var(--hairline)";
  return /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      flexDirection: "column",
      gap: "var(--space-xs)",
      width: fullWidth ? "100%" : "auto",
      ...style
    }
  }, label && /*#__PURE__*/React.createElement("label", {
    htmlFor: inputId,
    style: {
      fontFamily: "var(--font-sans)",
      fontSize: "var(--body-sm-size)",
      fontWeight: 500,
      color: "var(--text-ink)"
    }
  }, label), /*#__PURE__*/React.createElement("input", _extends({
    id: inputId,
    type: type,
    value: value,
    onChange: onChange,
    placeholder: placeholder,
    disabled: disabled,
    onFocus: () => setFocused(true),
    onBlur: () => setFocused(false),
    style: {
      height: "var(--control-height)",
      padding: "10px 14px",
      borderRadius: "var(--radius-md)",
      background: "var(--canvas)",
      color: disabled ? "var(--text-muted-soft)" : "var(--text-ink)",
      fontFamily: "var(--font-sans)",
      fontSize: "var(--body-md-size)",
      lineHeight: 1.55,
      border: `1px solid ${borderColor}`,
      boxShadow: focused && !error ? "var(--focus-ring)" : "none",
      outline: "none",
      width: "100%",
      transition: "border-color 120ms ease, box-shadow 120ms ease"
    }
  }, rest)), (error || hint) && /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: "var(--font-sans)",
      fontSize: "var(--caption-size)",
      color: error ? "var(--error)" : "var(--text-muted)"
    }
  }, error || hint));
}
Object.assign(__ds_scope, { TextInput });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/forms/TextInput.jsx", error: String((e && e.message) || e) }); }

// components/layout/CtaBand.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
function CtaBand({
  tone = "coral",
  title,
  subtitle,
  actions,
  aside,
  style,
  ...rest
}) {
  const coral = tone === "coral";
  return /*#__PURE__*/React.createElement("section", _extends({
    style: {
      background: coral ? "var(--primary)" : "var(--surface-dark)",
      borderRadius: "var(--radius-lg)",
      padding: "64px",
      display: "grid",
      gridTemplateColumns: aside ? "minmax(0, 1fr) minmax(0, 1fr)" : "minmax(0, 1fr)",
      gap: "var(--space-xxl)",
      alignItems: "center",
      ...style
    }
  }, rest), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      flexDirection: "column",
      gap: "var(--space-md)",
      alignItems: "flex-start"
    }
  }, /*#__PURE__*/React.createElement("h2", {
    style: {
      fontFamily: "var(--font-display)",
      fontWeight: 400,
      fontSize: "var(--display-sm-size)",
      lineHeight: "var(--display-sm-lh)",
      letterSpacing: "var(--display-sm-ls)",
      color: coral ? "var(--on-primary)" : "var(--text-on-dark)",
      margin: 0,
      maxWidth: "26ch"
    }
  }, title), subtitle && /*#__PURE__*/React.createElement("p", {
    style: {
      fontFamily: "var(--font-sans)",
      fontSize: "var(--body-md-size)",
      lineHeight: 1.55,
      color: coral ? "rgba(255,255,255,0.85)" : "var(--text-on-dark-soft)",
      margin: 0,
      maxWidth: "50ch"
    }
  }, subtitle), actions && /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      flexWrap: "wrap",
      gap: "var(--space-sm)",
      marginTop: "var(--space-xs)"
    }
  }, actions)), aside && /*#__PURE__*/React.createElement("div", {
    style: {
      minWidth: 0
    }
  }, aside));
}
Object.assign(__ds_scope, { CtaBand });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/layout/CtaBand.jsx", error: String((e && e.message) || e) }); }

// components/layout/Footer.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
function Footer({
  brand = "Anthropic",
  columns = [],
  legal = "© 2026 Anthropic PBC",
  meta = [],
  style,
  ...rest
}) {
  return /*#__PURE__*/React.createElement("footer", _extends({
    style: {
      background: "var(--surface-dark)",
      color: "var(--text-on-dark-soft)",
      padding: "64px var(--space-lg)",
      ...style
    }
  }, rest), /*#__PURE__*/React.createElement("div", {
    style: {
      maxWidth: "var(--container-max)",
      margin: "0 auto",
      display: "flex",
      flexDirection: "column",
      gap: "var(--space-xxl)"
    }
  }, /*#__PURE__*/React.createElement(__ds_scope.Wordmark, {
    name: brand,
    tone: "onDark",
    size: 18
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "grid",
      gridTemplateColumns: "repeat(4, minmax(0, 1fr))",
      gap: "var(--space-xl)"
    }
  }, columns.map(col => /*#__PURE__*/React.createElement("div", {
    key: col.title,
    style: {
      display: "flex",
      flexDirection: "column",
      gap: "var(--space-sm)"
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: "var(--font-sans)",
      fontSize: "var(--body-sm-size)",
      fontWeight: 500,
      color: "var(--text-on-dark)"
    }
  }, col.title), col.links.map(l => /*#__PURE__*/React.createElement("a", {
    key: l,
    href: "#",
    style: {
      fontFamily: "var(--font-sans)",
      fontSize: "var(--body-sm-size)",
      lineHeight: 1.55,
      color: "var(--text-on-dark-soft)",
      textDecoration: "none"
    }
  }, l))))), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      flexWrap: "wrap",
      gap: "var(--space-lg)",
      justifyContent: "space-between",
      borderTop: "1px solid var(--hairline-dark)",
      paddingTop: "var(--space-lg)"
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: "var(--font-sans)",
      fontSize: "var(--caption-size)",
      color: "var(--text-on-dark-soft)"
    }
  }, legal), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      gap: "var(--space-lg)"
    }
  }, meta.map(m => /*#__PURE__*/React.createElement("a", {
    key: m,
    href: "#",
    style: {
      fontFamily: "var(--font-sans)",
      fontSize: "var(--caption-size)",
      color: "var(--text-on-dark-soft)",
      textDecoration: "none"
    }
  }, m))))));
}
Object.assign(__ds_scope, { Footer });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/layout/Footer.jsx", error: String((e && e.message) || e) }); }

// components/layout/HeroBand.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
function HeroBand({
  eyebrow,
  title,
  subtitle,
  actions,
  note,
  artifact,
  style,
  ...rest
}) {
  return /*#__PURE__*/React.createElement("section", _extends({
    style: {
      background: "var(--canvas)",
      padding: "var(--space-section) var(--space-lg)",
      ...style
    }
  }, rest), /*#__PURE__*/React.createElement("div", {
    style: {
      maxWidth: "var(--container-max)",
      margin: "0 auto",
      display: "grid",
      gridTemplateColumns: artifact ? "minmax(0, 1fr) minmax(0, 1fr)" : "minmax(0, 720px)",
      gap: "var(--space-xxl)",
      alignItems: "center"
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      flexDirection: "column",
      gap: "var(--space-lg)"
    }
  }, eyebrow && /*#__PURE__*/React.createElement("div", null, eyebrow), /*#__PURE__*/React.createElement("h1", {
    style: {
      fontFamily: "var(--font-display)",
      fontWeight: 400,
      fontSize: "var(--display-xl-size)",
      lineHeight: "var(--display-xl-lh)",
      letterSpacing: "var(--display-xl-ls)",
      color: "var(--text-ink)",
      margin: 0,
      textWrap: "pretty"
    }
  }, title), subtitle && /*#__PURE__*/React.createElement("p", {
    style: {
      fontFamily: "var(--font-sans)",
      fontSize: "var(--title-md-size)",
      lineHeight: 1.5,
      color: "var(--text-body-strong)",
      margin: 0,
      maxWidth: "44ch",
      textWrap: "pretty"
    }
  }, subtitle), actions && /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      flexWrap: "wrap",
      gap: "var(--space-sm)",
      marginTop: "var(--space-xs)"
    }
  }, actions), note && /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: "var(--font-sans)",
      fontSize: "var(--caption-size)",
      color: "var(--text-muted-soft)"
    }
  }, note)), artifact && /*#__PURE__*/React.createElement("div", {
    style: {
      minWidth: 0
    }
  }, artifact)));
}
Object.assign(__ds_scope, { HeroBand });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/layout/HeroBand.jsx", error: String((e && e.message) || e) }); }

// components/layout/HeroIllustrationCard.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
function HeroIllustrationCard({
  children,
  tone = "cream",
  caption,
  style,
  ...rest
}) {
  const dark = tone === "dark";
  return /*#__PURE__*/React.createElement("div", _extends({
    style: {
      background: dark ? "var(--surface-dark)" : "var(--canvas)",
      border: dark ? "1px solid transparent" : "1px solid var(--hairline)",
      borderRadius: "var(--radius-xl)",
      padding: "var(--space-lg)",
      minHeight: 320,
      display: "flex",
      flexDirection: "column",
      gap: "var(--space-sm)",
      justifyContent: "center",
      ...style
    }
  }, rest), children, caption && /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: "var(--font-sans)",
      fontSize: "var(--caption-size)",
      color: dark ? "var(--text-on-dark-soft)" : "var(--text-muted)"
    }
  }, caption));
}
Object.assign(__ds_scope, { HeroIllustrationCard });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/layout/HeroIllustrationCard.jsx", error: String((e && e.message) || e) }); }

// components/layout/Section.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
function Section({
  children,
  tone = "canvas",
  pad = "section",
  maxWidth = "var(--container-max)",
  style,
  ...rest
}) {
  const tones = {
    canvas: {
      background: "var(--canvas)",
      color: "var(--text-body)"
    },
    soft: {
      background: "var(--surface-soft)",
      color: "var(--text-body)"
    },
    cream: {
      background: "var(--surface-card)",
      color: "var(--text-body)"
    },
    creamStrong: {
      background: "var(--surface-cream-strong)",
      color: "var(--text-body)"
    },
    dark: {
      background: "var(--surface-dark)",
      color: "var(--text-on-dark-soft)"
    }
  };
  const pads = {
    section: "var(--space-section) var(--space-lg)",
    lg: "var(--space-xxl) var(--space-lg)",
    sm: "var(--space-xl) var(--space-lg)",
    none: "0"
  };
  return /*#__PURE__*/React.createElement("section", _extends({
    style: {
      ...tones[tone],
      padding: pads[pad] || pad,
      ...style
    }
  }, rest), /*#__PURE__*/React.createElement("div", {
    style: {
      maxWidth,
      margin: "0 auto"
    }
  }, children));
}
Object.assign(__ds_scope, { Section });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/layout/Section.jsx", error: String((e && e.message) || e) }); }

// components/navigation/CategoryTabs.jsx
try { (() => {
function CategoryTabs({
  tabs = [],
  value,
  onChange,
  style
}) {
  return /*#__PURE__*/React.createElement("div", {
    role: "tablist",
    style: {
      display: "flex",
      flexWrap: "wrap",
      gap: "var(--space-xs)",
      ...style
    }
  }, tabs.map(tab => {
    const active = tab === value;
    return /*#__PURE__*/React.createElement("button", {
      key: tab,
      role: "tab",
      "aria-selected": active,
      onClick: () => onChange && onChange(tab),
      style: {
        padding: "8px 14px",
        borderRadius: "var(--radius-md)",
        border: "1px solid transparent",
        cursor: "pointer",
        background: active ? "var(--surface-card)" : "transparent",
        color: active ? "var(--text-ink)" : "var(--text-muted)",
        fontFamily: "var(--font-sans)",
        fontSize: "var(--nav-link-size)",
        fontWeight: 500,
        lineHeight: 1.4
      }
    }, tab);
  }));
}
Object.assign(__ds_scope, { CategoryTabs });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/navigation/CategoryTabs.jsx", error: String((e && e.message) || e) }); }

// components/navigation/TopNav.jsx
try { (() => {
function TopNav({
  brand = "Claude",
  items = ["Product", "Solutions", "Use cases", "Pricing", "Research", "Company"],
  activeItem,
  ctaLabel = "Try Claude",
  signInLabel = "Sign in",
  onNavigate,
  style
}) {
  return /*#__PURE__*/React.createElement("header", {
    style: {
      height: "var(--nav-height)",
      background: "var(--canvas)",
      borderBottom: "1px solid var(--hairline-soft)",
      display: "flex",
      alignItems: "center",
      ...style
    }
  }, /*#__PURE__*/React.createElement("nav", {
    style: {
      width: "100%",
      maxWidth: "var(--container-max)",
      margin: "0 auto",
      padding: "0 var(--space-lg)",
      display: "flex",
      alignItems: "center",
      gap: "var(--space-xl)"
    }
  }, /*#__PURE__*/React.createElement(__ds_scope.Wordmark, {
    name: brand
  }), /*#__PURE__*/React.createElement("ul", {
    style: {
      display: "flex",
      alignItems: "center",
      gap: "var(--space-lg)",
      listStyle: "none",
      margin: 0,
      padding: 0,
      flex: 1
    }
  }, items.map(item => /*#__PURE__*/React.createElement("li", {
    key: item
  }, /*#__PURE__*/React.createElement("a", {
    href: "#",
    onClick: e => {
      e.preventDefault();
      onNavigate && onNavigate(item);
    },
    style: {
      fontFamily: "var(--font-sans)",
      fontSize: "var(--nav-link-size)",
      fontWeight: 500,
      lineHeight: 1.4,
      color: item === activeItem ? "var(--text-ink)" : "var(--text-muted)",
      textDecoration: "none"
    }
  }, item)))), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      alignItems: "center",
      gap: "var(--space-md)"
    }
  }, /*#__PURE__*/React.createElement(__ds_scope.TextLink, {
    tone: "ink",
    size: "sm"
  }, signInLabel), /*#__PURE__*/React.createElement(__ds_scope.Button, {
    variant: "primary"
  }, ctaLabel))));
}
Object.assign(__ds_scope, { TopNav });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/navigation/TopNav.jsx", error: String((e && e.message) || e) }); }

// ui_kits/marketing/ConnectorsPage.jsx
try { (() => {
const {
  useState,
  useMemo
} = React;
const N = window.WarmCanvasDesignSystem_d8b88e;
const {
  Section,
  CategoryTabs,
  ConnectorTile,
  TextInput,
  Badge,
  CtaBand,
  Button,
  TextLink
} = N;
const ALL = [{
  name: "Google Drive",
  cat: "Files",
  desc: "Search and cite documents.",
  status: "connected"
}, {
  name: "Notion",
  cat: "Files",
  desc: "Read pages and databases.",
  status: "connected"
}, {
  name: "Dropbox",
  cat: "Files",
  desc: "Open shared folders."
}, {
  name: "GitHub",
  cat: "Developer",
  desc: "Repos, issues, pull requests.",
  status: "connected"
}, {
  name: "Sentry",
  cat: "Developer",
  desc: "Triage errors in context."
}, {
  name: "Linear",
  cat: "Developer",
  desc: "Read and file issues."
}, {
  name: "Jira",
  cat: "Work",
  desc: "Tickets, sprints, epics.",
  status: "connected"
}, {
  name: "Slack",
  cat: "Work",
  desc: "Summarise channels and threads."
}, {
  name: "Asana",
  cat: "Work",
  desc: "Track project status."
}, {
  name: "Snowflake",
  cat: "Data",
  desc: "Query warehouse tables."
}, {
  name: "BigQuery",
  cat: "Data",
  desc: "Run read-only analysis."
}, {
  name: "Stripe",
  cat: "Data",
  desc: "Look up customers and invoices."
}];
const CATS = ["All", "Files", "Developer", "Work", "Data"];
function ConnectorsPage() {
  const [cat, setCat] = useState("All");
  const [q, setQ] = useState("");
  const tiles = useMemo(() => ALL.filter(t => (cat === "All" || t.cat === cat) && t.name.toLowerCase().includes(q.toLowerCase())), [cat, q]);
  return /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement(Section, {
    tone: "canvas",
    pad: "lg"
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      maxWidth: 660,
      display: "flex",
      flexDirection: "column",
      gap: "var(--space-md)"
    }
  }, /*#__PURE__*/React.createElement(Badge, {
    tone: "cream"
  }, "Directory"), /*#__PURE__*/React.createElement("h1", {
    className: "ds-display-lg"
  }, "Connectors"), /*#__PURE__*/React.createElement("p", {
    className: "ds-body-md",
    style: {
      fontSize: "var(--title-md-size)",
      color: "var(--text-body-strong)"
    }
  }, "Give Claude read access to the places your work already lives. Every connector honours the permissions you already have.")), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      alignItems: "flex-end",
      justifyContent: "space-between",
      gap: "var(--space-lg)",
      marginTop: "var(--space-xl)",
      flexWrap: "wrap"
    }
  }, /*#__PURE__*/React.createElement(CategoryTabs, {
    tabs: CATS,
    value: cat,
    onChange: setCat
  }), /*#__PURE__*/React.createElement(TextInput, {
    placeholder: "Search connectors",
    value: q,
    onChange: e => setQ(e.target.value),
    fullWidth: false,
    style: {
      width: 260
    }
  })), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "grid",
      gridTemplateColumns: "repeat(4, minmax(0, 1fr))",
      gap: "var(--space-md)",
      marginTop: "var(--space-lg)"
    }
  }, tiles.map(t => /*#__PURE__*/React.createElement(ConnectorTile, {
    key: t.name,
    name: t.name,
    status: t.status
  }, t.desc))), tiles.length === 0 && /*#__PURE__*/React.createElement("p", {
    className: "ds-body-md",
    style: {
      marginTop: "var(--space-xl)",
      color: "var(--text-muted)"
    }
  }, "Nothing matches \u201C", q, "\u201D. ", /*#__PURE__*/React.createElement(TextLink, {
    onClick: () => setQ("")
  }, "Clear the search"), ".")), /*#__PURE__*/React.createElement(Section, {
    tone: "cream",
    pad: "lg"
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      gap: "var(--space-xl)",
      flexWrap: "wrap"
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      maxWidth: "48ch",
      display: "flex",
      flexDirection: "column",
      gap: "var(--space-sm)"
    }
  }, /*#__PURE__*/React.createElement("h2", {
    className: "ds-display-sm"
  }, "Missing something your team uses?"), /*#__PURE__*/React.createElement("p", {
    className: "ds-body-md"
  }, "Any service with an MCP server works today. Build one in an afternoon, or ask us to prioritise it.")), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      gap: "var(--space-sm)"
    }
  }, /*#__PURE__*/React.createElement(Button, null, "Build a connector"), /*#__PURE__*/React.createElement(Button, {
    variant: "secondary"
  }, "Request one")))), /*#__PURE__*/React.createElement(Section, {
    tone: "canvas",
    pad: "lg"
  }, /*#__PURE__*/React.createElement(CtaBand, {
    tone: "coral",
    title: "Bring your context with you",
    subtitle: "Connect a tool in under a minute.",
    actions: /*#__PURE__*/React.createElement(Button, {
      variant: "onCoral"
    }, "Open Claude")
  })));
}
Object.assign(window, {
  ConnectorsPage
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/marketing/ConnectorsPage.jsx", error: String((e && e.message) || e) }); }

// ui_kits/marketing/DevelopersPage.jsx
try { (() => {
const {
  useState,
  useMemo
} = React;
const N = window.WarmCanvasDesignSystem_d8b88e;
const {
  Section,
  CodeWindowCard,
  ProductMockupCard,
  FeatureCard,
  CategoryTabs,
  CtaBand,
  Button,
  Badge,
  TextLink
} = N;
const SAMPLES = {
  Python: `from anthropic import Anthropic

client = Anthropic()
msg = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Summarise this diff"}],
)
print(msg.content[0].text)`,
  TypeScript: `import Anthropic from "@anthropic-ai/sdk"

const client = new Anthropic()
const msg = await client.messages.create({
  model: "claude-sonnet-4-5",
  max_tokens: 1024,
  messages: [{ role: "user", content: "Summarise this diff" }],
})
console.log(msg.content[0].text)`,
  cURL: `curl https://api.anthropic.com/v1/messages \\
  -H "x-api-key: $ANTHROPIC_API_KEY" \\
  -H "anthropic-version: 2023-06-01" \\
  -d '{"model":"claude-sonnet-4-5",
       "max_tokens":1024,
       "messages":[{"role":"user","content":"Hi"}]}'`
};
function DevelopersPage() {
  const [lang, setLang] = useState("Python");
  return /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement(Section, {
    tone: "canvas",
    pad: "lg"
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: "grid",
      gridTemplateColumns: "minmax(0, 5fr) minmax(0, 7fr)",
      gap: "var(--space-xxl)",
      alignItems: "center"
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      flexDirection: "column",
      gap: "var(--space-md)",
      alignItems: "flex-start"
    }
  }, /*#__PURE__*/React.createElement(Badge, {
    tone: "coral"
  }, "API"), /*#__PURE__*/React.createElement("h1", {
    className: "ds-display-lg"
  }, "Three lines to your first response"), /*#__PURE__*/React.createElement("p", {
    className: "ds-body-md",
    style: {
      fontSize: "var(--title-md-size)",
      color: "var(--text-body-strong)"
    }
  }, "Same models, same tool use, same agent runtime the Claude apps are built on."), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      gap: "var(--space-sm)"
    }
  }, /*#__PURE__*/React.createElement(Button, null, "Get an API key"), /*#__PURE__*/React.createElement(Button, {
    variant: "secondary"
  }, "Read the docs"))), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      flexDirection: "column",
      gap: "var(--space-sm)"
    }
  }, /*#__PURE__*/React.createElement(CategoryTabs, {
    tabs: Object.keys(SAMPLES),
    value: lang,
    onChange: setLang
  }), /*#__PURE__*/React.createElement(CodeWindowCard, {
    filename: lang === "Python" ? "quickstart.py" : lang === "TypeScript" ? "quickstart.ts" : "quickstart.sh",
    code: SAMPLES[lang],
    statusLeft: "api reachable",
    statusRight: "claude-sonnet-4-5",
    actions: /*#__PURE__*/React.createElement(Button, {
      variant: "secondaryOnDark"
    }, "Copy")
  })))), /*#__PURE__*/React.createElement(Section, {
    tone: "dark"
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      maxWidth: 640,
      marginBottom: "var(--space-xxl)"
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "ds-caption-upper",
    style: {
      color: "var(--accent-amber)"
    }
  }, "Agents"), /*#__PURE__*/React.createElement("h2", {
    className: "ds-display-lg",
    style: {
      color: "var(--text-on-dark)",
      marginTop: "var(--space-sm)"
    }
  }, "Long-running work, supervised"), /*#__PURE__*/React.createElement("p", {
    className: "ds-body-md",
    style: {
      color: "var(--text-on-dark-soft)",
      marginTop: "var(--space-sm)"
    }
  }, "Start a run, stream its steps, set a budget, stop it mid-flight. The runtime handles retries and tool permissions.")), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "grid",
      gridTemplateColumns: "minmax(0, 1fr) minmax(0, 1fr)",
      gap: "var(--space-lg)"
    }
  }, /*#__PURE__*/React.createElement(ProductMockupCard, {
    label: "Run timeline",
    caption: "fix-flaky-tests \xB7 acme/checkout"
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      flexDirection: "column"
    }
  }, [["Read repository", "14 files", "done"], ["Reproduce failure", "3 runs", "done"], ["Patch test harness", "2 files changed", "done"], ["Run test suite", "128 passing", "done"], ["Open pull request", "#4192", "active"]].map(([step, detail, state], i) => /*#__PURE__*/React.createElement("div", {
    key: step,
    style: {
      display: "flex",
      alignItems: "center",
      gap: "var(--space-sm)",
      padding: "12px 16px",
      borderTop: i ? "1px solid var(--hairline-dark)" : "none"
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      width: 8,
      height: 8,
      borderRadius: "50%",
      background: state === "active" ? "var(--accent-amber)" : "var(--accent-teal)",
      flexShrink: 0
    }
  }), /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: "var(--font-sans)",
      fontSize: "var(--body-sm-size)",
      color: "var(--text-on-dark)",
      flex: 1
    }
  }, step), /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: "var(--font-mono)",
      fontSize: "12px",
      color: "var(--text-on-dark-soft)"
    }
  }, detail))))), /*#__PURE__*/React.createElement(CodeWindowCard, {
    filename: "run.ts",
    style: {
      background: "var(--surface-dark-elevated)"
    },
    code: `const run = await claude.agents.start("fix-flaky-tests", {\n  repo: "acme/checkout",\n  tools: ["shell", "git"],\n  budget: { minutes: 45 },\n})\n\nfor await (const step of run.stream()) {\n  logger.info(step.summary)\n}`,
    terminal: "$ npx claude run fix-flaky-tests\n→ 14 files read · 3 files changed\n→ 128 tests passing\n→ opened PR #4192 (12m 04s)",
    statusLeft: "agent finished",
    statusRight: "45m budget \xB7 12m used"
  }))), /*#__PURE__*/React.createElement(Section, {
    tone: "canvas"
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: "grid",
      gridTemplateColumns: "repeat(3, minmax(0, 1fr))",
      gap: "var(--space-lg)"
    }
  }, /*#__PURE__*/React.createElement(FeatureCard, {
    title: "Tool use",
    footer: /*#__PURE__*/React.createElement(TextLink, null, "Tool use guide")
  }, "Declare a JSON schema and Claude calls your function \u2014 with parallel calls and structured results."), /*#__PURE__*/React.createElement(FeatureCard, {
    title: "Batch and caching",
    footer: /*#__PURE__*/React.createElement(TextLink, null, "Pricing details")
  }, "Cache long prompts and submit batches for a fraction of the per-token cost."), /*#__PURE__*/React.createElement(FeatureCard, {
    title: "MCP",
    footer: /*#__PURE__*/React.createElement(TextLink, null, "Build a server")
  }, "Expose your own systems through the Model Context Protocol and reuse them across apps."))), /*#__PURE__*/React.createElement(Section, {
    tone: "canvas",
    pad: "lg"
  }, /*#__PURE__*/React.createElement(CtaBand, {
    tone: "dark",
    title: "Start with the quickstart",
    subtitle: "Free keys, no card, rate limits that scale with usage.",
    actions: /*#__PURE__*/React.createElement(Button, {
      variant: "secondaryOnDark"
    }, "Open the docs"),
    aside: /*#__PURE__*/React.createElement(CodeWindowCard, {
      filename: "install.sh",
      code: "pip install anthropic\nexport ANTHROPIC_API_KEY=sk-ant-…",
      showLineNumbers: false,
      style: {
        background: "var(--surface-dark-elevated)"
      }
    })
  })));
}
Object.assign(window, {
  DevelopersPage
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/marketing/DevelopersPage.jsx", error: String((e && e.message) || e) }); }

// ui_kits/marketing/HomePage.jsx
try { (() => {
const {
  useState,
  useMemo
} = React;
const N = window.WarmCanvasDesignSystem_d8b88e;
const {
  HeroBand,
  HeroIllustrationCard,
  Section,
  FeatureCard,
  ModelComparisonCard,
  CtaBand,
  CodeWindowCard,
  Button,
  Badge,
  TextLink,
  ConnectorTile
} = N;
const heroCode = `from anthropic import Anthropic

client = Anthropic()
run = client.agents.start(
    "review-pull-request",
    repo="acme/checkout",
)
for step in run.stream():
    print(step.summary)`;
function HomePage({
  onNavigate
}) {
  return /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement(HeroBand, {
    eyebrow: /*#__PURE__*/React.createElement(Badge, {
      tone: "coral"
    }, "Claude Sonnet 4.5"),
    title: "Meet your thinking partner",
    subtitle: "Claude helps your team reason through the work that actually matters \u2014 research, code, analysis, and the messy problems in between.",
    note: "No credit card required.",
    actions: /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement(Button, {
      onClick: () => onNavigate && onNavigate("Pricing")
    }, "Try Claude"), /*#__PURE__*/React.createElement(Button, {
      variant: "secondary"
    }, "Talk to sales")),
    artifact: /*#__PURE__*/React.createElement(HeroIllustrationCard, {
      tone: "dark",
      caption: "Agent run \xB7 acme/checkout"
    }, /*#__PURE__*/React.createElement(CodeWindowCard, {
      filename: "review.py",
      code: heroCode,
      statusLeft: "connected",
      statusRight: "claude-sonnet-4-5",
      style: {
        padding: 0,
        background: "transparent"
      }
    }))
  }), /*#__PURE__*/React.createElement(Section, {
    tone: "cream"
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      maxWidth: 620,
      marginBottom: "var(--space-xxl)"
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "ds-caption-upper",
    style: {
      color: "var(--text-muted)"
    }
  }, "Why Claude"), /*#__PURE__*/React.createElement("h2", {
    className: "ds-display-lg",
    style: {
      marginTop: "var(--space-sm)"
    }
  }, "Built for the work that takes real thought")), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "grid",
      gridTemplateColumns: "repeat(3, minmax(0, 1fr))",
      gap: "var(--space-lg)"
    }
  }, /*#__PURE__*/React.createElement(FeatureCard, {
    title: "Connect your tools",
    tone: "cream",
    style: {
      background: "var(--canvas)",
      border: "1px solid var(--hairline)"
    },
    footer: /*#__PURE__*/React.createElement(TextLink, null, "Browse connectors")
  }, "Claude reads the systems your team already works in \u2014 drives, wikis, tickets, repos \u2014 with permissions intact."), /*#__PURE__*/React.createElement(FeatureCard, {
    title: "Think, then answer",
    tone: "cream",
    style: {
      background: "var(--canvas)",
      border: "1px solid var(--hairline)"
    },
    footer: /*#__PURE__*/React.createElement(TextLink, null, "How extended thinking works")
  }, "Extended thinking works a problem through step by step and hands back the reasoning alongside the answer."), /*#__PURE__*/React.createElement(FeatureCard, {
    title: "Work that runs itself",
    tone: "cream",
    style: {
      background: "var(--canvas)",
      border: "1px solid var(--hairline)"
    },
    footer: /*#__PURE__*/React.createElement(TextLink, null, "See agent examples")
  }, "Give Claude a goal and the tools to reach it. Agents run for hours, check their work, and report back."))), /*#__PURE__*/React.createElement(Section, {
    tone: "dark"
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: "grid",
      gridTemplateColumns: "minmax(0, 5fr) minmax(0, 7fr)",
      gap: "var(--space-xxl)",
      alignItems: "center"
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      flexDirection: "column",
      gap: "var(--space-md)",
      alignItems: "flex-start"
    }
  }, /*#__PURE__*/React.createElement(Badge, {
    tone: "onDark"
  }, "Claude Code"), /*#__PURE__*/React.createElement("h2", {
    className: "ds-display-lg",
    style: {
      color: "var(--text-on-dark)"
    }
  }, "It ships code, not suggestions"), /*#__PURE__*/React.createElement("p", {
    className: "ds-body-md",
    style: {
      color: "var(--text-on-dark-soft)",
      maxWidth: "42ch"
    }
  }, "Claude works in your terminal and your repo: reads the codebase, writes the change, runs the tests, opens the pull request."), /*#__PURE__*/React.createElement(Button, {
    variant: "secondaryOnDark"
  }, "Read the docs")), /*#__PURE__*/React.createElement(CodeWindowCard, {
    filename: "agent.ts",
    style: {
      background: "var(--surface-dark-elevated)"
    },
    code: `const run = await claude.agents.start("fix-flaky-tests", {\n  repo: "acme/checkout",\n  budget: { minutes: 45 },\n})\n\nawait run.wait()\nconsole.log(run.pullRequest.url)`,
    terminal: "$ npx claude run fix-flaky-tests\n→ 14 files read · 3 files changed\n→ 128 tests passing\n→ opened PR #4192",
    statusLeft: "agent finished",
    statusRight: "45m budget \xB7 12m used"
  }))), /*#__PURE__*/React.createElement(Section, {
    tone: "canvas"
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      alignItems: "flex-end",
      justifyContent: "space-between",
      gap: "var(--space-lg)",
      marginBottom: "var(--space-xxl)"
    }
  }, /*#__PURE__*/React.createElement("h2", {
    className: "ds-display-lg",
    style: {
      maxWidth: "20ch"
    }
  }, "Which problem are you up against?"), /*#__PURE__*/React.createElement(TextLink, null, "Compare all models")), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "grid",
      gridTemplateColumns: "repeat(3, minmax(0, 1fr))",
      gap: "var(--space-lg)"
    }
  }, /*#__PURE__*/React.createElement(ModelComparisonCard, {
    name: "Opus",
    tagline: "The hardest problems",
    badge: /*#__PURE__*/React.createElement(Badge, {
      tone: "coral"
    }, "New"),
    meta: [{
      label: "Context",
      value: "200K"
    }, {
      label: "Best for",
      value: "research"
    }],
    link: /*#__PURE__*/React.createElement(TextLink, null, "Read the model guide")
  }, "Deep reasoning over long documents and multi-step agent runs where getting it right matters more than speed."), /*#__PURE__*/React.createElement(ModelComparisonCard, {
    name: "Sonnet",
    tagline: "Everyday work, at pace",
    meta: [{
      label: "Context",
      value: "200K"
    }, {
      label: "Best for",
      value: "coding"
    }],
    link: /*#__PURE__*/React.createElement(TextLink, null, "Read the model guide")
  }, "The default for product work \u2014 fast enough to sit inside a loop, strong enough to trust with a codebase."), /*#__PURE__*/React.createElement(ModelComparisonCard, {
    name: "Haiku",
    tagline: "Volume and latency",
    meta: [{
      label: "Context",
      value: "200K"
    }, {
      label: "Best for",
      value: "classify"
    }],
    link: /*#__PURE__*/React.createElement(TextLink, null, "Read the model guide")
  }, "Near-instant responses for classification, extraction and the high-throughput edges of a pipeline."))), /*#__PURE__*/React.createElement(Section, {
    tone: "soft"
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      alignItems: "flex-end",
      justifyContent: "space-between",
      gap: "var(--space-lg)",
      marginBottom: "var(--space-xl)"
    }
  }, /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("span", {
    className: "ds-caption-upper",
    style: {
      color: "var(--text-muted)"
    }
  }, "Connectors"), /*#__PURE__*/React.createElement("h2", {
    className: "ds-display-md",
    style: {
      marginTop: "var(--space-sm)"
    }
  }, "Bring your context with you")), /*#__PURE__*/React.createElement(TextLink, null, "View the directory")), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "grid",
      gridTemplateColumns: "repeat(4, minmax(0, 1fr))",
      gap: "var(--space-md)"
    }
  }, /*#__PURE__*/React.createElement(ConnectorTile, {
    name: "Drive",
    status: "connected"
  }, "Search and cite documents."), /*#__PURE__*/React.createElement(ConnectorTile, {
    name: "Jira",
    status: "connected"
  }, "Read tickets and sprints."), /*#__PURE__*/React.createElement(ConnectorTile, {
    name: "GitHub"
  }, "Repos, issues, pull requests."), /*#__PURE__*/React.createElement(ConnectorTile, {
    name: "Snowflake"
  }, "Query warehouse tables."))), /*#__PURE__*/React.createElement(Section, {
    tone: "canvas",
    pad: "lg"
  }, /*#__PURE__*/React.createElement(CtaBand, {
    tone: "coral",
    title: "Start with Claude today",
    subtitle: "Free to try. Bring your team when you're ready.",
    actions: /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement(Button, {
      variant: "onCoral",
      onClick: () => onNavigate && onNavigate("Pricing")
    }, "See pricing"), /*#__PURE__*/React.createElement(Button, {
      variant: "textOnDark",
      style: {
        color: "var(--on-primary)"
      }
    }, "Talk to sales"))
  })));
}
Object.assign(window, {
  HomePage
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/marketing/HomePage.jsx", error: String((e && e.message) || e) }); }

// ui_kits/marketing/PricingPage.jsx
try { (() => {
const {
  useState,
  useMemo
} = React;
const N = window.WarmCanvasDesignSystem_d8b88e;
const {
  Section,
  PricingTierCard,
  CategoryTabs,
  Badge,
  TextInput,
  Button,
  CtaBand,
  FeatureCard
} = N;
const TIERS = {
  Individual: [{
    name: "Free",
    price: "$0",
    cadence: "forever",
    blurb: "Try Claude in the web app.",
    features: ["Chat on web, iOS and Android", "Ask about attached files", "Standard usage limits"],
    cta: "Start free"
  }, {
    name: "Pro",
    price: "$20",
    cadence: "/ month",
    blurb: "For daily, serious use.",
    features: ["5× the usage of Free", "Access to Opus", "Projects and connectors", "Claude Code in the terminal"],
    cta: "Get Pro",
    featured: true,
    badge: /*#__PURE__*/React.createElement(Badge, {
      tone: "coral"
    }, "Popular")
  }, {
    name: "Max",
    price: "$100",
    cadence: "/ month",
    blurb: "For heavy agent workloads.",
    features: ["20× the usage of Pro", "Priority capacity", "Longer agent budgets"],
    cta: "Get Max"
  }],
  Teams: [{
    name: "Team",
    price: "$30",
    cadence: "/ person / mo",
    blurb: "For teams standardising on Claude.",
    features: ["Everything in Pro", "Central billing and admin", "Shared projects", "Minimum 5 seats"],
    cta: "Start a trial",
    featured: true
  }, {
    name: "Enterprise",
    price: "Custom",
    cadence: "",
    blurb: "For organisations with review requirements.",
    features: ["SSO and SCIM", "Audit logs and data controls", "Expanded context windows", "Dedicated support"],
    cta: "Contact sales"
  }, {
    name: "API",
    price: "Usage",
    cadence: "per million tokens",
    blurb: "Build Claude into your product.",
    features: ["Opus, Sonnet and Haiku", "Batch and streaming", "Tool use and agents", "Volume discounts"],
    cta: "Get an API key"
  }]
};
function PricingPage() {
  const [audience, setAudience] = useState("Individual");
  const tiers = TIERS[audience];
  return /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement(Section, {
    tone: "canvas",
    pad: "lg"
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      maxWidth: 680,
      display: "flex",
      flexDirection: "column",
      gap: "var(--space-md)"
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "ds-caption-upper",
    style: {
      color: "var(--text-muted)"
    }
  }, "Pricing"), /*#__PURE__*/React.createElement("h1", {
    className: "ds-display-lg"
  }, "Pick a plan that matches how much you think"), /*#__PURE__*/React.createElement("p", {
    className: "ds-body-md",
    style: {
      fontSize: "var(--title-md-size)",
      color: "var(--text-body-strong)"
    }
  }, "Every plan includes the full model family. What changes is how much you can use it.")), /*#__PURE__*/React.createElement("div", {
    style: {
      marginTop: "var(--space-xl)"
    }
  }, /*#__PURE__*/React.createElement(CategoryTabs, {
    tabs: Object.keys(TIERS),
    value: audience,
    onChange: setAudience
  })), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "grid",
      gridTemplateColumns: `repeat(${tiers.length}, minmax(0, 1fr))`,
      gap: "var(--space-lg)",
      marginTop: "var(--space-lg)",
      alignItems: "start"
    }
  }, tiers.map(t => /*#__PURE__*/React.createElement(PricingTierCard, {
    key: t.name,
    name: t.name,
    price: t.price,
    cadence: t.cadence,
    blurb: t.blurb,
    features: t.features,
    ctaLabel: t.cta,
    featured: t.featured,
    badge: t.badge
  })))), /*#__PURE__*/React.createElement(Section, {
    tone: "cream"
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: "grid",
      gridTemplateColumns: "minmax(0, 5fr) minmax(0, 7fr)",
      gap: "var(--space-xxl)",
      alignItems: "start"
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      flexDirection: "column",
      gap: "var(--space-md)"
    }
  }, /*#__PURE__*/React.createElement("h2", {
    className: "ds-display-md"
  }, "Not sure which plan fits?"), /*#__PURE__*/React.createElement("p", {
    className: "ds-body-md"
  }, "Tell us how your team works and we'll come back with a recommendation \u2014 usually within a day."), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      flexDirection: "column",
      gap: "var(--space-sm)",
      maxWidth: 360,
      marginTop: "var(--space-xs)"
    }
  }, /*#__PURE__*/React.createElement(TextInput, {
    label: "Work email",
    placeholder: "you@company.com"
  }), /*#__PURE__*/React.createElement(TextInput, {
    label: "Team size",
    placeholder: "e.g. 40",
    hint: "Rough is fine."
  }), /*#__PURE__*/React.createElement(Button, {
    style: {
      alignSelf: "flex-start",
      marginTop: "var(--space-xs)"
    }
  }, "Request a recommendation"))), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "grid",
      gridTemplateColumns: "1fr 1fr",
      gap: "var(--space-md)"
    }
  }, /*#__PURE__*/React.createElement(FeatureCard, {
    title: "Usage, explained",
    style: {
      background: "var(--canvas)",
      border: "1px solid var(--hairline)"
    }
  }, "Limits are measured in messages and agent minutes, not tokens. The plan page shows your current draw."), /*#__PURE__*/React.createElement(FeatureCard, {
    title: "Switch any time",
    style: {
      background: "var(--canvas)",
      border: "1px solid var(--hairline)"
    }
  }, "Upgrades apply immediately and prorate. Downgrades take effect at the end of the period."), /*#__PURE__*/React.createElement(FeatureCard, {
    title: "Your data",
    style: {
      background: "var(--canvas)",
      border: "1px solid var(--hairline)"
    }
  }, "Business plans exclude your content from model training by default. No setting to remember."), /*#__PURE__*/React.createElement(FeatureCard, {
    title: "Education and non-profit",
    style: {
      background: "var(--canvas)",
      border: "1px solid var(--hairline)"
    }
  }, "Discounted seats are available for accredited institutions and registered charities.")))), /*#__PURE__*/React.createElement(Section, {
    tone: "canvas",
    pad: "lg"
  }, /*#__PURE__*/React.createElement(CtaBand, {
    tone: "dark",
    title: "Ready to build on the API?",
    subtitle: "Keys are free to create; you only pay for what you use.",
    actions: /*#__PURE__*/React.createElement(Button, {
      variant: "secondaryOnDark"
    }, "Get an API key")
  })));
}
Object.assign(window, {
  PricingPage
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/marketing/PricingPage.jsx", error: String((e && e.message) || e) }); }

__ds_ns.Badge = __ds_scope.Badge;

__ds_ns.Wordmark = __ds_scope.Wordmark;

__ds_ns.Button = __ds_scope.Button;

__ds_ns.IconButton = __ds_scope.IconButton;

__ds_ns.TextLink = __ds_scope.TextLink;

__ds_ns.CalloutCard = __ds_scope.CalloutCard;

__ds_ns.CodeWindowCard = __ds_scope.CodeWindowCard;

__ds_ns.ConnectorTile = __ds_scope.ConnectorTile;

__ds_ns.CookieConsentCard = __ds_scope.CookieConsentCard;

__ds_ns.FeatureCard = __ds_scope.FeatureCard;

__ds_ns.ModelComparisonCard = __ds_scope.ModelComparisonCard;

__ds_ns.PricingTierCard = __ds_scope.PricingTierCard;

__ds_ns.ProductMockupCard = __ds_scope.ProductMockupCard;

__ds_ns.TextInput = __ds_scope.TextInput;

__ds_ns.CtaBand = __ds_scope.CtaBand;

__ds_ns.Footer = __ds_scope.Footer;

__ds_ns.HeroBand = __ds_scope.HeroBand;

__ds_ns.HeroIllustrationCard = __ds_scope.HeroIllustrationCard;

__ds_ns.Section = __ds_scope.Section;

__ds_ns.CategoryTabs = __ds_scope.CategoryTabs;

__ds_ns.TopNav = __ds_scope.TopNav;

})();
