import React from "react";

/**
 * The brand lockup, set as type. Intentional addition: the source documents a
 * radial-spike glyph but shipped no asset, so this renders the name only.
 */
export interface WordmarkProps {
  /** Brand or product name. */
  name?: string;
  tone?: "ink" | "onDark";
  /** Font size in px. Default 20. */
  size?: number;
  style?: React.CSSProperties;
}
export function Wordmark(props: WordmarkProps): JSX.Element;
