import React from "react";

/**
 * The 64px cream top bar every page opens with: wordmark, horizontal menu,
 * "Sign in" text link and one coral CTA.
 *
 * @startingPoint section="Navigation" subtitle="64px cream bar with wordmark, menu and coral CTA" viewport="1280x64"
 */
export interface TopNavProps {
  brand?: string;
  /** Menu labels, left to right. */
  items?: string[];
  /** Label rendered in ink instead of muted. */
  activeItem?: string;
  ctaLabel?: string;
  signInLabel?: string;
  onNavigate?: (item: string) => void;
  style?: React.CSSProperties;
}
export function TopNav(props: TopNavProps): JSX.Element;
