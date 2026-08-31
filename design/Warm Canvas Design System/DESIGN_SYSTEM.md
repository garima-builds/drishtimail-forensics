# Warm Canvas — consolidated design system reference

Single-file reference for the Warm Canvas system. Everything here is derived from one source: a written design-analysis brief (`Claude-design-analysis`, version alpha) describing the marketing surface of Anthropic's Claude product. No codebase, Figma file, font binaries or logo assets were provided. See `readme.md` for provenance, content voice, visual foundations and iconography prose; this file is the machine-facing spec.

Entry point: link **`styles.css`** (an `@import` list only). All values below are CSS custom properties on `:root`.

---

## 1. Identity in one paragraph

A tinted cream page floor, serif display headlines at weight 400 with negative tracking, one warm coral action colour used scarcely, and dark navy surfaces carrying all product chrome. Flat colour blocks, hairline borders, one faint shadow, no gradients, no textures, no blur, effectively no animation. Pacing is the layout mechanism: no two consecutive bands share a surface tone.

---

## 2. Colour tokens

### Brand & accent
| Token | Value | Use |
|---|---|---|
| `--primary` | `#cc785c` | Every primary CTA; full-bleed callout cards |
| `--primary-active` | `#a9583e` | Pressed state of primary |
| `--primary-disabled` | `#e6dfd8` | Disabled primary fill (with `--text-muted`) |
| `--on-primary` | `#ffffff` | Text on coral |
| `--accent-teal` | `#5db8a6` | Status dots: connected / live |
| `--accent-amber` | `#e8a55a` | Eyebrow labels on dark; in-progress dots |

### Surfaces
| Token | Value | Use |
|---|---|---|
| `--canvas` | `#faf9f5` | Default page floor. Never pure white |
| `--surface-soft` | `#f5f0e8` | Soft dividing bands |
| `--surface-card` | `#efe9de` | Feature / content cards |
| `--surface-cream-strong` | `#e8e0d2` | Selected tabs, emphasised bands |
| `--surface-dark` | `#181715` | Code windows, featured tier, footer |
| `--surface-dark-soft` | `#1f1e1b` | Code wells inside dark cards |
| `--surface-dark-elevated` | `#252320` | Elevated panels, on-dark buttons, status bars |

### Lines
| Token | Value | Use |
|---|---|---|
| `--hairline` | `#e6dfd8` | 1px border on cream surfaces (inputs, model/pricing/connector cards) |
| `--hairline-soft` | `#ebe6df` | In-band dividers, nav underline |
| `--hairline-dark` | `#302d29` | Borders inside navy cards — **added, not in source** |

### Text
| Token | Value | Use |
|---|---|---|
| `--text-ink` | `#141413` | Headlines, primary text |
| `--text-body-strong` | `#252523` | Lead paragraphs |
| `--text-body` | `#3d3d3a` | Default running text |
| `--text-muted` | `#6c6a64` | Sub-heads, breadcrumbs, inactive tabs |
| `--text-muted-soft` | `#8e8b82` | Captions, fine print |
| `--text-on-dark` | `#faf9f5` | Text on navy — cream-tinted, not white |
| `--text-on-dark-soft` | `#a09d96` | Secondary text on navy, footer links |
| `--text-link` | `#cc785c` | Inline links |

### Status
`--success #5db872` · `--warning #d4a017` · `--error #c64545`. Rare on marketing surfaces.

### Code syntax (**added — brief gave no values; please review**)
`--code-plain #d8d4cc` · `--code-comment #6f6b63` · `--code-keyword #cc9a7c` · `--code-string #9dc4b8` · `--code-fn #d8c58a` · `--code-num #c8a2c8` · `--code-gutter #58544d`

### Rules
- Coral is scarce on individual elements — **one primary CTA per band** — and generous only on full-bleed callout/CTA cards.
- Never introduce a fourth surface family. Cream + coral + navy is the trinity.
- No cool greys, no pure white canvas, no blue or cyan accents.

---

## 3. Type

Families: `--font-display` (Newsreader → stands in for Copernicus/Tiempos Headline) · `--font-sans` (Inter → StyreneB) · `--font-mono` (JetBrains Mono, exact).

| Role | Family | Size | Weight | Line height | Tracking | Class |
|---|---|---|---|---|---|---|
| display-xl | display | 64px | 400 | 1.05 | −1.5px | `.ds-display-xl` |
| display-lg | display | 48px | 400 | 1.1 | −1px | `.ds-display-lg` |
| display-md | display | 36px | 400 | 1.15 | −0.5px | `.ds-display-md` |
| display-sm | display | 28px | 400 | 1.2 | −0.3px | `.ds-display-sm` |
| title-lg | sans | 22px | 500 | 1.3 | 0 | `.ds-title-lg` |
| title-md | sans | 18px | 500 | 1.4 | 0 | `.ds-title-md` |
| title-sm | sans | 16px | 500 | 1.4 | 0 | `.ds-title-sm` |
| body-md | sans | 16px | 400 | 1.55 | 0 | `.ds-body-md` |
| body-sm | sans | 14px | 400 | 1.55 | 0 | `.ds-body-sm` |
| caption | sans | 13px | 500 | 1.4 | 0 | `.ds-caption` |
| caption-uppercase | sans | 12px | 500 | 1.4 | 1.5px | `.ds-caption-upper` |
| code | mono | 14px | 400 | 1.6 | 0 | `.ds-code` |
| button | sans | 14px | 500 | 1 | 0 | — |
| nav-link | sans | 14px | 500 | 1.4 | 0 | — |

