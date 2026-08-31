# assets

**Empty by design.** The source brief shipped no logo, icon set, illustrations or photography, and brand marks are never redrawn from memory.

When real assets arrive, put them here and:

- extend `components/brand/Wordmark.jsx` with the mark;
- pass real logos into `ConnectorTile.logo` and icons into `FeatureCard.icon` / `Button.iconLeft`;
- put hero line-art inside `HeroIllustrationCard`;
- update the ICONOGRAPHY section of `readme.md`.

Until then the kits use a letter fallback for connector logos and leave icon slots empty. If you need an icon set immediately, Lucide from CDN is the flagged substitution documented in `readme.md`.
