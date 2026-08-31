import React from "react";

/** Navy card that frames real product chrome (chat panel, agent controls) inside a lighter inner well. */
export interface ProductMockupCardProps {
  /** Title above the mockup, in `--text-on-dark`. */
  label?: string;
  /** Secondary line under the label. */
  caption?: string;
  /** The product-chrome fragment. */
  children?: React.ReactNode;
  style?: React.CSSProperties;
}
export function ProductMockupCard(props: ProductMockupCardProps): JSX.Element;
