/**
 * Safe user-facing error helpers. Never surface stack traces, secrets, or internals.
 */

import { captureException } from './sentry'

const UNSAFE_PATTERN =
  /traceback|stack trace|sqlalchemy|operationalerror|sqlite3\.|file:\/\/|\\Users\\|\/home\/|\/var\/|password|authorization|bearer\s|secret|api[_-]?key|environ|dotenv|\.py:\d+/i

/**
 * Convert an unknown thrown value into a short, user-safe message.
 */
export function toUserMessage(err, fallback = 'Something went wrong. Please try again.') {
  if (err == null) return fallback

  let message = null
  if (typeof err === 'string') {
    message = err.trim()
  } else if (typeof err === 'object' && typeof err.message === 'string') {
    message = err.message.trim()
  }

  if (!message || message === 'undefined' || message === 'null') {
    return fallback
  }
  if (UNSAFE_PATTERN.test(message)) {
    return fallback
  }
  // Likely a raw stack fragment
  if (message.includes('\n') && /at\s+\S+/.test(message)) {
    return fallback
  }
  return message
}

/**
 * Lightweight crash / failure telemetry. Never log secrets or PII.
 */
export function reportError(error, context = {}) {
  try {
    const safeContext = {}
    for (const [key, value] of Object.entries(context || {})) {
      const k = String(key).toLowerCase()
      if (
        k.includes('password') ||
        k.includes('token') ||
        k.includes('secret') ||
        k.includes('authorization') ||
        k === 'email' ||
        k === 'name'
      ) {
        continue
      }
      if (typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean') {
        safeContext[key] = value
      }
    }

    const payload = {
      message: toUserMessage(error, 'Unknown error'),
      status: typeof error?.status === 'number' ? error.status : undefined,
      name: typeof error?.name === 'string' ? error.name : undefined,
      ...safeContext,
    }
    console.error('[ABDiplomaHub]', payload)
    captureException(error instanceof Error ? error : new Error(payload.message), safeContext)
  } catch {
    // Logging must never throw into the UI.
  }
}

export function isNetworkError(err) {
  return err?.status === 0
}

export function isUnauthorized(err) {
  return err?.status === 401
}

