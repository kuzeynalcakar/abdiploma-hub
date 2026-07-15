# Google Analytics 4 — Setup Guide for ABDiploma Hub

You do **not** need to change any code for this. ABDiploma Hub is already wired for GA4.  
You only need to create a Google Analytics property and paste the Measurement ID into a frontend env file.

---

## 1. Where to create the GA4 property

1. Open [https://analytics.google.com/](https://analytics.google.com/) and sign in with your Google account.
2. Click **Admin** (gear icon, bottom left).
3. Under **Account**, create an account if you do not have one (e.g. “ABDiploma Hub”).
4. Under **Property**, click **Create property**.
5. Property name: `ABDiploma Hub` (or similar).
6. Choose your reporting time zone (Canada — Mountain Time recommended for Alberta) and currency.
7. Click **Next**, answer the business questions, then **Create**.
8. When asked for a data stream, choose **Web**.
9. Website URL: your live ABDiploma Hub URL (e.g. `https://your-domain.com` — use your real domain).  
   For local testing you can still create the stream; events from localhost will appear in Realtime once the ID is set.
10. Stream name: `ABDiploma Hub Web`.
11. Click **Create stream**.

---

## 2. How to obtain the Measurement ID

1. After the web stream is created, open **Admin → Data streams → ABDiploma Hub Web** (or your stream name).
2. At the top right you will see a **Measurement ID** that looks like:

   ```text
   G-XXXXXXXXXX
   ```

3. Copy the whole ID, including the `G-` prefix.

> Tip: Do **not** use a Universal Analytics `UA-` ID. ABDiploma Hub only supports GA4 (`G-…`).

---

## 3. Where to paste the ID

On your machine, open this file:

```text
frontend/.env
```

Find (or add) this line:

```env
VITE_GA_MEASUREMENT_ID=
```

Paste your ID after the equals sign, with **no spaces**:

```env
VITE_GA_MEASUREMENT_ID=G-XXXXXXXXXX
```

Save the file.

### Production hosts (Vercel, Netlify, Railway, etc.)

Also add the same variable in your host’s environment settings:

| Name | Value |
|------|--------|
| `VITE_GA_MEASUREMENT_ID` | `G-XXXXXXXXXX` |

Then **redeploy** the frontend so Vite bakes the value into the build.

> Important: Vite reads `VITE_…` variables at **build / dev-server start** time. Changing `.env` while the app is already running will not apply until you restart.

---

## 4. How to restart the frontend

From a terminal:

```powershell
cd C:\AlbertaPrep\frontend
npm run dev
```

If it was already running, stop it with `Ctrl+C`, then run `npm run dev` again.

For a production-style check locally:

```powershell
cd C:\AlbertaPrep\frontend
npm run build
npm run preview
```

---

## 5. How to verify Realtime events

1. Open your ABDiploma Hub site in a browser (local or production).
2. In Google Analytics, go to **Reports → Realtime** (or **Engage → Events** under Realtime).
3. Reload the ABDiploma Hub homepage.
4. Within about 30 seconds you should see:
   - At least **1 user** active
   - Event **`page_view`**
5. Optional browser check:
   - Open DevTools → **Network**
   - Filter by `google` or `gtag` or `collect`
   - Confirm requests to Google are happening (not blocked by an ad blocker)

If nothing appears:

- Confirm `VITE_GA_MEASUREMENT_ID` is set and the frontend was restarted / redeployed
- Disable ad blockers / privacy extensions for the test
- Confirm you copied a `G-` Measurement ID, not another ID type

---

## 6. How to confirm quiz events are being received

With Realtime open, perform these actions on the site:

| Action | Expected event |
|--------|----------------|
| Open any page / navigate | `page_view` |
| Start a practice quiz | `quiz_started` |
| Finish a quiz | `quiz_completed` |
| Start a quiz while logged out | `guest_quiz` (also `quiz_started`) |
| Start Daily Practice | `daily_practice_started` |
| Finish Daily Practice | `daily_practice_completed` |
| Open Weakness Map | `weakness_map_viewed` |
| Register | `signup` |
| Log in | `login` |
| Submit feedback thumbs | `feedback_sent` |
| Report a question | `question_reported` |

In Realtime → **Event count by Event name**, confirm the names above as you trigger them.

After ~24 hours, the same events also appear under **Reports → Engagement → Events** (not only Realtime).

---

## What ABDiploma Hub does automatically

- Loads the official gtag.js script when `VITE_GA_MEASUREMENT_ID` is set
- Sends SPA `page_view` on React Router navigation
- Calls `trackEvent(...)` for the product events listed above
- Does **nothing** when the Measurement ID is empty (safe for local work without GA)

You do **not** need to paste any HTML snippet into `index.html` — the app already initializes GA4 in code.

---

## Security notes

- Never put your Google Analytics **API secrets** or service-account keys in the frontend.
- The Measurement ID (`G-…`) is designed to be public in client-side code; that is expected.
- Do not commit real production secrets you care about into git if your repo is public — prefer host env vars for production deploys.
