import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'

import {

  api,

  clearSessionClient,

  hasSessionHint,

  markSessionActive,

  SESSION_EXPIRED_EVENT,

} from '../lib/api'

import { trackEvent } from '../lib/analytics'

import { reportError, toUserMessage } from '../lib/errors'



const AuthContext = createContext(null)



export function AuthProvider({ children }) {

  const [user, setUser] = useState(null)

  // Until the session cookie/hint is checked we don't know if the user is

  // logged in, so protected routes wait instead of redirecting.

  const [isLoading, setIsLoading] = useState(hasSessionHint())

  // Transient network failures while restoring a session (hint kept).

  const [sessionError, setSessionError] = useState(null)

  const [sessionHint, setSessionHint] = useState(hasSessionHint())



  const clearSession = useCallback(() => {

    clearSessionClient()

    setSessionHint(false)

    setUser(null)

    setSessionError(null)

  }, [])



  const restoreSession = useCallback(async () => {

    if (!hasSessionHint()) {

      setUser(null)

      setSessionError(null)

      setSessionHint(false)

      setIsLoading(false)

      return

    }



    setIsLoading(true)

    setSessionError(null)

    try {

      const data = await api('/auth/me')

      // Successful restore: keep hint, drop any legacy localStorage secret.

      markSessionActive()

      setSessionHint(true)

      setUser(data)

    } catch (err) {

      if (err?.status === 401) {

        clearSession()

      } else {

        // Keep the hint on network / 5xx so a retry can succeed.

        setUser(null)

        setSessionError(

          toUserMessage(err, 'Could not restore your session. Check your connection and try again.'),

        )

        reportError(err, { action: 'restore_session' })

      }

    } finally {

      setIsLoading(false)

    }

  }, [clearSession])



  useEffect(() => {

    restoreSession()

  }, [restoreSession])



  useEffect(() => {

    const onExpired = () => {

      clearSession()

      setIsLoading(false)

    }

    window.addEventListener(SESSION_EXPIRED_EVENT, onExpired)

    return () => window.removeEventListener(SESSION_EXPIRED_EVENT, onExpired)

  }, [clearSession])



  const login = useCallback(async (email, password) => {

    const data = await api('/auth/login', {

      method: 'POST',

      body: { email, password },

    })

    // Cookie carries the secret; do not persist data.token in localStorage.

    markSessionActive()

    setSessionHint(true)

    setUser(data.user)

    setSessionError(null)

    trackEvent('login', { method: 'email' })

  }, [])



  const register = useCallback(async (name, email, password) => {

    const data = await api('/auth/register', {

      method: 'POST',

      body: { name, email, password },

    })

    markSessionActive()

    setSessionHint(true)

    setUser(data.user)

    setSessionError(null)

    trackEvent('signup', { method: 'email' })

  }, [])



  const logout = useCallback(async () => {

    try {

      await api('/auth/logout', { method: 'POST' })

    } catch {

      // Local logout must succeed even if the server is unreachable.

    }

    clearSession()

  }, [clearSession])



  const value = useMemo(

    () => ({

      user,

      isLoading,

      sessionError,

      hasStoredSession: sessionHint,

      login,

      register,

      logout,

      restoreSession,

      clearSession,

    }),

    [

      user,

      isLoading,

      sessionError,

      sessionHint,

      login,

      register,

      logout,

      restoreSession,

      clearSession,

    ],

  )



  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>

}



export function useAuth() {

  return useContext(AuthContext)

}


