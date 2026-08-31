import React from "react";

/**
 * One pricing tier. The featured tier flips to the navy surface — the dark
 * background *is* the featured signal; no coral border or ribbon.
 *
 * @startingPoint section="Cards" subtitle="Cream tier and navy featured tier" viewport="700x420"
 */
export interface PricingTierCardProps {
  /** Plan name, sans 22px/500. */
  name?: string;
  /** Price, set in display serif. */
  price?: string;
  /** e.g. "per person / month". */
  cadence?: string;
  blurb?: string;
  features?: string[];
  ctaLabel?: string;
  /** Flips the card to the navy featured treatment. */
  featured?: boolean;
  /** Optional `<Badge>` beside the plan name. */
  badge?: React.ReactNode;
  onCta?: () => void;
  style?: React.CSSProperties;
}
export function PricingTierCard(props: PricingTierCardProps): JSX.Element;
