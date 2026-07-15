import { Link, Navigate } from 'react-router-dom'
import Button from '../ui/Button'
import ErrorAlert from '../ui/ErrorAlert'
import { useAuth } from '../../context/AuthContext'
import { LINK_FOCUS } from '../../lib/focusStyles'

/**
 * Restricts children to authenticated admin users (is_admin from /auth/me).
 */
function AdminRoute({ children }) {
  const { user, isLoading, sessionError, hasStoredSession, restoreSession } = useAuth()

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-white">
        <p className="text-sm text-gray-500" role="status" aria-live="polite">
          Loading your session…
        </p>
      </div>
    )
  }

  if (!user && hasStoredSession && sessionError) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center bg-gray-50 px-6">
        <div className="w-full max-w-md rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
          <h1 className="text-lg font-semibold text-gray-900">
            Could not restore your session
          </h1>
          <ErrorAlert className="mt-4" message={sessionError} />
          <div className="mt-6 flex flex-col gap-3 sm:flex-row">
            <Button type="button" onClick={restoreSession}>
              Try again
            </Button>
            <Link
              to="/login"
              className={[
                'inline-flex min-h-10 items-center justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-900 hover:bg-gray-50',
                LINK_FOCUS,
              ].join(' ')}
            >
              Log in
            </Link>
          </div>
        </div>
      </div>
    )
  }

  if (!user) {
    return <Navigate to="/login" replace state={{ from: '/admin' }} />
  }

  if (!user.is_admin) {
    return <Navigate to="/dashboard" replace />
  }

  return children
}

export default AdminRoute
