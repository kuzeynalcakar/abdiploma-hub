# ABDiploma Hub — Component Inventory

This document lists every reusable UI component for ABDiploma Hub. Screens must compose these components rather than building one-off UI.

**Scope:** Login, Dashboard, Quiz, Practice, Weakness Map, Options — as defined in `INFORMATION_ARCHITECTURE.md`.

**Rules:**

- Reuse components listed here before creating new ones.
- Do not add components for features outside the six screens.
- Props describe data and callbacks only — no business logic inside components.

---

## Layout

Components that define page structure.

### AppLayout

**Purpose:** Wraps authenticated screens (Dashboard, Quiz, Practice, Weakness Map, Options) with a fixed sidebar, header, and scrollable main content area.

**Props:**

| Prop | Type | Description |
|------|------|-------------|
| `pageTitle` | string | Title shown in the header |
| `children` | node | Main page content |

**States:**

| State | Description |
|-------|-------------|
| Default | Sidebar visible, header visible, content scrolls |
| Mobile | Sidebar hidden or overlaid; content full-width (layout behavior only, no animation) |

**Reusable?** Yes — all authenticated screens.

---

### LoginLayout

**Purpose:** Centers the login form on a white background without sidebar or header.

**Props:**

| Prop | Type | Description |
|------|------|-------------|
| `children` | node | Login form content |

**States:**

| State | Description |
|-------|-------------|
| Default | Single-column, vertically centered content |

**Reusable?** Yes — Login only.

---

## Navigation

Components for moving between the six screens.

### Sidebar

**Purpose:** Fixed left navigation with links to Dashboard, Quiz, Practice, Weakness Map, and Options.

**Props:**

| Prop | Type | Description |
|------|------|-------------|
| `activePath` | string | Current route, used to highlight the active item |
| `items` | array | Nav entries: `label`, `path`, `icon` |

**States:**

| State | Description |
|-------|-------------|
| Default | All items visible, one item active |
| Active item | Accent background and text on current route |

**Reusable?** Yes — via `AppLayout` on all authenticated screens.

---

### SidebarNavItem

**Purpose:** Single sidebar row with icon and label.

**Props:**

| Prop | Type | Description |
|------|------|-------------|
| `label` | string | Nav label |
| `path` | string | Route path |
| `icon` | node | Simple line icon |
| `isActive` | boolean | Whether this item matches the current route |

**States:**

| State | Description |
|-------|-------------|
| Default | Muted icon and text |
| Active | Accent background and text |
| Hover | Neutral raised background |

**Reusable?** Yes — used inside `Sidebar`.

---

### Header

**Purpose:** Minimal top bar with page title and user avatar placeholder.

**Props:**

| Prop | Type | Description |
|------|------|-------------|
| `title` | string | Current page title |

**States:**

| State | Description |
|-------|-------------|
| Default | Title left, avatar right |

**Reusable?** Yes — via `AppLayout` on all authenticated screens.

---

### Avatar

**Purpose:** User avatar placeholder in the header.

**Props:**

| Prop | Type | Description |
|------|------|-------------|
| `initials` | string | Optional one- or two-character initials |

**States:**

| State | Description |
|-------|-------------|
| Default | Circular placeholder with generic icon or initials |
| Empty | Generic user icon when no initials provided |

**Reusable?** Yes — used inside `Header`.

---

## Actions

Interactive controls for user actions.

### Button

**Purpose:** Primary user actions across all screens. Variants match `DESIGN_SYSTEM.md`.

**Props:**

| Prop | Type | Description |
|------|------|-------------|
| `variant` | `"primary"` \| `"secondary"` \| `"ghost"` | Visual style |
| `label` | string | Button text |
| `onClick` | function | Click handler |
| `disabled` | boolean | Prevents interaction |
| `type` | `"button"` \| `"submit"` | HTML button type for forms |

**States:**

