# Warm Canvas — design system

A warm-canvas **editorial** interface system: a tinted cream page floor, serif display headlines, one warm coral action colour, and dark navy surfaces where product chrome lives. It is deliberately humanist where most AI-product brands are cool blue + slate.

## Provenance and sources

This system was built from **one source**: a written design-analysis brief pasted into chat (front-matter `version: alpha`, `name: Claude-design-analysis`) describing the marketing surface of Anthropic's Claude product — colours, type scale, spacing, radii, and a component inventory with per-component background/text/typography/padding values.

- **No codebase, Figma file, repository, slide deck, screenshots, font binaries, or logo files were provided.** Everything here derives from that brief.
- Every token value in `tokens/` is copied verbatim from the brief. Where the brief was silent (syntax-highlight colours inside code windows, the border tone inside navy cards, error state on the input) the addition is listed under **Intentional additions** below.
- **No logo or brand mark exists in this system.** The brief describes a "radial-spike glyph" but shipped no asset, and marks are never redrawn from memory — `Wordmark` sets the brand name in the display serif instead. Drop a real SVG into `assets/` and extend `components/brand/Wordmark.jsx` when one is available.
- The named typefaces (Copernicus / Tiempos Headline, StyreneB) are licensed and unavailable; open substitutes are in use and flagged under **Fonts**.
- The brief scopes itself to the **marketing surface**. The claude.ai chat product (message bubbles, conversation sidebar, file chips) is explicitly out of scope there, so no app UI kit is included here.

## Products represented

| Surface | In this system | Notes |
|---|---|---|
| Marketing site | `ui_kits/marketing/` — Home, Pricing, Connectors, Developers | The only surface the source documents |
| Product app (chat) | not built | Out of scope in the source brief |
| Slide template | not built | No deck was provided |

---

## CONTENT FUNDAMENTALS

**Voice.** Considered, plain, unhurried. Sentences are short and declarative, and they describe what the product *does* rather than how it feels. The register is closer to a literary magazine's product column than to SaaS marketing: no exclamation marks, no hype adjectives ("revolutionary", "cutting-edge", "10x"), no invented category names.

**Person.** Second person for the reader, third person for the product. "Claude reads the systems your team already works in." Never first-person-plural bragging ("we've built the world's best…"); "we" appears only in operational statements ("We use cookies to understand how the site is used").

**Casing.** Sentence case everywhere — headlines, buttons, nav items, card titles, badges. The only uppercase is the 12px tracked eyebrow/flag label (`caption-uppercase`), used for section eyebrows ("RESEARCH", "CONNECTORS") and status flags ("NEW", "BETA"). Title Case is not used.

**Headlines** are one clause, 4–8 words, and often carry a small twist of plain English where a competitor would use jargon:
- "Meet your thinking partner"
- "Built for the work that takes real thought"
- "It ships code, not suggestions"
- "Which problem are you up against?"

**Body copy** is 1–2 sentences per card, 2–3 per section intro. Concrete nouns, specific numbers, no filler: "Limits are measured in messages and agent minutes, not tokens." Em-dashes and commas do the pacing work; bullet lists appear only in pricing feature checklists.

**Buttons** are verb-first and 2–3 words: "Try Claude", "Talk to sales", "Get an API key", "Read the docs", "Start a trial". Never "Learn more →" as a primary action; "Read the model guide" as a coral text link instead.

**Fine print** is factual and short: "No credit card required." "Rough is fine." "Minimum 5 seats."

**Emoji: never.** Not in copy, not in cards, not as icon substitutes. Unicode arrows (›, →) appear only inside code/terminal output, and `—` is used as the pricing checklist marker instead of a check glyph.

**Numbers** are written as digits with units attached (`200K context`, `$30 / person / mo`, `12m 04s`), and technical values are set in mono so they read as data rather than prose.

---

## VISUAL FOUNDATIONS

