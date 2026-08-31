import React from "react";

/** Sub-nav filter row. Inactive tabs are transparent + muted; the active tab fills with `--surface-card`. */
export interface CategoryTabsProps {
  tabs?: string[];
  /** Currently selected tab label. */
  value?: string;
  onChange?: (tab: string) => void;
  style?: React.CSSProperties;
}
export function CategoryTabs(props: CategoryTabsProps): JSX.Element;
