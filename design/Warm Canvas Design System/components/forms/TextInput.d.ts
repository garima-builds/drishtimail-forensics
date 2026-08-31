import React from "react";

/** 40px cream text field with a hairline border; focus shifts the border to coral plus a 3px coral-at-15% ring. */
export interface TextInputProps {
  label?: string;
  /** Helper text under the field. */
  hint?: string;
  /** Error message — also turns the border red. */
  error?: string;
  value?: string;
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
  placeholder?: string;
  type?: string;
  disabled?: boolean;
  id?: string;
  fullWidth?: boolean;
  style?: React.CSSProperties;
}
export function TextInput(props: TextInputProps): JSX.Element;
