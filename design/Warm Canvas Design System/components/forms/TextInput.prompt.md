The system's only form control — a 40px cream input with hairline border.

```jsx
<TextInput label="Work email" placeholder="you@company.com" hint="We'll never share it." />
<TextInput label="Seats" error="Enter a number between 1 and 500." />
```

Focus is the one emphatic state: border shifts to `--primary` with a `--focus-ring` halo. Only the focused state is specified by the source; `error` is an intentional addition (see readme).
