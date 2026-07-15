# ABDiploma Hub — Design System

This document defines the visual language for ABDiploma Hub. All UI work should follow these guidelines.

**Stack:** Tailwind CSS. No inline styles. No React code in this document — tokens and rules only.

---

## Theme

ABDiploma Hub should feel:

| Quality | Expression |
|---------|------------|
| **Modern** | Clean layout, current spacing and type conventions, no dated effects |
| **Minimal** | Only what the screen needs; no decorative chrome |
| **Educational** | Readable, structured, calm focus on content and progress |
| **Calm** | Soft neutrals, restrained accent use, no visual noise |
| **Professional** | Consistent, trustworthy, suitable for exam preparation |

Design for clarity first. Every element should earn its place.

---

## Colors

### Principles

- **White** is the default page background.
- **Neutral grays** define surfaces, borders, and secondary text.
- **Blue** is the only accent color — used for links, primary actions, active states, and focus rings.
- **Semantic colors** (green, amber, red) are reserved for success, warning, and error feedback only.

### Palette

| Token | Hex | Usage |
|-------|-----|-------|
| `background` | `#FFFFFF` | Page and main content area |
| `surface` | `#F9FAFB` | Subtle alternate backgrounds, table headers, sidebar |
| `surface-raised` | `#F3F4F6` | Hover states on neutral surfaces, disabled backgrounds |
| `border` | `#E5E7EB` | Card borders, dividers, input outlines |
| `border-strong` | `#D1D5DB` | Emphasized separators, table borders |
| `text-primary` | `#111827` | Headings, body copy, table data |
| `text-secondary` | `#6B7280` | Supporting text, descriptions |
| `text-muted` | `#9CA3AF` | Labels, placeholders, metadata |
| `accent` | `#2563EB` | Primary buttons, links, active nav, focus rings |
| `accent-hover` | `#1D4ED8` | Primary button hover |
| `accent-subtle` | `#EFF6FF` | Selected row backgrounds, active nav tint |
| `success` | `#16A34A` | Correct answers, success messages, positive trends |
| `success-subtle` | `#F0FDF4` | Success alert backgrounds |
| `warning` | `#D97706` | Caution states, incomplete items |
| `warning-subtle` | `#FFFBEB` | Warning alert backgrounds |
| `error` | `#DC2626` | Form errors, incorrect answers, destructive emphasis |
| `error-subtle` | `#FEF2F2` | Error alert backgrounds |

### Rules

- Do not introduce purple, pink, teal, or other accent hues.
- Do not use color alone to convey meaning — pair with text or icons.
- Keep accent usage purposeful; most of the UI should remain neutral.

---

## Typography

### Font

Use **one font family** across the entire application:

**Inter** — with system fallbacks: `Inter, ui-sans-serif, system-ui, sans-serif`

Load Inter via a single `@font-face` or CDN import in the global stylesheet. Do not mix serif, mono, or display fonts in the UI (mono may appear only inside code snippets if ever needed).

### Type scale

| Token | Size | Weight | Line height | Usage |
|-------|------|--------|-------------|-------|
| `heading-xl` | 30px (1.875rem) | 600 | 1.25 | Page titles |
| `heading-lg` | 24px (1.5rem) | 600 | 1.3 | Section headings |
| `heading-md` | 20px (1.25rem) | 600 | 1.35 | Card titles, subsections |
| `heading-sm` | 16px (1rem) | 600 | 1.4 | Table column headers, compact headings |
| `body` | 16px (1rem) | 400 | 1.5 | Paragraphs, form values, table cells |
| `body-sm` | 14px (0.875rem) | 400 | 1.5 | Secondary content, button labels |
| `label` | 12px (0.75rem) | 500 | 1.4 | Form labels, badges, metadata |
| `label-muted` | 12px (0.75rem) | 400 | 1.4 | Timestamps, helper hints |

### Rules

- Headings are **large and readable** — never below 16px for visible titles.
- Body text stays at **16px** for comfortable reading during study sessions.
- Labels are **small and muted** — use `text-muted` color, not reduced body size alone.
- Do not use more than two weights in a single component (typically 400 and 600).
- Sentence case for UI labels; title case only for proper nouns and page titles.

---

## Spacing

Use an **8px base unit**. All margins, padding, and gaps should be multiples of 8px.

| Token | Value | Common use |
|-------|-------|------------|
| `space-1` | 8px | Tight internal padding, icon gaps |
| `space-2` | 16px | Input padding, compact card padding |
| `space-3` | 24px | Card padding, form field spacing |
| `space-4` | 32px | Section spacing within a page |
| `space-5` | 40px | Large section breaks |
| `space-6` | 48px | Page-level vertical rhythm |
| `space-8` | 64px | Major layout separation |

### Layout defaults

- Page content padding: `24px` (mobile), `32px` (desktop).
- Gap between stacked cards: `16px` or `24px`.
- Form field vertical spacing: `16px`.
- Sidebar width: `240px`.

