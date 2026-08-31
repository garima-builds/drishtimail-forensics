import React from "react";

/**
 * The signature developer-page artifact: a navy code editor with line numbers,
 * muted syntax colours, an optional terminal panel and a status bar.
 *
 * @startingPoint section="Cards" subtitle="Navy code editor with terminal + status bar" viewport="700x380"
 */
export interface CodeWindowCardProps {
  /** Shown in the title bar, mono 13px. */
  filename?: string;
  /** Raw source; highlighted with the system's muted syntax palette. */
  code?: string;
  showLineNumbers?: boolean;
  /** Left status-bar text, preceded by a teal status dot. */
  statusLeft?: React.ReactNode;
  /** Right status-bar text (branch, model name, token count). */
  statusRight?: React.ReactNode;
  /** Slot at top right — usually a `secondaryOnDark` Button. */
  actions?: React.ReactNode;
  /** Optional terminal-output block rendered under the code. */
  terminal?: string;
  style?: React.CSSProperties;
}
export function CodeWindowCard(props: CodeWindowCardProps): JSX.Element;
