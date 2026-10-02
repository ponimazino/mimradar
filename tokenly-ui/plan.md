# Tokenly Crypto Screener — Implementation & Design Plan

## Product scope
Tokenly is a responsive crypto-screening dashboard for mobile web and desktop web. It helps a research-minded user scan tokens through market and technical indicators, compare status quickly, then jump into a social-trends surface that connects trending topics to related tokens. The first version is a polished, interactive front-end using representative data states so the product is immediately legible without external API credentials.

## Implementation approach
- Use a small Vite + vanilla JavaScript app to keep the prototype fast, portable, and dependency-light.
- `src/main.js` owns the app state (active section, search term, timeframe, sort direction, selected token, trend selection) and renders semantic HTML.
- `src/style.css` owns the Claymorphism design system, responsive breakpoints, tables/cards, charts, shadows, and accessible focus/hover states.
- `public/manus-routes.json` declares the single-page route set for the preview/runtime contract.
- `app.config.ts` provides a stable project logo URL for the Webdev project identity.
- The dashboard intentionally keeps data local for this iteration; future live market/social data can map into the same view-models without changing the core layout.

## Design direction

### Design movement
**Claymorphism** — tactile, soft-sculpted interface surfaces inspired by friendly 3D UI, but tuned for a serious market research workflow.

### Core principles
1. **Soft surfaces, sharp signals:** plush cards and controls create a calm base, while indicator status colors and price deltas remain crisp.
2. **Scan first, drill second:** the primary dashboard supports a 5-second sweep; selected tokens reveal deeper context without losing place.
3. **Evidence over decoration:** every expressive element carries information—sparklines, topic heat, confidence bars, and indicator chips.
4. **Touch-friendly by default:** controls stay large, pill-like, and reachable on mobile, with hover states that feel like a physical press.

### Color philosophy
Use a warm cream canvas to avoid the coldness of typical exchange software. Charcoal ink is the anchor for high legibility. The ownable signal color is **punchy coral `#ff6b5f`**, used for live attention and active navigation. Mint and lavender are reserved for positive momentum and social context, while amber marks caution without feeling alarming.

### Layout paradigm
A **command-center rail** rather than a centered marketing grid: a narrow left navigation creates a stable home; the content column is a flowing stack of signal bands; the right-side detail rail appears contextually on wide screens and collapses into a bottom sheet/card flow on mobile.

### Signature elements
- **Sculpted coral mark:** a rounded square with a cut-out upward zig motif, reused as the Tokenly wordmark anchor.
- **Indicator beads:** small raised circular dots paired with labels to show green/amber/red status in a tactile way.
- **Trend ribbon:** stacked topic pills with momentum bars that visually connect social energy to token tags.

### Interaction philosophy
Interactions should feel like pressing a soft physical object: controls lift gently on hover, compress on active, and never rely on abrupt motion. Filtering updates in place; selecting a token updates the detail rail and highlights the matching row/card. The social view keeps the currently selected topic visibly connected to the tokens it influences.

### Animation
Use 160–240ms ease-out transitions for hover/press and a light 600ms stagger on initial content reveal. Sparklines should draw in once; avoid continuous motion that can distract from financial data. Respect `prefers-reduced-motion` by disabling transforms and animation.

### Typography system
- **Display:** Plus Jakarta Sans, 700–800 weight for page titles and large metrics.
- **Interface:** Plus Jakarta Sans, 500–700 weight for labels, tables, and controls.
- **Numerals:** use tabular numerals via `font-variant-numeric: tabular-nums` so price and percentage columns align.

### Brand essence
**Positioning:** The tactile market radar for finding the next token worth a closer look.

**Personality:** perceptive, buoyant, grounded.

### Brand voice
Headlines and CTAs are short, specific, and research-oriented rather than hypey.
- “Find the signal before the crowd.”
- “Trace the chatter to the chart.”

### Wordmark & logo
The Tokenly mark is a coral rounded square containing two offset diagonal clay bars that form a subtle upward zig. The wordmark sits beside it in bold lowercase type; the symbol is recognizable independently in compact/mobile contexts.

### Signature brand color
**Tokenly Coral `#ff6b5f`** — a warm signal color with enough contrast to own the interface without overwhelming the neutral research canvas.

## Project structure
```text
/tokenly
  app.config.ts              # Project identity / stable logo metadata
  package.json               # Vite scripts and dependency pin
  plan.md                    # This implementation and design plan
  public/manus-routes.json   # Single-page route manifest
  index.html                 # App shell, font loading, metadata
  src/main.js                # UI state, view models, rendering, interactions
  src/style.css              # Claymorphism tokens, responsive layout, components
```

## Required behavior covered
- Responsive web and mobile-web layouts.
- Screener surface with search, timeframe, sorting, filtering, market stats, multiple indicators, and token cards/rows.
- Token detail view with expanded indicator breakdown and market context.
- Social-trends surface with popularity/momentum signals and topic-to-token relationships.
- Navigation between overview, screener, and social trends.
- Clear representative-data states and stale-data messaging.
- Claymorphism styling with rounded controls, layered shadows, and touch-friendly interactions.