Avoid odd values (10px, 12px, 14px, 20px) unless aligning to an icon's intrinsic size.

---

## Corners

Corners are **rounded but subtle** — enough to feel modern, not pill-shaped unless intentional (e.g., avatars).

| Token | Value | Usage |
|-------|-------|-------|
| `radius-sm` | 4px | Badges, small tags |
| `radius-md` | 6px | Buttons, inputs, table cells |
| `radius-lg` | 8px | Cards, modals, dropdowns |
| `radius-full` | 9999px | Avatars, circular icon buttons only |

Do not use large radius (16px+) on rectangular containers.

---

## Shadows

Shadows are **very light** — suggest elevation without drama.

| Token | Value | Usage |
|-------|-------|-------|
| `shadow-sm` | `0 1px 2px rgba(0, 0, 0, 0.05)` | Cards, dropdowns |
| `shadow-md` | `0 1px 3px rgba(0, 0, 0, 0.08), 0 1px 2px rgba(0, 0, 0, 0.04)` | Modals, popovers (rare) |

- Cards use `shadow-sm` only.
- Do not stack multiple shadow layers on one element.
- Never use colored or inset shadows.

---

## Buttons

Three variants. All buttons use `radius-md`, `body-sm` text, and `space-2` horizontal padding (minimum 16px vertical padding for touch targets).

### Primary

- Background: `accent`
- Text: white
- Hover: `accent-hover`
- Use for the single main action on a screen (e.g., Log in, Submit, Start Quiz).

### Secondary

- Background: white
- Border: 1px `border-strong`
- Text: `text-primary`
- Hover: `surface` background
- Use for alternative actions (e.g., Cancel, Back).

### Ghost

- Background: transparent
- Text: `text-secondary`
- Hover: `surface-raised` background
- Use for tertiary actions, toolbar items, sidebar nav items.

### Shared rules

- Minimum touch target: 40px height.
- Disabled: `surface-raised` background, `text-muted` text, no shadow, cursor not-allowed.
- One primary button per view when possible.
- No gradient fills, glow, or animated backgrounds on buttons.

---

## Cards

Cards group related content on Dashboard, Quiz, Practice, and similar screens.

| Property | Value |
|----------|-------|
| Background | white (`background`) |
| Border | 1px solid `border` |
| Shadow | `shadow-sm` |
| Radius | `radius-lg` |
| Padding | `space-3` (24px) |

- Do not nest cards inside cards.
- Card titles use `heading-md`; body uses `body` or `body-sm`.
- Interactive cards (entry points) may use a hover state: `surface` background, border unchanged.
- No gradient borders or glass effects.

---

## Sidebar

Fixed left navigation for authenticated screens.

| Property | Value |
|----------|-------|
| Position | Fixed, full viewport height |
| Width | 240px |
| Background | `surface` |
| Border | 1px right `border` |

### Navigation items

- Layout: icon + label, left-aligned.
- Icons: simple line icons (24px), `text-secondary` default, `accent` when active.
- Active item: `accent-subtle` background, `accent` text, no bold animation.
- Padding per item: `space-2` vertical, `space-2` horizontal.
- Gap between icon and label: `space-1`.

### Rules

- **No animations** — no slide-in, bounce, or transition effects on the sidebar or its items.
- No collapsible flyouts or mega-menus.
- Sidebar stays visible on desktop; on mobile, use a simple full-width overlay or bottom nav consistent with these same tokens (no animation requirement change for open/close — keep instant or a minimal 150ms fade if unavoidable).

---

## Header

Minimal top bar on authenticated screens.

| Property | Value |
|----------|-------|
| Height | 56px |
| Background | white |
| Border | 1px bottom `border` |
| Padding | `space-2` horizontal |

### Contents

1. **Page title** — `heading-md`, left-aligned (or centered on mobile if sidebar is hidden).
2. **User avatar placeholder** — right-aligned, 32px circle, `surface-raised` background, `text-muted` initials or generic user icon.

### Rules

- No breadcrumbs unless a screen explicitly requires them.
- No search bar, notifications bell, or extra actions in the header unless added to scope later.
- Header does not scroll away — it stays at the top of the content area (below or beside the fixed sidebar depending on layout).

---

## Forms

All inputs share one consistent style.

### Input fields

| Property | Value |
|----------|-------|
| Height | 40px |
| Padding | `space-2` horizontal |
| Background | white |
| Border | 1px `border-strong` |
| Radius | `radius-md` |
| Text | `body` |
| Placeholder | `text-muted` |

### States

- **Focus:** 2px ring in `accent`, border `accent`.
- **Error:** border `error`, helper text in `error` below the field (`body-sm`).
- **Disabled:** `surface-raised` background, `text-muted` text.

### Labels

