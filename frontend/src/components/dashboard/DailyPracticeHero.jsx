import { Link } from 'react-router-dom'
import Button from '../ui/Button'
import { FOCUS_RING, LINK_FOCUS } from '../../lib/focusStyles'

function DailyPracticeHero({
  status,
  loading,
  locked,
  lockReason,
  onStart,
  onTakeFirstQuiz,
  onCreateAccount,
  guestMode = false,
}) {
  if (loading) {
    return (
      <section
        className="overflow-hidden rounded-2xl border border-orange-200 bg-gradient-to-br from-orange-50 to-white p-6 shadow-sm sm:p-8"
        aria-busy="true"
      >
        <p className="text-sm text-gray-600" role="status" aria-live="polite">
          Loading today&apos;s practice…
        </p>
      </section>
    )
  }

  if (guestMode) {
    return (
      <section className="overflow-hidden rounded-2xl border border-blue-200 bg-gradient-to-br from-blue-50 to-white p-6 shadow-sm sm:p-8">
        <p className="text-xs font-semibold uppercase tracking-wide text-blue-800">
          Start here
        </p>
        <h2 className="mt-2 text-2xl font-bold text-gray-900 sm:text-3xl">
          Try diploma exam practice
        </h2>
        <p className="mt-3 max-w-xl text-sm leading-6 text-gray-600">
          Browse courses and start a practice quiz right away—no account required.
          Create a free account afterward to save progress and use Daily Practice.
        </p>
        <div className="mt-6 flex flex-col gap-3 sm:flex-row">
          <Link
            to="/quiz"
            className={[
              'inline-flex min-h-12 items-center justify-center rounded-lg bg-blue-700 px-8 text-sm font-semibold text-white hover:bg-blue-800',
              LINK_FOCUS,
            ].join(' ')}
          >
            Start Practice Quiz
          </Link>
          <Link
            to="/register"
            className={[
              'inline-flex min-h-12 items-center justify-center rounded-lg border border-blue-300 bg-white px-8 text-sm font-semibold text-blue-900 hover:bg-blue-50',
              LINK_FOCUS,
            ].join(' ')}
          >
            Create free account
          </Link>
        </div>
      </section>
    )
  }

  if (locked) {
    return (
      <section className="overflow-hidden rounded-2xl border border-gray-200 bg-gradient-to-br from-gray-50 to-white p-6 shadow-sm sm:p-8">
        <div className="min-w-0 flex-1">
          <p className="text-xs font-semibold uppercase tracking-wide text-orange-800">
            Today&apos;s practice
          </p>
          <h2 className="mt-1 text-2xl font-bold text-gray-900">
            Daily Practice needs a first quiz
          </h2>
          <p className="mt-2 max-w-xl text-sm leading-6 text-gray-600">
            {lockReason ||
              'Daily Practice builds a short set from your previous results. Complete one quiz first so we know which topics to prioritize.'}
          </p>
          <div className="mt-6">
            {onCreateAccount ? (
              <Link
                to="/register"
                className={[
                  'inline-flex min-h-11 items-center justify-center rounded-lg bg-blue-700 px-6 py-2.5 text-sm font-semibold text-white hover:bg-blue-800',
                  LINK_FOCUS,
                ].join(' ')}
              >
                Create free account
              </Link>
            ) : (
              <Button onClick={onTakeFirstQuiz}>Take Your First Quiz</Button>
            )}
          </div>
        </div>
      </section>
    )
  }

  const completed = status?.is_completed
  const progress = status
    ? `${status.completed_count} / ${status.total_questions}`
    : '0 / 10'

  return (
    <section className="overflow-hidden rounded-2xl border border-orange-200 bg-gradient-to-br from-orange-50 via-white to-amber-50 p-6 shadow-sm sm:p-8">
      <div className="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
        <div className="min-w-0 flex-1">
          <p className="text-xs font-semibold uppercase tracking-wide text-orange-800">
            Today&apos;s practice
          </p>
          <h2 className="mt-2 text-2xl font-bold tracking-tight text-gray-900 sm:text-3xl">
            Daily Practice for topics that need review
          </h2>
          <p className="mt-3 max-w-xl text-sm leading-6 text-gray-600">
            Daily Practice builds focused sessions from your previous results—not a
            random list of questions.
          </p>
          {status?.focus_message && (
            <p className="mt-3 max-w-xl text-sm leading-6 text-gray-700">
              {status.focus_message}
            </p>
          )}

          <dl className="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-3">
            <div className="rounded-lg border border-orange-100 bg-white px-3 py-3 sm:px-4">
              <dt className="text-xs text-gray-500">Progress</dt>
              <dd className="mt-1 text-lg font-bold text-gray-900 sm:text-xl">{progress}</dd>
            </div>
            <div className="rounded-lg border border-orange-100 bg-white px-3 py-3 sm:px-4">
              <dt className="text-xs text-gray-500">Est. time</dt>
              <dd className="mt-1 text-lg font-bold text-gray-900 sm:text-xl">
                ~{status?.estimated_time_minutes || 10} min
              </dd>
            </div>
            <div className="col-span-2 rounded-lg border border-orange-100 bg-white px-3 py-3 sm:col-span-1 sm:px-4">
              <dt className="text-xs text-gray-500">Questions</dt>
              <dd className="mt-1 text-lg font-bold text-gray-900 sm:text-xl">
                {status?.total_questions || 10}
              </dd>
            </div>
          </dl>
        </div>

        <div className="shrink-0">
          {completed ? (
            <div className="text-center lg:text-right">
              <p className="text-lg font-semibold text-gray-900">
                Today&apos;s set is done
              </p>
              <p className="mt-1 text-sm text-gray-600">
                Come back tomorrow for a new set.
              </p>
              <Link
                to="/daily-practice"
                className={[
                  'mt-4 inline-flex min-h-12 w-full items-center justify-center rounded-lg border border-orange-200 bg-white px-8 text-sm font-semibold text-orange-900 hover:bg-orange-50 sm:w-auto',
                  LINK_FOCUS,
                ].join(' ')}
              >
                View Results
              </Link>
            </div>
          ) : (
            <button
              type="button"
              onClick={onStart}
              className={[
                'inline-flex min-h-14 w-full items-center justify-center rounded-lg bg-orange-600 px-6 text-base font-semibold text-white hover:bg-orange-700 sm:w-auto sm:min-w-[220px] sm:px-8',
                FOCUS_RING,
              ].join(' ')}
            >
              {status?.is_started ? 'Resume Daily Practice' : 'Start Daily Practice'}
            </button>
          )}
        </div>
      </div>
    </section>
  )
}

export default DailyPracticeHero
