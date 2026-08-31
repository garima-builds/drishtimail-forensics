import React from "react";

/** Tappable integration tile for 4-up / 6-up connector grids. Whole card is the target. */
export interface ConnectorTileProps {
  name?: string;
  /** Short description. */
  children?: React.ReactNode;
  /** Logo node; falls back to the first letter of `name`. */
  logo?: React.ReactNode;
  /** `connected` shows a teal status dot. */
  status?: "connected" | "available";
  style?: React.CSSProperties;
}
export function ConnectorTile(props: ConnectorTileProps): JSX.Element;
