import React from "react";

/** A 36px circular icon control — carousel arrows, share, "view more". Always give it a `label`. */
export interface IconButtonProps {
  /** A single icon node, 16–20px. */
  children?: React.ReactNode;
  /** Accessible name (there is no visible text). */
  label: string;
  /** `cream` on canvas, `dark` on navy surfaces, `bare` for inline rows. */
  tone?: "cream" | "dark" | "bare";
  disabled?: boolean;
  /** Diameter in px. Default 36. */
  size?: number;
  onClick?: (e: React.MouseEvent) => void;
  style?: React.CSSProperties;
}
export function IconButton(props: IconButtonProps): JSX.Element;
