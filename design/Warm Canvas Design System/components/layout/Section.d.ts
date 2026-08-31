import React from "react";

/**
 * Band wrapper that enforces the 96px section rhythm and the 1200px centred
 * container. Intentional addition — the source documents the rhythm but ships
 * no component for it.
 */
export interface SectionProps {
  children?: React.ReactNode;
  /** Surface mode. Never repeat the same tone in two consecutive bands. */
  tone?: "canvas" | "soft" | "cream" | "creamStrong" | "dark";
  /** Vertical padding preset, or any CSS padding string. */
  pad?: "section" | "lg" | "sm" | "none" | string;
  maxWidth?: string;
  style?: React.CSSProperties;
}
export function Section(props: SectionProps): JSX.Element;
