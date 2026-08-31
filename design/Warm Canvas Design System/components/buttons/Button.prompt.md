The 40px-tall action control — coral `primary` for the single main action, `secondary` (cream + hairline) beside it, `secondaryOnDark` on navy surfaces, `onCoral` inside coral callout cards.

```jsx
<Button variant="primary">Try Claude</Button>
<Button variant="secondary">Talk to sales</Button>
<Button variant="secondaryOnDark">View docs</Button>
<Button variant="text">Sign in</Button>
```

Variants: `primary` (darkens to `--primary-active` on press — the only state change in the system), `secondary`, `secondaryOnDark`, `onCoral`, `text`, `textOnDark`. `disabled` swaps to `--primary-disabled` cream. Pass `href` for link semantics, `fullWidth` inside pricing cards.