- Positioned above the input.
- Style: `label`, color `text-secondary`.
- Required fields: append a muted asterisk — do not rely on color alone.

### Layout

- Full-width inputs on mobile.
- Max form width on desktop: 480px for login and settings; wider for data-heavy screens as needed.
- Error messages appear directly below the relevant field, not only at the top of the form.

---

## Tables

Clean, readable data presentation for progress, results, and lists.

| Element | Style |
|---------|-------|
| Header row | `surface` background, `heading-sm` text, `text-secondary` |
| Body rows | white background, `body` text |
| Borders | 1px `border` horizontal dividers; no vertical grid lines |
| Row height | 48px minimum |
| Cell padding | `space-2` horizontal, `space-1` vertical |
| Hover | `surface` background on interactive rows |

### Rules

- Left-align text; right-align numbers.
- Use zebra striping only if a table exceeds 10 rows — alternate `background` and `surface` at 5% opacity difference, not strong contrast.
- Empty state: centered `body-sm` muted message inside the table container, not a separate card.

---

## Charts

Used on Dashboard and Weakness Map for progress visualization.

### Style

- **Minimal** — axis lines, labels, and data marks only.
- **Flat colors** — solid fills from the palette (`accent`, `success`, `warning`, `error`, and neutral grays).
- **No 3D** — no depth, bevel, or perspective.
- **No gradients** — single flat color per series.

### Defaults

| Element | Style |
|---------|-------|
| Grid lines | `border` color, horizontal only, dashed optional |
| Axis labels | `label`, `text-muted` |
| Data lines / bars | 2px stroke or solid fill, `accent` for primary series |
| Tooltip | white card with `shadow-sm`, `border`, `body-sm` text |

- Limit chart palette to 4 series colors maximum: `accent`, `#6B7280`, `success`, `warning`.
- Prefer bar and line charts; avoid pie charts unless showing ≤4 categories.
- Include a text summary adjacent to or below the chart for accessibility.

---

## Motion and interaction

- **No fancy animations.** No parallax, spring physics, or staggered reveals.
- Instant state changes are preferred.
- If feedback is required, use a simple opacity or color change under 150ms — never bounce, shake, or pulse.
- Loading states: static skeleton blocks in `surface-raised` or a simple spinner in `accent` — no elaborate loaders.

---

## Prohibited patterns

Never use:

| Pattern | Reason |
|---------|--------|
| Glassmorphism | Conflicts with calm, professional tone |
| Neon / fluorescent colors | Too loud for educational focus |
| Bright non-semantic colors | Distracts from content |
| Fancy animations | Adds noise, slows comprehension |
| Complex backgrounds | Patterns, meshes, photos behind UI |
| Gradients | On buttons, cards, charts, or backgrounds |
| Multiple accent colors | Blue is the sole accent |
| Drop shadows heavier than `shadow-md` | Breaks minimal elevation model |
| Decorative illustrations in chrome | Keep art inside content areas only |

When in doubt, remove the element rather than decorate it.

---

## Tailwind mapping reference

Map tokens to Tailwind utilities consistently:

| Token | Tailwind equivalent |
|-------|---------------------|
| `background` | `bg-white` |
| `surface` | `bg-gray-50` |
| `surface-raised` | `bg-gray-100` |
| `border` | `border-gray-200` |
| `border-strong` | `border-gray-300` |
| `text-primary` | `text-gray-900` |
| `text-secondary` | `text-gray-500` |
| `text-muted` | `text-gray-400` |
| `accent` | `bg-blue-600` / `text-blue-600` |
| `accent-hover` | `bg-blue-700` |
| `accent-subtle` | `bg-blue-50` |
| `success` | `text-green-600` / `bg-green-600` |
| `warning` | `text-amber-600` / `bg-amber-600` |
| `error` | `text-red-600` / `bg-red-600` |
| `space-1` | `p-2`, `gap-2`, `m-2` |
| `space-2` | `p-4`, `gap-4`, `m-4` |
| `space-3` | `p-6`, `gap-6`, `m-6` |
| `radius-md` | `rounded-md` |
| `radius-lg` | `rounded-lg` |
| `shadow-sm` | `shadow-sm` |

Extend the Tailwind theme in configuration when exact hex values are needed; do not hardcode arbitrary colors in components.

---

## Checklist for new UI

Before shipping any screen or component, confirm:

- [ ] White background, neutral surfaces, blue accent only
- [ ] Inter (single font) with correct type scale
- [ ] Spacing in 8px multiples
- [ ] Subtle corners and light shadows
- [ ] Buttons use primary / secondary / ghost correctly
- [ ] Cards are white with thin border and small shadow
- [ ] Sidebar is fixed, icon-based, no animations
- [ ] Header is minimal — title and avatar only
- [ ] Forms match the shared input style
- [ ] Tables are clean with readable row height
- [ ] Charts are flat, minimal, no 3D or gradients
- [ ] No prohibited patterns