| State | Description |
|-------|-------------|
| Default | Normal appearance per variant |
| Hover | Variant-specific hover color |
| Disabled | Muted appearance, not clickable |
| Focus | Accent focus ring |

**Reusable?** Yes — Login, Dashboard, Quiz, Practice, Weakness Map, Options.

---

### IconButton

**Purpose:** Small icon-only control. Used for the optional show/hide password toggle on Login.

**Props:**

| Prop | Type | Description |
|------|------|-------------|
| `icon` | node | Show or hide icon |
| `label` | string | Accessible name (e.g. "Show password") |
| `onClick` | function | Click handler |
| `disabled` | boolean | Prevents interaction |

**States:**

| State | Description |
|-------|-------------|
| Default | Ghost-style, transparent background |
| Hover | Neutral raised background |
| Disabled | Muted, not clickable |

**Reusable?** Yes — Login (`PasswordField`); available anywhere a compact icon action is needed.

---

## Forms

Input components for Login and Options.

### FormField

**Purpose:** Wraps a label, control, and optional error message with consistent spacing.

**Props:**

| Prop | Type | Description |
|------|------|-------------|
| `label` | string | Field label |
| `error` | string | Optional error message below the control |
| `required` | boolean | Shows required indicator on label |
| `children` | node | Input control (`TextField`, `PasswordField`, or `Toggle`) |

**States:**

| State | Description |
|-------|-------------|
| Default | Label above control, no error |
| Error | Error message visible below control |

**Reusable?** Yes — Login, Options.

---

### TextField

**Purpose:** Single-line text input for email and basic preference fields.

**Props:**

| Prop | Type | Description |
|------|------|-------------|
| `value` | string | Current value |
| `onChange` | function | Value change handler |
| `placeholder` | string | Placeholder text |
| `type` | `"text"` \| `"email"` | Input type |
| `disabled` | boolean | Read-only interaction |
| `name` | string | Form field name |

**States:**

| State | Description |
|-------|-------------|
| Default | Empty or filled, neutral border |
| Focus | Accent border and ring |
| Disabled | Muted background and text |
| Error | Error border (via parent `FormField`) |

**Reusable?** Yes — Login (email), Options (preference fields).

---

### PasswordField

**Purpose:** Password input with optional show/hide visibility toggle.

**Props:**

| Prop | Type | Description |
|------|------|-------------|
| `value` | string | Current value |
| `onChange` | function | Value change handler |
| `placeholder` | string | Placeholder text |
| `showToggle` | boolean | Whether to render the visibility `IconButton` |
| `name` | string | Form field name |

**States:**

| State | Description |
|-------|-------------|
| Default | Masked characters |
| Visible | Characters shown when toggle is active |
| Focus | Accent border and ring |
| Error | Error border (via parent `FormField`) |

**Reusable?** Yes — Login.

---

### Toggle

**Purpose:** On/off control for basic preference settings on Options.

**Props:**

| Prop | Type | Description |
|------|------|-------------|
| `label` | string | Preference name |
| `checked` | boolean | Current value |
| `onChange` | function | Change handler |
| `disabled` | boolean | Prevents interaction |

**States:**

| State | Description |
|-------|-------------|
| Off | Neutral track |
| On | Accent track |
| Disabled | Muted, not interactive |

**Reusable?** Yes — Options.

---

## Feedback & Status

Messages, loading, and empty states shared across screens.

### Alert

**Purpose:** Displays form-level or page-level messages (e.g. invalid credentials on Login).

**Props:**

| Prop | Type | Description |
|------|------|-------------|
| `variant` | `"error"` \| `"success"` \| `"warning"` | Semantic color |
| `message` | string | Alert text |

**States:**

| State | Description |
|-------|-------------|
| Visible | Colored background and text per variant |
| Hidden | Not rendered when `message` is empty |

**Reusable?** Yes — Login (invalid credentials), Options (save confirmation if shown).

---

### FeedbackMessage

