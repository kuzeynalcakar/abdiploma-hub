import Card from '../ui/Card'
import { masteryStyle } from '../../lib/mastery'

function TopicAccuracyBadge({ accuracy }) {
  const style = masteryStyle(
    accuracy >= 90
      ? 'excellent'
      : accuracy >= 75
        ? 'strong'
        : accuracy >= 60
          ? 'improving'
          : accuracy >= 40
            ? 'weak'
            : 'critical',
  )
  return (
    <span
      className={[
        'rounded-full px-2.5 py-0.5 text-xs font-medium',
        style.bg,
        style.text,
      ].join(' ')}
    >
      {accuracy}%
    </span>
  )
}

function QuizResultsView({
  title,
  results,
  subtitle,
  children,
  headingRef,
}) {
  const strongTopics = results?.topics?.filter((t) => t.accuracy >= 75) || []
  const weakTopics = results?.topics?.filter((t) => t.accuracy < 75) || []
  const types = results?.question_types || {}

  return (
    <>
      <Card className="min-w-0">
        <h2
          ref={headingRef}
          tabIndex={-1}
          className="text-xl font-semibold break-words text-gray-900 outline-none focus-visible:ring-2 focus-visible:ring-blue-600 focus-visible:ring-offset-2"
        >
          {title}
        </h2>
        {subtitle && (
          <p className="mt-1 text-sm text-gray-500">{subtitle}</p>
        )}

        <p className="mt-6 text-center text-4xl font-bold text-blue-600 sm:text-5xl">
          {results.score_percent}%
        </p>
        <p className="mt-1 text-center text-xs text-gray-500">
          Auto-graded questions only
        </p>

        <dl className="mt-8 grid grid-cols-2 gap-3 text-center sm:grid-cols-4 sm:gap-4">
          <div className="rounded-md bg-gray-50 p-3 sm:p-4">
            <dt className="text-xs font-medium text-gray-500">Completed</dt>
            <dd className="mt-1 text-xl font-semibold text-gray-900 sm:text-2xl">
              {results.total_questions}
            </dd>
          </div>
          <div className="rounded-md bg-green-50 p-3 sm:p-4">
            <dt className="text-xs font-medium text-green-700">Correct</dt>
            <dd className="mt-1 text-xl font-semibold text-green-700 sm:text-2xl">
              {results.correct}
            </dd>
          </div>
          <div className="rounded-md bg-red-50 p-3 sm:p-4">
            <dt className="text-xs font-medium text-red-700">Incorrect</dt>
            <dd className="mt-1 text-xl font-semibold text-red-700 sm:text-2xl">
              {results.wrong}
            </dd>
          </div>
          <div className="rounded-md bg-amber-50 p-3 sm:p-4">
            <dt className="text-xs font-medium text-amber-700">Review</dt>
            <dd className="mt-1 text-xl font-semibold text-amber-700 sm:text-2xl">
              {results.review_required || 0}
            </dd>
          </div>
        </dl>

        {(types.multiple_choice ||
          types.numerical_response ||
          types.written_response) && (
          <div className="mt-6 rounded-md border border-gray-200 bg-gray-50 p-4">
            <h3 className="text-sm font-semibold text-gray-900">
              Question types
            </h3>
            <dl className="mt-3 grid grid-cols-1 gap-2 text-sm sm:grid-cols-3">
              <div className="flex justify-between gap-2 sm:flex-col sm:justify-start">
                <dt className="text-gray-500">Multiple Choice</dt>
                <dd className="font-semibold text-gray-900">
                  {types.multiple_choice || 0}
                </dd>
              </div>
              <div className="flex justify-between gap-2 sm:flex-col sm:justify-start">
                <dt className="text-gray-500">Numerical</dt>
                <dd className="font-semibold text-gray-900">
                  {types.numerical_response || 0}
                </dd>
              </div>
              <div className="flex justify-between gap-2 sm:flex-col sm:justify-start">
                <dt className="text-gray-500">Written</dt>
                <dd className="font-semibold text-gray-900">
                  {types.written_response || 0}
                </dd>
              </div>
            </dl>
            {(results.review_required || 0) > 0 && (
              <p className="mt-3 text-xs text-amber-700">
                Written response questions require self-review and are not
                included in the auto-graded score.
              </p>
            )}
          </div>
        )}
      </Card>

      <Card className="min-w-0">
        <h3 className="text-base font-semibold text-gray-900">
          Topic performance
        </h3>
        <p className="mt-1 text-xs text-gray-500">
          Based on auto-graded questions only
        </p>

        {/* Stacked rows on small screens — avoids horizontal overflow */}
        <ul className="mt-4 flex flex-col gap-2 sm:hidden">
          {results.topics.map((topic) => (
            <li
              key={topic.topic_id}
              className="rounded-lg border border-gray-100 bg-gray-50 px-3 py-3"
            >
              <div className="flex items-start justify-between gap-3">
                <p className="min-w-0 text-sm font-medium break-words text-gray-900">
                  {topic.topic_name}
                </p>
                <TopicAccuracyBadge accuracy={topic.accuracy} />
              </div>
              <p className="mt-1 text-xs text-gray-500">
                {topic.correct}/{topic.total} correct
              </p>
            </li>
          ))}
        </ul>

        <div className="mt-4 hidden overflow-x-auto sm:block">
          <table className="w-full min-w-0 table-fixed text-left text-sm">
            <caption className="sr-only">
              Topic performance: correct answers and accuracy by topic
            </caption>
            <thead>
              <tr className="border-b border-gray-200 text-xs font-medium uppercase tracking-wide text-gray-600">
                <th scope="col" className="py-2 pr-4">Topic</th>
                <th scope="col" className="w-24 py-2 pr-4">Correct</th>
                <th scope="col" className="w-24 py-2">Accuracy</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {results.topics.map((topic) => (
                <tr key={topic.topic_id}>
                  <td className="py-3 pr-4 break-words text-gray-900">
                    {topic.topic_name}
                  </td>
                  <td className="py-3 pr-4 text-gray-700">
                    {topic.correct}/{topic.total}
                  </td>
                  <td className="py-3">
                    <TopicAccuracyBadge accuracy={topic.accuracy} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {strongTopics.length > 0 && weakTopics.length === 0 && (
          <p className="mt-4 text-sm text-green-700">
            All topics look strong on this quiz.
          </p>
        )}
      </Card>

      {children}
    </>
  )
}

export default QuizResultsView
