import React from "react";

/** The navy footer that closes every page: wordmark, 4 link columns, legal row. Never inverts to cream. */
export interface FooterProps {
  brand?: string;
  /** Exactly four columns at desktop. */
  columns?: { title: string; links: string[] }[];
  /** Copyright line. */
  legal?: string;
  /** Bottom-right links (Privacy, Terms, …). */
  meta?: string[];
  style?: React.CSSProperties;
}
export function Footer(props: FooterProps): JSX.Element;
