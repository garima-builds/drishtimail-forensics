The signature developer-page artifact: navy code editor with line numbers, muted syntax colours, optional terminal panel and status bar.

```jsx
<CodeWindowCard filename="review.py" code={src} actions={<Button variant="secondaryOnDark">Run</Button>}
  terminal={"$ python review.py\n2 suggestions"} statusLeft="connected" statusRight="claude-sonnet-4-5" />
```

Code never wraps — the card scrolls horizontally at small widths.
