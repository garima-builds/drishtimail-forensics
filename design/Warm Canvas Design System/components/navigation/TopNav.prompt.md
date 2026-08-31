The 64px cream top bar. Sits flush at the top of every page; the only coral on it is the single CTA.

```jsx
<TopNav brand="Claude" activeItem="Pricing" ctaLabel="Try Claude" onNavigate={setPage} />
```

Pass your own `items` array to retitle the menu. Below 768px the source collapses this to a hamburger opening a full-screen cream sheet — see `ui_kits/marketing`.
