import React from "react";

/**
 * The workhorse of 3-up feature grids: cream card, 12px radius, 32px padding,
 * no shadow and no border.
 *
 * @startingPoint section="Cards" subtitle="Cream 3-up feature card, 32px padding" viewport="700x260"
 */
export interface FeatureCardProps {
  title?: string;
  /** Body copy. */
  children?: React.ReactNode;
  /** Optional 20–24px icon node above the title. */
  icon?: React.ReactNode;
  /** Uppercase caption above the title. */
  eyebrow?: string;
  /** `cream` on canvas bands, `dark` when the grid sits in a navy band. */
  tone?: "cream" | "dark";
  /** Slot for a TextLink or Button at the bottom. */
  footer?: React.ReactNode;
  style?: React.CSSProperties;
}
export function FeatureCard(props: FeatureCardProps): JSX.Element;
