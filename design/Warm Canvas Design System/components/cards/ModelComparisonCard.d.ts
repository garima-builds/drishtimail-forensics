import React from "react";

/** Cream + hairline card comparing one model tier: serif name, capability blurb, mono spec rows, coral link. */
export interface ModelComparisonCardProps {
  /** Model name — rendered in display serif at 36px. */
  name?: string;
  /** One-line positioning statement. */
  tagline?: string;
  /** Longer capability description. */
  children?: React.ReactNode;
  /** Spec rows; values render in mono. */
  meta?: { label: string; value: string }[];
  /** Usually a `<TextLink>`. */
  link?: React.ReactNode;
  /** Optional `<Badge>` at top right. */
  badge?: React.ReactNode;
  style?: React.CSSProperties;
}
export function ModelComparisonCard(props: ModelComparisonCardProps): JSX.Element;
