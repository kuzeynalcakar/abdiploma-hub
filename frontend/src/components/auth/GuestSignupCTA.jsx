import { Link } from 'react-router-dom'
import Card from '../ui/Card'
import { LINK_FOCUS } from '../../lib/focusStyles'

function GuestSignupCTA({ title, description }) {
  return (
    <Card className="border-2 border-blue-200 bg-gradient-to-br from-blue-50 to-white">
      <h2 className="text-lg font-semibold text-gray-900">
        {title || 'Save your practice progress'}
      </h2>
      <p className="mt-2 text-sm leading-6 text-gray-600">
        {description ||
          'Create a free account to use Daily Practice, your Weakness Map, and saved progress across sessions.'}
      </p>
      <ul className="mt-4 flex flex-col gap-2 text-sm text-gray-700">
        <li className="flex items-center gap-2">
          <span className="text-blue-700" aria-hidden="true">
            •
          </span>
          Daily Practice focused on topics that need improvement
        </li>
        <li className="flex items-center gap-2">
          <span className="text-blue-700" aria-hidden="true">
            •
          </span>
          Weakness Map showing accuracy by topic
        </li>
        <li className="flex items-center gap-2">
          <span className="text-blue-700" aria-hidden="true">
            •
          </span>
          Saved progress so you can track improvement over time
        </li>
      </ul>
      <div className="mt-6 flex flex-col gap-3 sm:flex-row">
        <Link
          to="/register"
          className={[
            'inline-flex min-h-10 w-full items-center justify-center rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 sm:w-auto',
            LINK_FOCUS,
          ].join(' ')}
        >
          Create free account
        </Link>
        <Link
          to="/login"
          className={[
            'inline-flex min-h-10 w-full items-center justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-900 hover:bg-gray-50 sm:w-auto',
            LINK_FOCUS,
          ].join(' ')}
        >
          Log in
        </Link>
      </div>
    </Card>
  )
}

export default GuestSignupCTA
