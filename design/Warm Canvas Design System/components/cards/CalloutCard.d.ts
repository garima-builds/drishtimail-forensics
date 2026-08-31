import React from "react";

/** Full-bleed coral card — the system's one generous use of the brand colour. Put an `onCoral` Button inside. */
export interface CalloutCardProps {
  /** Serif headline, 28px on coral. */
  title?: string;
  children?: React.ReactNode;
  /** Button row; use `variant="onCoral"`. */
  actions?: React.ReactNode;
  align?: "left" | "center";
  style?: React.CSSProperties;
}
export function CalloutCard(props: CalloutCardProps): JSX.Element;
