import React from "react";

/**
 * Cream hero: 6/6 grid with the serif h1 stack on the left and one artifact
 * (illustration card or code window) on the right. 96px vertical padding.
 *
 * @startingPoint section="Marketing" subtitle="6/6 cream hero with serif h1 and artifact slot" viewport="1280x620"
 */
export interface HeroBandProps {
  /** Small node above the h1 — usually a `<Badge>`. */
  eyebrow?: React.ReactNode;
  /** The 64px serif headline. */
  title?: React.ReactNode;
  subtitle?: React.ReactNode;
  /** Button row. */
  actions?: React.ReactNode;
  /** Fine print under the buttons. */
  note?: React.ReactNode;
  /** Right-hand artifact; omitting it makes the hero single-column. */
  artifact?: React.ReactNode;
  style?: React.CSSProperties;
}
export function HeroBand(props: HeroBandProps): JSX.Element;
