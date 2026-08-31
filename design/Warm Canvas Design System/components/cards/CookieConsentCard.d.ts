import React from "react";

/** Floating navy consent card, pinned bottom-right — one of the few places dark surface appears small on cream pages. */
export interface CookieConsentCardProps {
  title?: string;
  children?: React.ReactNode;
  acceptLabel?: string;
  rejectLabel?: string;
  onAccept?: () => void;
  onReject?: () => void;
  style?: React.CSSProperties;
}
export function CookieConsentCard(props: CookieConsentCardProps): JSX.Element;