Per-value tokens exist as `--display-xl-size` / `-lh` / `-ls`, `--title-md-size`, `--body-md-size`, etc.

### Rules
- Display is **always** serif at weight 400 with its negative tracking. Serif at 700, or a sans display, is off-brand.
- Emphasis goes **bigger in serif**, never bolder.
- Prices, model names and pricing-tier headlines stay serif even at 28px.
- Body 400 for paragraphs, 500 for labels/buttons/nav.
- Sentence case everywhere; uppercase only for `caption-uppercase` eyebrows and flags.
- Minimum body size 14px; captions 12–13px.

---

## 4. Spacing, layout, shape, elevation

Spacing (4px base): `--space-xxs 4` · `xs 8` · `sm 12` · `md 16` · `lg 24` · `xl 32` · `xxl 48` · `section 96`.

| Context | Value |
|---|---|
| Between major bands | `--space-section` 96px |
| Content card padding | `--space-xl` 32px |
| Code window / connector tile padding | `--space-lg` 24px / 20px |
| Coral callout padding | `--space-xxl` 48px |
| CTA band padding | 64px |
| Footer vertical padding | 64px |

Layout: `--container-max` 1200px centred · `--nav-height` 64px · `--control-height` 40px · `--icon-button-size` 36px. Hero = 6/6 grid. Feature grids 3-up. Connector grids 4–6-up. Pricing 3-up.

Radius: `--radius-xs 4` · `sm 6` · `md 8` (buttons, inputs, tabs) · `lg 12` (all content/product cards) · `xl 16` (hero artifact container only) · `pill`/`full` 9999.

Elevation: `--border-hairline` (1px `--hairline`) · `--shadow-subtle 0 1px 3px rgba(20,20,19,.08)` — the system's only shadow, used rarely · `--focus-ring 0 0 0 3px rgba(204,120,92,.15)`. Cream cards have **no border and no shadow**; the tone step is the elevation.

Responsive: mobile <768px (hamburger nav as full-screen cream sheet; h1 64→32px; grids 1-up; footer 4→1 col) · tablet 768–1024 (2-up features, 2-up pricing) · desktop 1024–1440 · wide >1440 (container caps at 1200). Grids reduce columns rather than scaling cards. Code never wraps — the card scrolls horizontally.

---

## 5. States

Only **default, pressed, focused, disabled** are specified.

| State | Treatment |
|---|---|
| Primary pressed | fill → `--primary-active` |
| Secondary pressed | fill → `--surface-card` |
| On-dark pressed | fill → `--surface-dark-soft` |
| Input focused | border → `--primary` + `--focus-ring` |
| Disabled | `--primary-disabled` fill with `--text-muted`; never opacity alone |
| Link pressed | underline |
| Hover | **nothing beyond the pressed colour step — do not add one** |

Motion: a 120ms colour transition on interactive fills is the only movement. No fades, lifts, scales, bounces, parallax or scroll reveals. Transparency is limited to text-on-coral at 85–88% white, the 15% focus ring and 22% selection. No blur, no glass, no protection gradients.

---

## 6. Component API

Namespace: `window.WarmCanvasDesignSystem_d8b88e`. Each component lives in `components/<group>/` with a `.d.ts` props contract and a `.prompt.md` usage note.

### buttons/
**`Button`** — `variant?: "primary" | "secondary" | "secondaryOnDark" | "onCoral" | "text" | "textOnDark"`, `children`, `disabled?`, `href?`, `iconLeft?`, `iconRight?`, `fullWidth?`, `onClick?`, `style?`. 40px tall, 12×20 padding, 8px radius.
**`IconButton`** — `label` (required), `children`, `tone?: "cream" | "dark" | "bare"`, `size?` (default 36), `disabled?`, `onClick?`.
**`TextLink`** — `href?`, `children`, `tone?: "coral" | "ink" | "onDark" | "muted"`, `size?: "sm" | "md"`.

### badges/
**`Badge`** — `children`, `tone?: "cream" | "coral" | "amber" | "teal" | "outline" | "onDark"`. Cream renders 13px sentence case; coral/amber/teal render 12px uppercase, 1.5px tracking.

### forms/
**`TextInput`** — `label?`, `hint?`, `error?`, `value?`, `onChange?`, `placeholder?`, `type?`, `disabled?`, `id?`, `fullWidth?`. 40px, 10×14 padding, 8px radius.

### brand/
**`Wordmark`** — `name?`, `tone?: "ink" | "onDark"`, `size?` (default 20). Type only — no mark exists.

