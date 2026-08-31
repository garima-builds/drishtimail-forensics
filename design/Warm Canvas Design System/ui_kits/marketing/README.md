# UI kit — marketing site

Click-through recreation of the marketing surface described in the source brief. Open `index.html`.

Screens (top-nav switches between them):
- **HomePage.jsx** — hero with code-window artifact, cream feature grid, navy Claude Code band, 3-up model comparison, connector row, coral CTA.
- **PricingPage.jsx** — audience tabs (Individual / Teams), 3-up tiers with the navy featured tier, contact form, navy CTA.
- **ConnectorsPage.jsx** — live category tabs + search filtering a 4-up connector grid, empty state, cream contribution band.
- **DevelopersPage.jsx** — language-switching quickstart code window, navy agents band with run timeline, feature grid, navy CTA with code aside.

Also live: the floating navy cookie consent card (dismisses) and the navy footer.

Every screen composes the published components from `components/` — nothing is re-implemented locally. Screens are loaded as `text/babel` scripts and register themselves on `window`, so they use `React.useState` rather than ES imports.

No assets are referenced: the source shipped no logos, icons or illustrations. Icon slots are left empty and connector tiles fall back to a letter mark.