**Purpose:** Shows immediate correct/incorrect feedback after checking an answer on Practice.

**Props:**

| Prop | Type | Description |
|------|------|-------------|
| `variant` | `"success"` \| `"error"` | Correct or incorrect |
| `message` | string | Short feedback text (e.g. "Correct" / "Incorrect") |
| `explanation` | string | Optional explanation shown when provided |

**States:**

| State | Description |
|-------|-------------|
| Hidden | Not shown until answer is checked |
| Success | Green styling |
| Error | Red styling |

**Reusable?** Yes — Practice.

---

### EmptyState

**Purpose:** Placeholder when a screen has no content to show yet.

**Props:**

| Prop | Type | Description |
|------|------|-------------|
| `title` | string | Short heading (e.g. "No activity yet") |
| `description` | string | Supporting message |
| `actionLabel` | string | Optional button label |
| `onAction` | function | Optional button handler |

**States:**

| State | Description |
|-------|-------------|
| Default | Centered muted text with optional action |
| With action | Includes a secondary or primary `Button` |

**Reusable?** Yes — Dashboard (no progress), Quiz (no quiz available), Practice (no questions), Weakness Map (no data).

---

### LoadingPlaceholder

**Purpose:** Simple placeholder while content is loading (e.g. Quiz mid-load).

**Props:**

| Prop | Type | Description |
|------|------|-------------|
| `message` | string | Optional waiting text |

**States:**

| State | Description |
|-------|-------------|
| Loading | Neutral skeleton blocks or spinner |

**Reusable?** Yes — Quiz (mid-load).

---

## Cards & Surfaces

Container components for grouped content.

### Card

**Purpose:** White bordered container with light shadow. Base surface for grouped content on every screen except Login.

**Props:**

| Prop | Type | Description |
|------|------|-------------|
| `title` | string | Optional card heading |
| `children` | node | Card body content |

**States:**

| State | Description |
|-------|-------------|
| Default | White background, thin border, small shadow |
| Interactive | Optional hover background when the whole card is clickable |

**Reusable?** Yes — Dashboard, Quiz, Practice, Weakness Map, Options.

---

### EntryCard

**Purpose:** Dashboard entry point linking to Quiz, Practice, or Weakness Map. One purpose per card.

**Props:**

| Prop | Type | Description |
|------|------|-------------|
| `title` | string | Destination name |
| `description` | string | Short purpose text |
| `actionLabel` | string | Button or link label |
| `onAction` | function | Navigate to destination |

**States:**

| State | Description |
|-------|-------------|
| Default | Card with title, description, and action |
| Hover | Subtle neutral background on interactive area |

**Reusable?** Yes — Dashboard (Quiz, Practice, Weakness Map entry cards).

---

## Content Display

Read-only and structured content components.

### AppTitle

**Purpose:** Displays the app name on the Login screen.

**Props:**

| Prop | Type | Description |
|------|------|-------------|
| `title` | string | App name (e.g. "ABDiploma Hub") |

**States:**

| State | Description |
|-------|-------------|
| Default | Large readable heading |

**Reusable?** Yes — Login only.

---

### ReadOnlyText

**Purpose:** Displays a label and read-only value (e.g. account email on Options).

**Props:**

| Prop | Type | Description |
|------|------|-------------|
| `label` | string | Field label |
| `value` | string | Display value |

**States:**

| State | Description |
|-------|-------------|
| Default | Muted label, primary text value |

**Reusable?** Yes — Options (account email), Practice and Quiz (topic label when shown).

---

### ProgressSummary

**Purpose:** Read-only summary of recent or overall progress on the Dashboard.

**Props:**

| Prop | Type | Description |
|------|------|-------------|
| `items` | array | Stat entries: `label`, `value` |
| `emptyMessage` | string | Shown when there is no activity (e.g. "No activity yet") |

**States:**

