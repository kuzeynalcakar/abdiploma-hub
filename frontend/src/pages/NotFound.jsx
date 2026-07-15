import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { usePageSeo } from '../lib/seo'
import SkipLink from '../components/a11y/SkipLink'
import { LINK_FOCUS } from '../lib/focusStyles'

function NotFound() {
  usePageSeo({
    title: 'Page Not Found | ABDiploma Hub',
    description:
      'This ABDiploma Hub page could not be found. Return to free Alberta diploma exam practice.',
    path: '/404',
    robots: 'noindex,nofollow',
    noCanonical: true,
  })
  const { user } = useAuth()
  const homePath = user ? '/dashboard' : '/'

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-white px-6 text-center">
      <SkipLink />
      <main id="main-content" tabIndex={-1}>
        <p className="text-sm font-medium text-blue-700">404</p>
        <h1 className="mt-2 text-3xl font-semibold text-gray-900">
          Page not found
        </h1>
        <p className="mt-3 max-w-md text-sm text-gray-600">
          The page you are looking for doesn&apos;t exist or may have moved.
        </p>
        <Link
          to={homePath}
          className={[
            'mt-8 inline-flex rounded-md bg-blue-600 px-6 py-2.5 text-sm font-medium text-white hover:bg-blue-700',
            LINK_FOCUS,
          ].join(' ')}
        >
          {user ? 'Back to dashboard' : 'Back to home'}
        </Link>
      </main>
    </div>
  )
}

export default NotFound
