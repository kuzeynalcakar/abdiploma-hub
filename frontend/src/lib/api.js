import { reportError, toUserMessage } from './errors'

/** Same-origin `/api/v1` by default; set VITE_API_URL for a separate API host. */
function resolveApiBase() {
  const raw = String(import.meta.env.VITE_API_URL || '')
    .trim()
    .replace(/\/$/, '')
  if (!raw) return '/api/v1'
  if (raw.endsWith('/api/v1')) return raw
  return `${raw}/api/v1`
}

const API_BASE = resolveApiBase()

/** localStorage key for the Bearer access token. */
const ACCESS_TOKEN_KEY = 'access_token'

/** Legacy keys from older builds — cleared on read/write. */
const LEGACY_TOKEN_KEY = 'albertaprep_token'
const LEGACY_SESSION_HINT_KEY = 'albertaprep_session'

const REQUEST_TIMEOUT_MS = 20000

const SESSION_EXPIRED_EVENT = 'albertaprep:session-expired'

/** Paths where 401 means bad credentials, not an expired session. */
const AUTH_CREDENTIAL_PATHS = new Set(['/auth/login', '/auth/register'])

/** In-flight GET dedupe — prevents StrictMode / overlapping callers from double-fetching. */
const inflightGets = new Map()

function clearLegacyKeys() {
  try {
    localStorage.removeItem(LEGACY_TOKEN_KEY)
    localStorage.removeItem(LEGACY_SESSION_HINT_KEY)
  } catch {
    // ignore
  }
}

/** True when a Bearer access token is stored. */
export function hasSessionHint() {
  return Boolean(getToken())
}

/** Read the access token from localStorage. */
export function getToken() {
  try {
    const token = localStorage.getItem(ACCESS_TOKEN_KEY)
    return token || null
  } catch {
    return null
  }
}

/** Persist the access token for Authorization: Bearer on API requests. */
export function setToken(token) {
  try {
    if (token) {
      localStorage.setItem(ACCESS_TOKEN_KEY, token)
    } else {
      localStorage.removeItem(ACCESS_TOKEN_KEY)
    }
    clearLegacyKeys()
  } catch {
    // Private mode / blocked storage.
  }
}

/** @deprecated Prefer setToken — kept for call sites. */
export function markSessionActive() {
  // No-op when token is already set via setToken(access_token).
}

/** Remove the access token (local logout). */
export function clearSessionClient() {
  setToken(null)
}

export class ApiError extends Error {
  constructor(message, status) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

function detailToMessage(detail) {
  // FastAPI validation errors arrive as a list of {loc, msg} objects.
  if (Array.isArray(detail)) {
    const parts = detail
      .map((item) => {
        if (typeof item === 'string') return item
        if (item && typeof item.msg === 'string') {
          return item.msg.replace(/^Value error, /, '')
        }
        return null
      })
      .filter(Boolean)
    return parts.length ? parts.join(' ') : null
  }
  if (typeof detail === 'string') return detail
  if (detail && typeof detail === 'object' && typeof detail.msg === 'string') {
    return detail.msg
  }
  // Never stringify unknown objects (may contain internals).
  return null
}

function statusFallbackMessage(status) {
  if (status === 0) {
    return 'Could not reach the server. Check your connection and try again.'
  }
  if (status === 408 || status === 504) {
    return 'The request timed out. Please try again.'
  }
  if (status === 401) {
    return 'Please log in again to continue.'
  }
  if (status === 403) {
    return 'You do not have permission to do that.'
  }
  if (status === 404) {
    return 'We could not find what you were looking for.'
  }
  if (status === 422) {
    return 'Some of the information you entered looks invalid. Please check and try again.'
  }
  if (status === 429) {
    return 'Too many requests. Please wait a moment and try again.'
  }
  if (status >= 500) {
    return 'Something went wrong on our side. Please try again in a moment.'
  }
  return `Something went wrong (${status}).`
}

async function parseBody(response) {
  const contentType = response.headers.get('content-type') || ''
  if (response.status === 204) return null
  if (contentType.includes('application/json')) {
    try {
      return await response.json()
    } catch {
      return null
    }
  }
  // Non-JSON error pages (proxies, HTML) — ignore body.
  try {
    await response.text()
  } catch {
    // ignore
  }
  return null
}

function notifySessionExpired(path) {
  if (AUTH_CREDENTIAL_PATHS.has(path)) return
  if (typeof window === 'undefined') return
  window.dispatchEvent(new CustomEvent(SESSION_EXPIRED_EVENT))
}

async function request(path, { method = 'GET', body } = {}) {
  if (typeof navigator !== 'undefined' && navigator.onLine === false) {
    throw new ApiError(
      'You appear to be offline. Reconnect and try again.',
      0,
    )
  }

  const headers = {}
  const token = getToken()
  if (token) headers.Authorization = `Bearer ${token}`
  if (body !== undefined) headers['Content-Type'] = 'application/json'

  let response
  try {
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS)
    try {
      response = await fetch(`${API_BASE}${path}`, {
        method,
        headers,
        body: body !== undefined ? JSON.stringify(body) : undefined,
        signal: controller.signal,
      })
    } finally {
      clearTimeout(timeoutId)
    }
  } catch (err) {
    const aborted = err?.name === 'AbortError'
    const message = aborted
      ? 'The request timed out. Please try again.'
      : 'Could not reach the server. Check your connection and try again.'
    const apiErr = new ApiError(message, 0)
    reportError(apiErr, { action: 'api_network', path, method, aborted: Boolean(aborted) })
    throw apiErr
  }

  if (response.status === 204) return null

  const data = await parseBody(response)
  if (!response.ok) {
    if (response.status === 401) {
      notifySessionExpired(path)
    }
    const raw = detailToMessage(data?.detail)
    const message = toUserMessage(raw, statusFallbackMessage(response.status))
    const apiErr = new ApiError(message, response.status)
    if (response.status >= 500 || response.status === 0) {
      reportError(apiErr, { action: 'api_error', path, method, status: response.status })
    }
    throw apiErr
  }

  // Successful responses should parse as JSON.
  if (data === null) {
    const apiErr = new ApiError(
      'Received an unexpected response from the server. Please try again.',
      502,
    )
    reportError(apiErr, { action: 'api_malformed', path, method })
    throw apiErr
  }
  return data
}

export async function api(path, options = {}) {
  const method = (options.method || 'GET').toUpperCase()
  const canDedupe = method === 'GET' && options.body === undefined

  if (!canDedupe) {
    return request(path, options)
  }

  const existing = inflightGets.get(path)
  if (existing) return existing

  const pending = request(path, options).finally(() => {
    inflightGets.delete(path)
  })
  inflightGets.set(path, pending)
  return pending
}

export { SESSION_EXPIRED_EVENT, ACCESS_TOKEN_KEY, LEGACY_TOKEN_KEY }