### Colour
Three surface modes and one accent. Cream (`--canvas` #faf9f5) is the page floor — warm, never pure white, never cool grey. Cream cards (`--surface-card` #efe9de) sit one step darker. Navy (`--surface-dark` #181715) carries all product chrome. Coral (`--primary` #cc785c) is the only chromatic accent in the interface: scarce on individual controls (one CTA per band), generous on full-bleed callout cards. Teal and amber are companion accents restricted to status dots and eyebrow labels. Text is a five-step warm grey ramp, never pure black.

**Pacing is the layout mechanism:** no two consecutive bands share a surface tone. The canonical page runs cream → cream-card → navy → cream → coral callout → navy footer.

### Type
Serif display / sans body, and the split is not negotiable. Display sizes (64/48/36/28) are weight **400** with negative tracking (−1.5px to −0.3px); bold serif is off-brand. Body and all UI labels are the humanist sans at 400 (paragraphs) and 500 (labels, buttons, nav). Mono is reserved for code, spec values and status bars. Emphasis is achieved by going **bigger in serif**, never bolder.

### Spacing & layout
4px base. 96px between major bands (`--space-section`), 32px inside content cards, 24px inside code windows and connector tiles, 48px inside coral callouts, 64px inside CTA bands. Content caps at 1200px centred. Heroes are a 6/6 grid (text left, artifact right); feature grids 3-up; connector grids 4–6-up; pricing 3-up. Nothing is fixed-position except the top nav's page-top placement and the floating cookie card at 24px bottom-right.

### Backgrounds
Flat colour only. **No gradients, no textures, no repeating patterns, no full-bleed photography, no background images.** Where a hero needs an artifact it is either a line-art illustration (coral + navy strokes on cream) or, more often, real product chrome — a code window or agent timeline. None of those illustration assets shipped with the brief, so the kits use code/product mockups exclusively and the `HeroIllustrationCard` is left as an empty container for real art.

### Elevation & shadows
Colour-block first, shadow rare. Cream cards have **no border and no shadow** — the tone step is the elevation. Inputs, model cards, pricing tiers and connector tiles use a 1px `--hairline` (#e6dfd8) border, which reads as one elevation step rather than an ink line. The system contains exactly one shadow, `0 1px 3px rgba(20,20,19,0.08)`, used rarely. Inside navy cards, depth comes from `--surface-dark-soft` wells and `--hairline-dark` (#302d29) borders, plus the code window's own chrome (line numbers, status bar).

### Corner radii
Hierarchical and strict: 8px for controls (buttons, inputs, tabs), 12px for all content and product cards, 16px only for the hero artifact container, pill for badges, full circle for icon buttons and avatars. 4px/6px exist for tiny dropdown items.

### Cards
Two archetypes. **Cream card:** `--surface-card` fill, 12px radius, 32px padding, no border, no shadow. **Navy card:** `--surface-dark` fill, 12px radius, 24–32px padding, inner wells at `--surface-dark-soft` with hairline-dark borders. Pricing's featured tier is simply the navy card — no ribbon, no coral outline.

### States
Documented states are **default and pressed only**. Primary buttons darken to `--primary-active` on press; secondary buttons step to `--surface-card`; on-dark buttons step down to `--surface-dark-soft`. Nothing scales, lifts, or glows. Hover deliberately carries **no** treatment beyond those colour steps — do not add one. Focus is the one emphatic state: the input's border shifts to coral with a 3px coral-at-15% ring (`--focus-ring`). Disabled uses cream (`--primary-disabled`) with muted text, never opacity alone. Links underline on press.

### Animation
Effectively none. The brief puts motion out of scope, so the only movement in this system is a 120ms colour transition on interactive fills — no fades, no bounces, no parallax, no scroll reveals, no easing curves worth naming. If a prototype needs motion, keep it to short linear/ease colour and opacity changes and flag it as an addition.

### Transparency & blur
Almost never. There is no glass/blur layer anywhere. The only alpha values in the system are text-on-coral at 85–88% white, the 15% coral focus ring, the 22% coral text selection, and the faint shadow. No protection gradients — copy always sits on a solid surface, so text over imagery never needs a scrim.

### Imagery tone
Warm, low-saturation, no grain. Code and product surfaces use muted warm syntax colours (soft coral keywords, sage strings, dull gold identifiers) rather than saturated IDE blues and magentas. Avatars, when used, crop to 40px circles.

---

## ICONOGRAPHY

**No icon assets were provided with the source brief** — no icon font, no SVG sprite, no PNGs. The system therefore ships **no icons of its own**, and none were drawn (hand-rolled SVG stand-ins are worse than absence: they get copied into production).

How the components handle this:
- Icons are **slots**, not assets: `FeatureCard.icon`, `IconButton.children`, `ConnectorTile.logo`, `Button.iconLeft/iconRight` all accept any node. Pass real brand icons when you have them.
- `ConnectorTile` falls back to the connector's first letter on a cream 36px rounded square — a neutral placeholder that reads as "logo goes here" rather than pretending to be one.
- Non-icon glyphs the system *does* use: a 7–8px coloured dot for status (teal = connected/live, amber = in progress, green = success), an em-dash `—` as the pricing checklist marker, and three dim 9px circles as the code window's title-bar controls.
- **Emoji are never used**, including as icon substitutes.

**Recommended substitution if you need an icon set:** [Lucide](https://lucide.dev) from CDN — 1.5–2px stroke, rounded caps, geometrically calm, which sits closest to this system's restraint. Load `https://unpkg.com/lucide@latest/dist/umd/lucide.js`, render at 20px, colour `currentColor`, and never fill. **This is a flagged substitution, not the brand's real icon set** — replace it as soon as the real assets are available.

---

## Fonts (flagged substitutions)

| Brief specifies | Shipped here | Why |
|---|---|---|
| Copernicus / Tiempos Headline | **Newsreader** (Google Fonts, wght 400/500) | Closest freely-available Tiempos-class news serif: similar proportions and a workable optical size axis at display sizes. The brief's own suggestion, Cormorant Garamond, is too high-contrast and delicate at 400. |
| StyreneB | **Inter** (Google Fonts, 400/500/600) | The brief names Inter as the intended substitute — both are humanist screen sans. |
| JetBrains Mono | **JetBrains Mono** | Exact; freely available. |

**Ask:** if licensed Copernicus/Tiempos Headline and StyreneB binaries exist, send them — I'll add `@font-face` rules in `tokens/fonts.css` and drop the Google import. Until then every headline in this system is an approximation of the brand voice, which is the single largest fidelity gap.

---

## Intentional additions

Additions beyond the source inventory, each with a reason:

- **`Section`** — the brief documents the 96px band rhythm and 1200px container but ships no component for it; every screen needs one.
- **`Wordmark`** — a lockup slot had to exist for nav and footer; renders the name as type because no mark was provided.
- **`Badge` tones `amber` / `teal` / `outline` / `onDark`** — the brief defines the two accent colours and their uses (category badges, status) but only two badge variants.
- **`Button` variants `onCoral` / `textOnDark`** — the brief states callout cards use "a cream/canvas button on coral" and dark cards use dark secondaries; these encode that.
- **`TextInput` error state** — flagged as a known gap in the source; added because forms in the kits need it. Uses `--error`.
- **Syntax-highlight tokens (`--code-*`) and `--hairline-dark`** — the brief describes "muted blues / oranges / grays" and internal code-window chrome without giving values. These are warm-muted approximations. **Please review.**

---

## Components

Grouped by concern under `components/`. Each directory holds `<Name>.jsx`, `<Name>.d.ts`, `<Name>.prompt.md` and one `@dsCard` HTML.

**brand/** — `Wordmark`
**buttons/** — `Button`, `IconButton`, `TextLink`
**badges/** — `Badge`
**forms/** — `TextInput`
**navigation/** — `TopNav`, `CategoryTabs`
**cards/** — `FeatureCard`, `ProductMockupCard`, `CodeWindowCard`, `ModelComparisonCard`, `PricingTierCard`, `CalloutCard`, `ConnectorTile`, `CookieConsentCard`
**layout/** — `Section`, `HeroBand`, `HeroIllustrationCard`, `CtaBand`, `Footer`

---

## Index

| Path | What it is |
|---|---|
| `DESIGN_SYSTEM.md` | Consolidated machine-facing spec — every token, component API, page recipe, do/don't |
| `styles.css` | Global entry — `@import` list only. Link this one file. |
| `tokens/fonts.css` | Font imports + `--font-display` / `--font-sans` / `--font-mono` |
| `tokens/colors.css` | Base palette + semantic aliases + code-syntax tokens |
| `tokens/typography.css` | Type scale tokens + `.ds-*` type classes |
| `tokens/spacing.css` | 4px scale, container, control heights |
| `tokens/radius.css` | Radius scale |
| `tokens/elevation.css` | The one shadow, focus ring, hairline borders |
| `tokens/base.css` | Element resets, heading defaults, link colours |
| `guidelines/*.card.html` | 19 foundation specimen cards (Colors, Type, Spacing, Brand) |
| `components/…` | 21 components — see list above |
| `ui_kits/marketing/` | Marketing-site recreation: `index.html` + `HomePage` · `PricingPage` · `ConnectorsPage` · `DevelopersPage` |
| `templates/marketing-page/` | `MarketingPage.dc.html` — editable cream landing-page template |
| `thumbnail.html` | Homepage tile |
| `SKILL.md` | Agent Skills entry point |
| `assets/README.md` | Placeholder — no logo, icon or image assets were provided |