| State | Description |
|-------|-------------|
| With data | Label/value pairs visible |
| Empty | Shows `emptyMessage` or zero values |

**Reusable?** Yes — Dashboard (inside a `Card`).

---

### ProgressIndicator

**Purpose:** Shows current position in a quiz session (e.g. "Question 3 of 10").

**Props:**

| Prop | Type | Description |
|------|------|-------------|
| `current` | number | Current question index (1-based) |
| `total` | number | Total question count |

**States:**

| State | Description |
|-------|-------------|
| Default | Text label showing current and total |

**Reusable?** Yes — Quiz.

---

## Quiz & Practice

Components shared by Quiz and Practice question flows.

### QuestionCard

**Purpose:** Contains a question prompt and its answer choices.

**Props:**

| Prop | Type | Description |
|------|------|-------------|
| `questionText` | string | Question prompt |
| `topicLabel` | string | Optional topic or filter label |
| `children` | node | `AnswerChoiceGroup` content |

**States:**

| State | Description |
|-------|-------------|
| Default | Question text above answer choices |
| Answered | Choices reflect selection (Quiz: pending submit; Practice: after check) |

**Reusable?** Yes — Quiz, Practice.

---

### AnswerChoiceGroup

**Purpose:** Groups selectable answer options for a single question.

**Props:**

| Prop | Type | Description |
|------|------|-------------|
| `choices` | array | Options: `id`, `label` |
| `selectedId` | string | Currently selected choice id |
| `onSelect` | function | Selection handler |
| `disabled` | boolean | Prevents further selection after submit or check |

**States:**

| State | Description |
|-------|-------------|
| Default | No selection |
| Selected | One choice highlighted |
| Disabled | Selection locked |

**Reusable?** Yes — Quiz, Practice.

---

### AnswerChoice

**Purpose:** Single selectable answer option with a large tap target.

**Props:**

| Prop | Type | Description |
|------|------|-------------|
| `label` | string | Answer text |
| `isSelected` | boolean | Whether this choice is selected |
| `onSelect` | function | Selection handler |
| `disabled` | boolean | Prevents interaction |

**States:**

| State | Description |
|-------|-------------|
| Default | Neutral border |
| Selected | Accent border and subtle background |
| Disabled | Muted, not clickable |

**Reusable?** Yes — used inside `AnswerChoiceGroup`.

---

### ResultsSummary

**Purpose:** Displays score and summary after a quiz session ends.

**Props:**

| Prop | Type | Description |
|------|------|-------------|
| `scoreLabel` | string | Summary heading |
| `scoreValue` | string | Score or result text |
| `details` | array | Optional detail lines: `label`, `value` |

**States:**

| State | Description |
|-------|-------------|
| Default | Read-only results display |

**Reusable?** Yes — Quiz (inside a `Card` after completion).

---

## Weakness Map

Components specific to the Weakness Map screen.

### TopicList

**Purpose:** Vertical list of topics with weakness levels. Simplifies to a list on mobile when space is tight.

**Props:**

| Prop | Type | Description |
|------|------|-------------|
| `topics` | array | Topic entries: `id`, `name`, `weaknessLevel` |
| `selectedId` | string | Currently selected topic id |
| `onSelect` | function | Topic selection handler |

**States:**

| State | Description |
|-------|-------------|
| Default | List of topics |
| Empty | Renders `EmptyState` when `topics` is empty |
| Selected | One topic highlighted |

**Reusable?** Yes — Weakness Map.

---

### TopicListItem

**Purpose:** Single row in the weakness topic list with a weakness indicator.

**Props:**

| Prop | Type | Description |
|------|------|-------------|
| `name` | string | Topic name |
| `weaknessLevel` | string | Weakness level value for display |
| `isSelected` | boolean | Whether this topic is selected |
| `onSelect` | function | Selection handler |

**States:**

| State | Description |
|-------|-------------|
| Default | Name and weakness indicator |
| Selected | Accent subtle background |

