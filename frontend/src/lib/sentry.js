/**
 * Optional Sentry browser SDK — production builds only when VITE_SENTRY_DSN is set.
 * Secrets/PII are scrubbed before send.
 */

const DSN = import.meta.env.VITE_SENTRY_DSN
const ENABLED = Boolean(import.meta.env.PROD && DSN)

let sentryModule = null
let initPromise = null

const SENSITIVE = /password|token|secret|authorization|cookie|bearer|session|email|api[_-]?key/i

function scrubValue(key, value) {
  if (SENSITIVE.test(String(key))) return '[Filtered]'
  if (typeof value === 'string' && SENSITIVE.test(value)) return '[Filtered]'
  if (value && typeof value === 'object' && !Array.isArray(value)) {
    const out = {}
    for (const [k, v] of Object.entries(value)) {
      out[k] = scrubValue(k, v)
    }
    return out
  }
  return value
}

function beforeSend(event) {
  try {
    if (event.request?.headers) {
      event.request.headers = scrubValue('headers', event.request.headers)
    }
    if (event.request?.cookies) {
      event.request.cookies = '[Filtered]'
    }
    if (event.extra) {
      event.extra = scrubValue('extra', event.extra)
    }
  } catch {
    // never block send pipeline fatally
  }
  return event
}

export function isSentryEnabled() {
  return ENABLED
}

export async function initSentry() {
  if (!ENABLED || initPromise) return initPromise
  initPromise = (async () => {
    try {
      sentryModule = await import('@sentry/react')
      sentryModule.init({
        dsn: DSN,
        environment: 'production',
        sendDefaultPii: false,
        beforeSend,
        tracesSampleRate: 0,
      })
    } catch {
      // Ad blockers / missing package must never break the app.
      sentryModule = null
    }
  })()
  return initPromise
}

export function captureException(error, context = {}) {
  if (!ENABLED) return
  try {
    const safe = scrubValue('context', context) || {}
    if (sentryModule?.captureException) {
      sentryModule.withScope((scope) => {
        Object.entries(safe).forEach(([k, v]) => scope.setExtra(k, v))
        sentryModule.captureException(error)
      })
      return
    }
    // Lazy init then capture once
    initSentry().then(() => {
      if (!sentryModule?.captureException) return
      sentryModule.withScope((scope) => {
        Object.entries(safe).forEach(([k, v]) => scope.setExtra(k, v))
        sentryModule.captureException(error)
      })
    })
  } catch {
    // swallow
  }
}

