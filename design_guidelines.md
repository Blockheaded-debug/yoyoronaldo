# Signal Trading App Design Guidelines

## Design Approach
**Reference-Based Approach**: Drawing inspiration from professional trading platforms like TradingView, Binance, and Coinbase Pro, combined with modern fintech aesthetics from companies like Robinhood and Stripe.

**Key Design Principles:**
- Data-first hierarchy with clear visual emphasis on trading signals
- Professional, trustworthy aesthetic suitable for financial applications
- Efficient information density without overwhelming users
- Strong contrast for critical trading information (BUY/SELL/HOLD signals)

## Core Design Elements

### A. Color Palette
**Dark Mode Primary (Trading Focus):**
- Background: 220 15% 8% (deep charcoal)
- Surface: 220 12% 12% (elevated cards)
- Primary: 174 100% 40% (neon lightning glow dark tosca green for profits/buy signals)
- Danger: 0 84% 60% (clear red for sell signals)
- Warning: 38 92% 50% (amber for hold/neutral signals)
- Text Primary: 220 15% 95% (high contrast white)
- Text Secondary: 220 10% 70% (muted text)

**Light Mode:**
- Background: 220 20% 98% (clean white)
- Surface: 220 15% 96% (subtle gray cards)
- Primary: 174 100% 25% (neon lightning glow dark tosca green for accessibility)
- Same danger/warning colors with adjusted lightness

### B. Typography
**Font Stack:** Inter via Google Fonts CDN
- Headers: 600-700 weight, tight letter spacing
- Body: 400-500 weight for readability
- Data/Numbers: 500-600 weight, tabular figures for alignment
- Critical Signals: 700 weight, larger size for prominence

### C. Layout System
**Tailwind Spacing Units:** 2, 4, 8, 12, 16
- Micro spacing: p-2, gap-2
- Component spacing: p-4, m-4, gap-4
- Section spacing: p-8, my-8
- Page margins: px-12, py-16

### D. Component Library

**Navigation:**
- Fixed header with trading pair selector
- Sidebar navigation for different analysis tools
- Breadcrumb navigation for complex workflows

**Forms:**
- Trading pair input with autocomplete
- Time frame selectors (1H, 4H, 1D, 1W buttons)
- Analysis trigger buttons with loading states

**Data Displays:**
- Signal cards with color-coded backgrounds (green/red/amber)
- Technical indicator tables with zebra striping
- Price charts with overlay indicators
- Real-time price tickers

**Cards & Containers:**
- Elevated cards for analysis results
- Bordered containers for form sections
- Full-width dashboard layouts

**Interactive Elements:**
- Primary buttons for trading actions
- Ghost buttons for secondary actions
- Toggle switches for indicator selections
- Dropdown selectors for market pairs

### E. Trading-Specific Enhancements

**Signal Visualization:**
- Large, prominent signal badges (BUY/SELL/HOLD)
- Color-coded indicator cards with trend arrows
- Confidence percentage displays
- Historical signal accuracy metrics

**Dashboard Layout:**
- Multi-column grid for various indicators
- Sticky header with current pair information
- Quick access toolbar for common trading pairs
- Real-time status indicators

**Data Tables:**
- Sortable columns for historical analysis
- Color-coded rows based on signal strength
- Expandable rows for detailed indicator breakdown
- Export functionality for analysis results

## Images
No large hero images required. This is a utility-focused trading application where data visualization takes precedence. Any imagery should be:
- Small logo/branding in header
- Icon-based illustrations for empty states
- Chart thumbnails for analysis previews
- Subtle background patterns for visual interest without distraction

## Accessibility & Usability
- High contrast ratios for critical trading information
- Consistent dark mode implementation across all components
- Keyboard navigation for power users
- Screen reader friendly data tables
- Clear visual hierarchy for rapid information scanning
- Mobile-responsive layouts for monitoring on-the-go

The design should feel professional, trustworthy, and efficient - prioritizing quick access to trading signals while maintaining visual clarity for complex financial data.