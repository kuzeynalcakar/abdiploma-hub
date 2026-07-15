# Review Context — SPEC-0003 Application Shell Refactor

This document captures the current state of the ABDiploma Hub application shell after the SPEC-0003 revision. It is intended for reviewers and future contributors.

---

## Current Folder Structure

```
AlbertaPrep/
├── AI_RULES.md
├── COMPONENT_INVENTORY.md
├── DESIGN_SYSTEM.md
├── INFORMATION_ARCHITECTURE.md
├── REVIEW_CONTEXT.md
└── frontend/
    ├── index.html
    ├── package.json
    ├── package-lock.json
    ├── vite.config.js
    ├── dist/                          # Build output (generated)
    │   ├── index.html
    │   └── assets/
    ├── node_modules/                  # Dependencies (not source)
    └── src/
        ├── main.jsx                   # React entry point
        ├── App.jsx                    # Root component (BrowserRouter)
        ├── index.css                  # Global styles (Tailwind import)
        └── components/
            └── layout/
                ├── AppLayout.jsx      # Authenticated page shell
                ├── Sidebar.jsx        # Fixed left navigation
                ├── SidebarNavItem.jsx # Single sidebar nav row
                ├── Header.jsx         # Top bar with title and avatar
                └── Avatar.jsx         # User avatar placeholder
```

**Notes:**

- All layout components live under `frontend/src/components/layout/`.
- No screen components (Login, Dashboard, Quiz, etc.) exist yet.
- No backend or API layer exists yet.
- Specification documents live at the repository root.

---

## Modified Files (SPEC-0003 Revision)

The following files were created or changed during the application shell refactor. No other application code was touched.

### Created

| File | Change |
|------|--------|
| `frontend/src/components/layout/Avatar.jsx` | Extracted avatar placeholder from `Header.jsx` into a reusable component. |
| `frontend/src/components/layout/SidebarNavItem.jsx` | Extracted single nav row from `Sidebar.jsx` into a reusable component. |

### Modified

| File | Change |
|------|--------|
| `frontend/src/components/layout/Header.jsx` | Replaced inline avatar `<div>` with `<Avatar />`. |
| `frontend/src/components/layout/Sidebar.jsx` | Replaced inline `NavLink` rows with `<SidebarNavItem />`; removed direct `NavLink` import. |

### Unchanged (part of shell, not modified in this revision)

| File | Role |
|------|------|
| `frontend/src/components/layout/AppLayout.jsx` | Shell wrapper — composes `Sidebar` and `Header`. |
| `frontend/src/App.jsx` | Root router setup only. |
| `frontend/src/main.jsx` | React bootstrap. |
| `frontend/src/index.css` | Tailwind import. |

---

## Component Responsibilities

### Layout layer

#### `AppLayout`

- **Purpose:** Wraps authenticated screens with a fixed sidebar, header, and scrollable main content area.
- **Props:** `pageTitle` (string), `children` (node).
- **Owns:** Mobile sidebar open/close state (`isSidebarOpen`).
- **Composes:** `Sidebar`, `Header`, and a `<main>` content slot.
- **Does not:** Contain business logic, routing definitions, or screen content.

#### `Sidebar`

- **Purpose:** Fixed left navigation for authenticated screens.
- **Props:** `isOpen` (boolean), `onClose` (function).
- **Owns:** Static `NAV_ITEMS` list (Dashboard, Quiz, Practice, Weakness Map, Options).
- **Composes:** `SidebarNavItem` for each nav entry.
- **Behavior:**
  - Desktop (`md:` and up): always visible, fixed 240px width (`w-60`).
  - Mobile: hidden by default; shown as overlay when `isOpen` is true; backdrop click calls `onClose`.
- **Does not:** Accept `activePath` or `items` props yet (inventory defines these for future use).

#### `SidebarNavItem`

- **Purpose:** Single sidebar navigation row.
- **Props:** `label` (string), `path` (string), `onClick` (function).
- **Renders:** A `NavLink` from `react-router-dom` with active/hover styling.
- **Active state:** Determined by `NavLink`'s `isActive` — accent background (`bg-blue-50`) and accent text (`text-blue-600`).
- **Default state:** Muted text (`text-gray-500`), hover raised background (`hover:bg-gray-100`).
- **Does not:** Render icons (not present in current implementation; inventory reserves `icon` prop for later).

#### `Header`

- **Purpose:** Minimal top bar with page title and user avatar.
- **Props:** `title` (string), `onMenuClick` (function).
- **Composes:** `<Avatar />` on the right; hamburger menu button on mobile (left of title).
- **Layout:** Sticky, 56px height (`h-14`), white background, bottom border.
- **Does not:** Include search, notifications, breadcrumbs, or user menu.

