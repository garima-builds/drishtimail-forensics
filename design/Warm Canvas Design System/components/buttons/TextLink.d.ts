import React from "react";

/** An inline link. Coral is the default and one of the system's most distinctive small details. */
export interface TextLinkProps {
  href?: string;
  children?: React.ReactNode;
  /** `coral` for body links, `ink` for nav, `onDark` inside navy surfaces, `muted` for footers. */
  tone?: "coral" | "ink" | "onDark" | "muted";
  size?: "sm" | "md";
  style?: React.CSSProperties;
}
export function TextLink(props: TextLinkProps): JSX.Element;
