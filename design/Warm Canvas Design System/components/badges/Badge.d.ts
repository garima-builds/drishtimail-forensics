import React from "react";

/**
 * Pill label. Cream for category tags (sentence case, 13px); coral for NEW / BETA
 * flags (uppercase, 12px, 1.5px tracking).
 *
 * @startingPoint section="Badges" subtitle="Category pills and uppercase coral flags" viewport="700x120"
 */
export interface BadgeProps {
  children?: React.ReactNode;
  /** `cream` category pill, `coral` flag, `amber`/`teal` companion accents, `outline`, `onDark`. */
  tone?: "cream" | "coral" | "amber" | "teal" | "outline" | "onDark";
  style?: React.CSSProperties;
}
export function Badge(props: BadgeProps): JSX.Element;