**Reusable?** Yes — used inside `TopicList`.

---

### WeaknessIndicator

**Purpose:** Visual marker for how weak or strong a topic is.

**Props:**

| Prop | Type | Description |
|------|------|-------------|
| `level` | string | Weakness level (display only; styling maps level to color/intensity) |

**States:**

| State | Description |
|-------|-------------|
| Default | Flat color bar or badge per level |

**Reusable?** Yes — Weakness Map (`TopicListItem`, `TopicDetail`).

---

### WeaknessLegend

**Purpose:** Key explaining strength vs weakness levels on the Weakness Map.

**Props:**

| Prop | Type | Description |
|------|------|-------------|
| `items` | array | Legend entries: `label`, `level` |

**States:**

| State | Description |
|-------|-------------|
| Default | Row of labeled indicators |

**Reusable?** Yes — Weakness Map.

---

### TopicDetail

**Purpose:** Shows name and weakness indicator for the selected topic, with a path to practice that topic.

**Props:**

| Prop | Type | Description |
|------|------|-------------|
| `name` | string | Selected topic name |
| `weaknessLevel` | string | Weakness level for the topic |
| `onPractice` | function | Navigate to Practice for this topic |

**States:**

| State | Description |
|-------|-------------|
| Default | Topic name, indicator, and "Practice this topic" action |
| Hidden | Not rendered when no topic is selected |

**Reusable?** Yes — Weakness Map (inside a `Card`).

---

## Screen-to-Component Map

Which components each screen uses. Screens should not introduce components outside this inventory.

| Component | Login | Dashboard | Quiz | Practice | Weakness Map | Options |
|-----------|:-----:|:---------:|:----:|:--------:|:------------:|:-------:|
| AppLayout | | ✓ | ✓ | ✓ | ✓ | ✓ |
| LoginLayout | ✓ | | | | | |
| Sidebar | | ✓ | ✓ | ✓ | ✓ | ✓ |
| SidebarNavItem | | ✓ | ✓ | ✓ | ✓ | ✓ |
| Header | | ✓ | ✓ | ✓ | ✓ | ✓ |
| Avatar | | ✓ | ✓ | ✓ | ✓ | ✓ |
| Button | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| IconButton | ✓ | | | | | |
| FormField | ✓ | | | | | ✓ |
| TextField | ✓ | | | | | ✓ |
| PasswordField | ✓ | | | | | |
| Toggle | | | | | | ✓ |
| Alert | ✓ | | | | | ✓ |
| FeedbackMessage | | | | ✓ | | |
| EmptyState | | ✓ | ✓ | ✓ | ✓ | |
| LoadingPlaceholder | | | ✓ | | | |
| Card | | ✓ | ✓ | ✓ | ✓ | ✓ |
| EntryCard | | ✓ | | | | |
| AppTitle | ✓ | | | | | |
| ReadOnlyText | | | ✓ | ✓ | | ✓ |
| ProgressSummary | | ✓ | | | | |
| ProgressIndicator | | | ✓ | | | |
| QuestionCard | | | ✓ | ✓ | | |
| AnswerChoiceGroup | | | ✓ | ✓ | | |
| AnswerChoice | | | ✓ | ✓ | | |
| ResultsSummary | | | ✓ | | | |
| TopicList | | | | | ✓ | |
| TopicListItem | | | | | ✓ | |
| WeaknessIndicator | | | | | ✓ | |
| WeaknessLegend | | | | | ✓ | |
| TopicDetail | | | | | ✓ | |

---

## Out of Scope

Do not create components for:

- Chat or AI assistant
- Notifications
- Leaderboard
- Confirmation dialogs (not defined in information architecture)
- Charts or 3D visualizations (Weakness Map uses a list with indicators)
- Search, breadcrumbs, or multi-step wizards
- Any screen beyond the six listed above

If a screen need arises that none of these components cover, update this document before building a new component.
