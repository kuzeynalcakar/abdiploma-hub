# ABDiploma Hub — Information Architecture

Scope: exactly six screens. No chat, AI assistant, notifications, or leaderboard.

---

## Login

### Purpose
- Authenticate the user so they can access the app.

### Components
- App name / title
- Email field
- Password field
- Form error message area

### Buttons
- Log in
- Show / hide password (optional control on the password field)

### Cards
- None

### Navigation
- Successful login → Dashboard
- No other in-app destinations from this screen

### Empty state
- Default: empty email and password fields
- Invalid credentials: inline error; fields remain editable

### Mobile behavior
- Single-column form
- Full-width fields and primary button
- Keyboard-friendly spacing; no side panels

---

## Dashboard

### Purpose
- Home overview after login; entry point to the main areas of the app.

### Components
- Page title
- Short summary of recent or overall progress (read-only)
- Links or entry points to Quiz, Practice, Weakness Map, and Options

### Buttons
- Start Quiz
- Practice
- Weakness Map
- Options (or equivalent nav control)

### Cards
- Progress summary card
- Entry cards for Quiz, Practice, and Weakness Map (one purpose each)

### Navigation
- Quiz → Quiz
- Practice → Practice
- Weakness Map → Weakness Map
- Options → Options
- Shared app navigation may also reach these screens

### Empty state
- No progress yet: summary shows zeros or “No activity yet”
- Entry cards remain available so the user can start

### Mobile behavior
- Stacked vertical layout
- Full-width cards
- Primary actions easy to tap; no multi-column grid required

---

## Quiz

### Purpose
- Present a scored quiz session and record answers.

### Components
- Quiz title or topic label
- Progress indicator (e.g. question X of Y)
- Question text
- Answer choices
- Result summary after the quiz ends

### Buttons
- Submit answer / Next
- Finish quiz (on last question or when complete)
- Back to Dashboard (after results, or exit if allowed)

### Cards
- Question card (prompt + choices)
- Results card (score / summary after completion)

### Navigation
- From Dashboard (or shared nav) → Quiz
- After finish → stay on results, then Dashboard
- Shared nav may leave the quiz (confirm if mid-session, if confirmation is used)

### Empty state
- No quiz available: message that no quiz is ready; action to return to Dashboard
- Mid-load: simple loading placeholder (no content invented beyond waiting)

### Mobile behavior
- One question visible at a time
- Full-width choices; large tap targets
- Sticky or bottom-placed primary action when needed

---

## Practice

### Purpose
- Let the user practice questions without treating the session as a full scored quiz run.

### Components
- Topic or filter label (if a topic is selected)
- Question text
- Answer choices
- Immediate feedback after an answer (correct / incorrect)
- Optional short explanation area when feedback is shown

### Buttons
- Check answer
- Next question
- Back to Dashboard

### Cards
- Practice question card
- Feedback card or inline feedback block after checking

### Navigation
- From Dashboard (or shared nav) → Practice
- Back / nav → Dashboard
- No link to chat or other unlisted screens

### Empty state
- No practice questions available: message and return to Dashboard
- No topic selected (if selection exists): prompt to choose a topic before questions appear

### Mobile behavior
- Single-column question flow
- Full-width controls
- Feedback appears below the question without overlapping content

---

## Weakness Map

### Purpose
- Show where the user is weak by topic or skill so they know what to practice.

### Components
- Page title
- Map or list of topics with weakness level
- Legend or key for strength vs weakness
- Selected topic detail (name + weakness indicator)

### Buttons
- Practice this topic (goes to Practice for that topic, when a topic is selected)
- Back to Dashboard

### Cards
- Topic weakness card (per topic, or one detail card for the selected topic)
- Empty / no-data card when there is nothing to show

### Navigation
- From Dashboard (or shared nav) → Weakness Map
- Practice this topic → Practice
- Back / nav → Dashboard

### Empty state
- No data yet: “Complete quizzes or practice to see your weakness map”
- CTA: Practice or Dashboard

### Mobile behavior
- Map simplifies to a vertical list of topics if space is tight
- Full-width topic rows/cards
- Detail and actions stack below the list

---

## Options

### Purpose
- Let the user view and change basic account or app preferences, and sign out.

### Components
- Page title
- Preference fields or toggles (only basic settings; none invented beyond preferences + account)
- Account email (read-only display)

### Buttons
- Save changes
- Log out
- Back to Dashboard

### Cards
- Preferences card
- Account card (email + log out)

### Navigation
- From Dashboard (or shared nav) → Options
- Log out → Login
- Back / nav → Dashboard

### Empty state
- Preferences show current defaults when nothing has been customized
- No settings list beyond what the product later defines; screen still shows account + log out

### Mobile behavior
- Single-column settings stack
- Full-width inputs and buttons
- Log out clearly separated from preference controls
