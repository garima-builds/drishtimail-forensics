import React from "react";

/**
 * The primary action control. Coral fill for the one real action on a band;
 * everything else is secondary, text or a coral inline link.
 *
 * @startingPoint section="Buttons" subtitle="Coral CTA, cream secondary, on-dark and on-coral pairs" viewport="700x220"
 */
export interface ButtonProps {
  /** Surface-aware fill. `onCoral` is the inverted cream button used inside coral callout cards. */
  variant?: "primary" | "secondary" | "secondaryOnDark" | "onCoral" | "text" | "textOnDark";
  children?: React.ReactNode;
  disabled?: boolean;
  /** Renders an <a> instead of a <button>. */
  href?: string;
  iconLeft?: React.ReactNode;
  iconRight?: React.ReactNode;
  fullWidth?: boolean;
  onClick?: (e: React.MouseEvent) => void;
  style?: React.CSSProperties;
}
export function Button(props: ButtonProps): JSX.Element;
