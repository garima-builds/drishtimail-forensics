import React from "react";

/**
 * Pre-footer CTA band, 64px padding. Coral on marketing pages; navy on
 * developer pages, usually paired with a code window in `aside`.
 *
 * @startingPoint section="Marketing" subtitle="Coral or navy pre-footer CTA band" viewport="1200x300"
 */
export interface CtaBandProps {
  tone?: "coral" | "dark";
  /** Serif headline — stays serif even at 28px. */
  title?: React.ReactNode;
  subtitle?: React.ReactNode;
  /** Button row; use `onCoral` on coral, `secondaryOnDark` on navy. */
  actions?: React.ReactNode;
  /** Optional right-hand artifact — makes the band a 2-column grid. */
  aside?: React.ReactNode;
  style?: React.CSSProperties;
}
export function CtaBand(props: CtaBandProps): JSX.Element;