#### `Avatar`

- **Purpose:** User avatar placeholder in the header.
- **Props:** `initials` (string, optional) — rendered as children when provided.
- **Default:** Empty circular placeholder (`h-8 w-8`, `rounded-full`, `bg-gray-100`, `text-gray-400`).
- **Accessibility:** `role="img"`, `aria-label="User avatar"`.
- **Does not:** Fetch user data or handle click interactions.

### Application entry

#### `App`

- **Purpose:** Root component; provides `BrowserRouter`.
- **Current state:** No routes defined yet.

#### `main`

- **Purpose:** Mounts React app in `StrictMode`, imports global CSS.

---

## Current Architecture Decisions

### Stack

| Layer | Choice |
|-------|--------|
| Framework | React 19 (functional components, JavaScript only) |
| Build tool | Vite 8 |
| Styling | Tailwind CSS 4 (via `@tailwindcss/vite` plugin) |
| Routing | React Router DOM 7 (`BrowserRouter`, `NavLink`) |
| Linting | oxlint |

### UI and styling rules

- **Tailwind only** — no inline styles, no UI component libraries.
- **Design tokens** follow `DESIGN_SYSTEM.md`: white background, neutral grays, blue accent, 8px spacing grid.
- **No icons** in the current shell (hamburger uses CSS bars; nav items are label-only).
- **No animations** on sidebar or nav items.
- **No gradients, glassmorphism, or decorative effects.**

### Component architecture

- **Composition over duplication** — `Avatar` and `SidebarNavItem` are extracted per `COMPONENT_INVENTORY.md`; parent components compose them rather than inlining markup.
- **Single responsibility** — each layout component owns one concern (shell structure, sidebar list, nav row, header bar, avatar placeholder).
- **Props are presentational** — components accept data and callbacks only; no business logic or fake data inside components.
- **Folder convention** — layout components grouped under `components/layout/`.

### Layout behavior

- **Desktop:** Sidebar fixed left at 240px; main content offset with `md:pl-60`.
- **Mobile:** Sidebar hidden; hamburger in header opens overlay sidebar with backdrop; nav click closes sidebar via `onClose`.
- **Header:** Sticky within the content column; does not scroll away.
- **Content area:** Padded `p-6` mobile, `md:p-8` desktop.

### Routing

- `BrowserRouter` is mounted at the app root.
- Nav paths are defined in `Sidebar` as static constants: `/dashboard`, `/quiz`, `/practice`, `/weakness-map`, `/options`.
- Route components and a `LoginLayout` are not implemented yet.

### Specification alignment

| Document | Governs |
|----------|---------|
| `AI_RULES.md` | Coding standards (JS, functional components, Tailwind, no inline styles) |
| `DESIGN_SYSTEM.md` | Visual tokens, spacing, typography, component appearance |
| `INFORMATION_ARCHITECTURE.md` | Six screens and their content/navigation scope |
| `COMPONENT_INVENTORY.md` | Reusable component list, props, and screen-to-component map |

### Intentional gaps (not yet built)

- Screen components (Login, Dashboard, Quiz, Practice, Weakness Map, Options)
- `LoginLayout`
- Route definitions in `App.jsx`
- `Sidebar` props `activePath` and `items` (inventory spec; current impl uses internal `NAV_ITEMS` and `NavLink` auto-active)
- `SidebarNavItem` `icon` and `isActive` props (inventory spec; current impl derives active state from `NavLink`)
- Authentication, API integration, and state management
- Remaining inventory components (Button, Card, FormField, etc.)

### Refactor constraints honored (SPEC-0003)

- UI, styling, and layout unchanged — refactor was structural only.
- No unrelated files modified.
- Duplicated JSX eliminated (avatar block, nav row template).
- `Header` and `Sidebar` reduced in size by delegating to child components.

---

## Component Dependency Graph

```
App (BrowserRouter)
└── (future routes)
    └── AppLayout
        ├── Sidebar
        │   └── SidebarNavItem (×5)
        └── Header
            └── Avatar
```

---

## Review Checklist

When reviewing the shell refactor, confirm:

- [ ] `Avatar.jsx` and `SidebarNavItem.jsx` exist under `components/layout/`
- [ ] `Header.jsx` imports and renders `<Avatar />`
- [ ] `Sidebar.jsx` maps `NAV_ITEMS` to `<SidebarNavItem />` with no inline `NavLink` duplication
- [ ] Visual output matches pre-refactor shell (classes preserved verbatim)
- [ ] No business logic, fake data, icons, or inline CSS introduced
- [ ] `AppLayout.jsx` unchanged and still composes sidebar + header correctly
