import { Link } from 'react-router-dom'

const BENEFITS = [
  'Weakness Map — accuracy by topic, strengths, and topics to review',
  'Daily Practice — focused sessions based on your previous performance',
  'Saved progress — track improvement across practice sessions',
]

function GuestQuizPrompt() {
  return (
    <div className="rounded-lg border border-blue-200 bg-blue-50 px-4 py-5">
      <p className="text-sm font-semibold text-blue-900">
        Create a free account to use:
      </p>
      <ul className="mt-3 space-y-2">
        {BENEFITS.map((item) => (
          <li key={item} className="flex gap-2 text-sm text-blue-900">
            <span className="text-blue-700" aria-hidden="true">
              •
            </span>
            {item}
          </li>
        ))}
      </ul>
      <div className="mt-4 flex flex-col justify-center gap-2 sm:flex-row">
        <Link
          to="/register"
          className="inline-flex min-h-10 items-center justify-center rounded-lg bg-blue-600 px-5 text-sm font-semibold text-white hover:bg-blue-700"
        >
          Create free account
        </Link>
        <Link
          to="/login"
          className="inline-flex min-h-10 items-center justify-center rounded-lg border border-blue-300 bg-white px-5 text-sm font-medium text-blue-800 hover:bg-blue-100"
        >
          Log in
        </Link>
      </div>
    </div>
  )
}

export default GuestQuizPrompt
