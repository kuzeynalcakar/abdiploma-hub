import { lazy, Suspense } from 'react'
import { Link } from 'react-router-dom'
import Card from '../ui/Card'
import Button from '../ui/Button'
import ErrorAlert from '../ui/ErrorAlert'
import { useAuth } from '../../context/AuthContext'
import { LINK_FOCUS } from '../../lib/focusStyles'

const AppLayout = lazy(() => import('../layout/AppLayout'))

function GateContent({ pageTitle, title, description }) {
  return (
    <AppLayout pageTitle={pageTitle}>
      <div className="mx-auto flex max-w-lg flex-col gap-6">
        <Card className="text-center">
          <div
            className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-gray-100"
            aria-hidden="true"
          >
            <svg
              viewBox="0 0 24 24"
              className="h-7 w-7 text-gray-500"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.75"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M8 11V8a4 4 0 1 1 8 0v3m-9 0h10a1 1 0 0 1 1 1v7a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1v-7a1 1 0 0 1 1-1z"
              />
            </svg>
          </div>
          <h2 className="mt-4 text-xl font-semibold text-gray-900">{title}</h2>
          <p className="mt-2 text-sm leading-6 text-gray-600">{description}</p>
          <div className="mt-6 flex flex-col justify-center gap-3 sm:flex-row">
            <Link
              to="/register"
              className={[
                'inline-flex min-h-10 items-center justify-center rounded-md bg-blue-600 px-5 py-2 text-sm font-medium text-white hover:bg-blue-700',
                LINK_FOCUS,
              ].join(' ')}
            >
              Create free account
            </Link>
            <Link
              to="/login"
              className={[
                'inline-flex min-h-10 items-center justify-center rounded-md border border-gray-300 bg-white px-5 py-2 text-sm font-medium text-gray-900 hover:bg-gray-50',
                LINK_FOCUS,
              ].join(' ')}
            >
              Log in
            </Link>
          </div>
          <p className="mt-4 text-xs text-gray-600">
            You can still practice quizzes as a guest from the dashboard.
          </p>
        </Card>
      </div>
    </AppLayout>
  )
}

function SessionRecoverContent({ pageTitle, message, onRetry, isRetrying }) {
  return (
    <AppLayout pageTitle={pageTitle}>
      <div className="mx-auto flex max-w-lg flex-col gap-6">
        <Card>
          <h2 className="text-xl font-semibold text-gray-900">
            Could not restore your session
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Your account is still signed in on this device, but we could not reach
            the server just now.
          </p>
          <ErrorAlert className="mt-4" message={message} />
          <div className="mt-6 flex flex-col gap-3 sm:flex-row">
            <Button type="button" onClick={onRetry} disabled={isRetrying}>
              {isRetrying ? 'Retrying…' : 'Try again'}
            </Button>
            <Link
              to="/dashboard"
              className={[
                'inline-flex min-h-10 items-center justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-900 hover:bg-gray-50',
                LINK_FOCUS,
              ].join(' ')}
            >
              Continue as guest
            </Link>
          </div>
        </Card>
      </div>
    </AppLayout>
  )
}

function AuthGate({ pageTitle, title, description, children }) {
  const { user, isLoading, sessionError, hasStoredSession, restoreSession } = useAuth()

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-white">
        <p className="text-sm text-gray-600" role="status" aria-live="polite">
          Loading your session…
        </p>
      </div>
    )
  }

  if (!user && hasStoredSession && sessionError) {
    return (
      <Suspense
        fallback={
          <div className="flex min-h-screen items-center justify-center bg-white">
            <p className="text-sm text-gray-600" role="status">
              Loading…
            </p>
          </div>
        }
      >
        <SessionRecoverContent
          pageTitle={pageTitle}
          message={sessionError}
          onRetry={restoreSession}
          isRetrying={isLoading}
        />
      </Suspense>
    )
  }

  if (!user) {
    return (
      <Suspense
        fallback={
          <div className="flex min-h-screen items-center justify-center bg-white">
            <p className="text-sm text-gray-600" role="status">
              Loading…
            </p>
          </div>
        }
      >
        <GateContent
          pageTitle={pageTitle}
          title={title}
          description={description}
        />
      </Suspense>
    )
  }

  return children
}

export default AuthGate
