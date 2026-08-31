import React from "react";

/** 16px-radius container for the hero's right-hand artifact — line-art illustration on cream, or product chrome on navy. */
export interface HeroIllustrationCardProps {
  children?: React.ReactNode;
  /** `cream` (canvas + hairline) or `dark` (navy product surface). */
  tone?: "cream" | "dark";
  caption?: string;
  style?: React.CSSProperties;
}
export function HeroIllustrationCard(props: HeroIllustrationCardProps): JSX.Element;
