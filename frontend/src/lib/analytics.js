/**
 * Google Analytics 4 helpers.
 * Measurement ID comes from VITE_GA_MEASUREMENT_ID — never hardcode IDs.
 *
 * All public methods are no-ops on failure (ad blockers, offline, missing gtag).
 */

const MEASUREMENT_ID = import.meta.env.VITE_GA_MEASUREMENT_ID

export function isAnalyticsEnabled() {
  return Boolean(MEASUREMENT_ID && typeof window !== 'undefined')
}

export function getMeasurementId() {
  return MEASUREMENT_ID || null
}

function scheduleIdle(callback) {
  try {
    if (typeof window !== 'undefined' && typeof window.requestIdleCallback === 'function') {
      window.requestIdleCallback(callback, { timeout: 2500 })
      return
    }
    setTimeout(callback, 1)
  } catch {
    // ignore
  }
}

function safeGtag(...args) {
  try {
    if (!isAnalyticsEnabled()) return
    if (typeof window.gtag !== 'function') return
    window.gtag(...args)
  } catch {
    // Ad blockers / network failures must not break the product UI.
  }
}

export function initGoogleAnalytics() {
  try {
    if (!isAnalyticsEnabled()) return
    if (window.__albertaprepGaInitialized) return
    window.__albertaprepGaInitialized = true

    scheduleIdle(() => {
      try {
        window.dataLayer = window.dataLayer || []
        window.gtag = function gtag() {
          try {
            window.dataLayer.push(arguments)
          } catch {
            // ignore
          }
        }
        window.gtag('js', new Date())
        window.gtag('config', MEASUREMENT_ID, {
          send_page_view: false,
        })

        const script = document.createElement('script')
        script.async = true
        script.defer = true
        script.src = `https://www.googletagmanager.com/gtag/js?id=${MEASUREMENT_ID}`
        script.onerror = () => {
          // GA unavailable — leave gtag as no-op pusher into dataLayer only.
        }
        document.head.appendChild(script)
      } catch {
        // ignore
      }
    })
  } catch {
    // ignore
  }
}

export function trackPageView(path, title) {
  safeGtag('event', 'page_view', {
    page_path: path,
    page_title: title || (typeof document !== 'undefined' ? document.title : ''),
  })
}

/**
 * Fire a named GA4 event. Never throws.
 * Known product events: quiz_started, quiz_completed, signup, login,
 * feedback_submitted, question_reported.
 */
export function trackEvent(eventName, params = {}) {
  try {
    const safeParams = {}
    for (const [key, value] of Object.entries(params || {})) {
      const k = String(key).toLowerCase()
      if (
        k.includes('password') ||
        k.includes('token') ||
        k.includes('secret') ||
        k === 'email' ||
        k === 'authorization'
      ) {
        continue
      }
      if (
        typeof value === 'string' ||
        typeof value === 'number' ||
        typeof value === 'boolean'
      ) {
        safeParams[key] = value
      }
    }
    safeGtag('event', eventName, safeParams)
  } catch {
    // ignore
  }
}