### navigation/
**`TopNav`** — `brand?`, `items?: string[]`, `activeItem?`, `ctaLabel?`, `signInLabel?`, `onNavigate?`. 64px cream bar.
**`CategoryTabs`** — `tabs?: string[]`, `value?`, `onChange?`. Active tab = `--surface-card` fill + ink text; nothing else changes.

### cards/
**`FeatureCard`** — `title?`, `children`, `icon?`, `eyebrow?`, `tone?: "cream" | "dark"`, `footer?`.
**`ProductMockupCard`** — `label?`, `caption?`, `children` (real product chrome inside a `--surface-dark-soft` well).
**`CodeWindowCard`** — `filename?`, `code?`, `showLineNumbers?`, `statusLeft?`, `statusRight?`, `actions?`, `terminal?`. Highlights with the `--code-*` palette.
**`ModelComparisonCard`** — `name?` (display serif), `tagline?`, `children`, `meta?: {label,value}[]` (values in mono), `link?`, `badge?`.
**`PricingTierCard`** — `name?`, `price?` (display serif), `cadence?`, `blurb?`, `features?: string[]`, `ctaLabel?`, `featured?`, `badge?`, `onCta?`. `featured` flips to navy — the dark surface **is** the signal; no ribbon or coral outline.
**`CalloutCard`** — `title?`, `children`, `actions?` (use `variant="onCoral"`), `align?: "left" | "center"`. Coral fill, 48px padding. One per page at most.
**`ConnectorTile`** — `name?`, `children`, `logo?`, `status?: "connected" | "available"`. Whole card is the tap target; teal dot marks connected.
**`CookieConsentCard`** — `title?`, `children`, `acceptLabel?`, `rejectLabel?`, `onAccept?`, `onReject?`. Navy, max 380px, pinned 24px bottom-right.

### layout/
**`Section`** — `children`, `tone?: "canvas" | "soft" | "cream" | "creamStrong" | "dark"`, `pad?: "section" | "lg" | "sm" | "none" | string`, `maxWidth?`. **Added** — enforces the 96px rhythm and 1200px container.
**`HeroBand`** — `eyebrow?`, `title?`, `subtitle?`, `actions?`, `note?`, `artifact?`. Omitting `artifact` makes it single-column.
**`HeroIllustrationCard`** — `children`, `tone?: "cream" | "dark"`, `caption?`. The only 16px radius in the system.
**`CtaBand`** — `tone?: "coral" | "dark"`, `title?`, `subtitle?`, `actions?`, `aside?`. 64px padding.
**`Footer`** — `brand?`, `columns?: {title,links[]}[]` (four at desktop), `legal?`, `meta?: string[]`. Never inverts to cream.

---

## 7. Page recipe

```
TopNav (cream, 64px)
HeroBand (cream) — serif h1 + subtitle + one primary + one secondary + artifact
Section tone="cream" — 3-up FeatureCard grid
Section tone="dark" — copy + CodeWindowCard / ProductMockupCard
Section tone="canvas" — 3-up ModelComparisonCard or pricing
Section tone="canvas" pad="lg" — CtaBand tone="coral" (or "dark" on developer pages)
Footer (navy)
```

Alternate the tone every band. Never place two cream bands back to back.

---

## 8. Content rules

Sentence case throughout. Second person for the reader, third person for the product. Headlines one clause, 4–8 words ("It ships code, not suggestions"). Body 1–2 sentences per card. Buttons verb-first, 2–3 words ("Get an API key"). Concrete nouns and real numbers over adjectives. No hype words, no exclamation marks, no Title Case, **no emoji ever** — including as icon substitutes. Numbers as digits with units attached, technical values in mono.

---

## 9. Do / don't

**Do** — anchor on cream; keep display serif at 400 with negative tracking; reserve coral for one CTA per band plus full-bleed callouts; show real product chrome instead of illustrations of it; alternate cream and navy bands; apply 96px between bands.

**Don't** — use pure white or cool grey canvas; bold the serif; use sans for display; put coral on incidental elements; add hover treatments; repeat a surface tone in consecutive bands; introduce a fourth surface family; add gradients, textures, blur or scroll animation; draw a logo or icon that wasn't supplied.

---

## 10. Known gaps

- **Fonts are substitutions.** Newsreader for Copernicus/Tiempos Headline, Inter for StyreneB. The licensed faces are unavailable; headlines are approximations of the brand voice.
- **No logo, icons, illustrations or photography.** Nothing was drawn. `Wordmark` is type; icon props are empty slots; `ConnectorTile` falls back to a letter mark. Lucide from CDN is the flagged icon substitution if one is needed.
- **Added values not in the source:** the `--code-*` syntax palette, `--hairline-dark`, `TextInput` `error`, `Section`, `Wordmark`, extra `Badge` tones, `Button` `onCoral` / `textOnDark`.
- **Marketing surface only.** The chat product (message bubbles, conversation sidebar, file chips) is out of scope in the source, so there is no app UI kit and no slide template.
