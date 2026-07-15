import { useId, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import Button from '../components/ui/Button'
import Card from '../components/ui/Card'
import Logo from '../components/brand/Logo'
import SkipLink from '../components/a11y/SkipLink'
import { useAuth } from '../context/AuthContext'
import { toUserMessage } from '../lib/errors'
import { usePageSeo } from '../lib/seo'
import { LINK_FOCUS } from '../lib/focusStyles'

const inputClasses =
  'h-10 w-full rounded-md border border-gray-300 bg-white px-4 text-base text-gray-900 placeholder:text-gray-500 focus:border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-600'

function Login() {
  usePageSeo({
    title: 'Log In | ABDiploma Hub',
    description:
      'Log in to ABDiploma Hub to save Alberta diploma exam practice progress, use your Weakness Map, and continue Daily Practice.',
    path: '/login',
    robots: 'index,follow',
  })
  const navigate = useNavigate()
  const { login } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const errorId = useId()

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError(null)
    setIsSubmitting(true)
    try {
      await login(email, password)
      navigate('/dashboard')
    } catch (err) {
      setError(toUserMessage(err, 'Incorrect email or password.'))
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center overflow-x-clip bg-gray-50 px-4 py-8 sm:px-6">
      <SkipLink />
      <main id="main-content" tabIndex={-1} className="w-full max-w-md min-w-0">
        <Card>
          <Link
            to="/dashboard"
            className={['flex justify-center rounded-md', LINK_FOCUS].join(' ')}
            aria-label="ABDiploma Hub"
          >
            <Logo size="lg" />
          </Link>
          <h1 className="mt-4 text-center text-xl font-semibold text-gray-900">
            Log in
          </h1>
          <p className="mt-2 text-center text-sm text-gray-600">
            Log in to save progress, open your Weakness Map, and continue Daily Practice.
          </p>

          {error && (
            <div
              id={errorId}
              role="alert"
              className="mt-6 rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800"
            >
              {error}
            </div>
          )}

          <form className="mt-6 flex flex-col gap-4" onSubmit={handleSubmit} noValidate>
            <div className="flex flex-col gap-2">
              <label htmlFor="email" className="text-xs font-medium text-gray-700">
                Email <span className="text-red-700" aria-hidden="true">*</span>
                <span className="sr-only">(required)</span>
              </label>
              <input
                id="email"
                name="email"
                type="email"
                required
                autoComplete="email"
                placeholder="you@example.com"
                className={inputClasses}
                value={email}
                aria-invalid={error ? true : undefined}
                aria-describedby={error ? errorId : undefined}
                onChange={(event) => setEmail(event.target.value)}
              />
            </div>

            <div className="flex flex-col gap-2">
              <label htmlFor="password" className="text-xs font-medium text-gray-700">
                Password <span className="text-red-700" aria-hidden="true">*</span>
                <span className="sr-only">(required)</span>
              </label>
              <input
                id="password"
                name="password"
                type="password"
                required
                autoComplete="current-password"
                placeholder="Your password"
                className={inputClasses}
                value={password}
                aria-invalid={error ? true : undefined}
                aria-describedby={error ? errorId : undefined}
                onChange={(event) => setPassword(event.target.value)}
              />
            </div>

            <div className="mt-2 flex flex-col">
              <Button type="submit" disabled={isSubmitting} aria-busy={isSubmitting}>
                {isSubmitting ? 'Logging in…' : 'Log in'}
              </Button>
            </div>
          </form>

          <p className="mt-6 text-center text-sm text-gray-600">
            New to ABDiploma Hub?{' '}
            <Link
              to="/register"
              className={['font-medium text-blue-700 hover:text-blue-800', LINK_FOCUS].join(' ')}
            >
              Create an account
            </Link>
          </p>
        </Card>
      </main>
    </div>
  )
}

export default Login
