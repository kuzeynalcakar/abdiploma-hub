import { buildDiplomaReadiness } from '../../lib/diplomaReadiness'

function TopicNameList({ topics, emptyLabel, tone }) {
  if (!topics.length) {
    return <p className="mt-2 text-sm text-gray-500">{emptyLabel}</p>
  }
  const badge =
    tone === 'strong'
      ? 'bg-green-100 text-green-800'
      : 'bg-orange-100 text-orange-900'

  return (
    <ul className="mt-3 flex flex-col gap-2">
      {topics.map((topic) => (
        <li
          key={topic.topic_id}
          className="flex items-center justify-between gap-3 rounded-lg border border-gray-100 bg-white px-3 py-2 text-sm"
        >
          <span className="min-w-0 break-words font-medium text-gray-900">
            {topic.topic_name}
          </span>
          <span className={`shrink-0 rounded-full px-2.5 py-0.5 text-xs font-semibold ${badge}`}>
            {topic.accuracy}%
          </span>
        </li>
      ))}
    </ul>
  )
}

/**
 * Diploma exam readiness overview using only Weakness Map API fields.
 */
function DiplomaExamReadiness({ weaknessMap }) {
  const readiness = buildDiplomaReadiness(weaknessMap)

  return (
    <section
      className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6"
      aria-labelledby="diploma-readiness-heading"
    >
      <p className="text-xs font-semibold uppercase tracking-wide text-blue-800">
        Diploma exam preparation
      </p>
      <h2
        id="diploma-readiness-heading"
        className="mt-1 text-xl font-bold text-gray-900 sm:text-2xl"
      >
        {readiness.courseName} Diploma Exam Readiness
      </h2>
      <p className="mt-3 text-sm leading-relaxed text-gray-600">
        This is an estimate from your practice results — not a diploma exam score. Use
        it to decide which topics to review before exam day.
      </p>

      {!readiness.sufficientForOverview ? (
        <div className="mt-5 rounded-lg border border-dashed border-slate-200 bg-slate-50 px-4 py-4">
          <p className="text-sm font-medium text-slate-800">
            Complete more practice sessions to generate a more accurate readiness
            overview.
          </p>
          {readiness.hasPracticeData && (
            <p className="mt-2 text-sm text-slate-600">
              So far you have completed{' '}
              <span className="font-semibold text-slate-900">
                {readiness.questionsCompleted}
              </span>{' '}
              question{readiness.questionsCompleted === 1 ? '' : 's'} across{' '}
              <span className="font-semibold text-slate-900">
                {readiness.coverageLabel}
              </span>
              . Keep practicing to broaden topic coverage.
            </p>
          )}
        </div>
      ) : (
        <>
          <div className="mt-5 rounded-lg border border-blue-100 bg-blue-50/70 px-4 py-4">
            <p className="text-xs font-semibold uppercase tracking-wide text-blue-800">
              Current preparation indicator
            </p>
            <p className="mt-1 text-base font-semibold text-slate-900">
              {readiness.preparationLabel}
            </p>
            <dl className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-3">
              <div className="rounded-md bg-white px-3 py-3 shadow-sm">
                <dt className="text-xs text-gray-500">Practice accuracy</dt>
                <dd className="mt-1 text-lg font-bold text-gray-900">
                  {readiness.overallAccuracy}%
                </dd>
              </div>
              <div className="rounded-md bg-white px-3 py-3 shadow-sm">
                <dt className="text-xs text-gray-500">Questions completed</dt>
                <dd className="mt-1 text-lg font-bold text-gray-900">
                  {readiness.questionsCompleted}
                </dd>
              </div>
              <div className="rounded-md bg-white px-3 py-3 shadow-sm">
                <dt className="text-xs text-gray-500">Topic coverage</dt>
                <dd className="mt-1 text-sm font-bold leading-snug text-gray-900 sm:text-base">
                  {readiness.coverageLabel}
                </dd>
              </div>
            </dl>
          </div>

          <div className="mt-6 grid gap-6 sm:grid-cols-2">
            <div>
              <h3 className="text-sm font-semibold text-green-800">Strength areas</h3>
              <p className="mt-1 text-xs text-gray-500">
                Topics with strong performance in your practice history
              </p>
              <TopicNameList
                topics={readiness.strengthTopics}
                emptyLabel="No strong topics yet—keep practicing to build them."
                tone="strong"
              />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-orange-800">Review areas</h3>
              <p className="mt-1 text-xs text-gray-500">
                Topics needing additional practice before exam day
              </p>
              <TopicNameList
                topics={readiness.reviewTopics}
                emptyLabel="No urgent review topics from your current practice."
                tone="review"
              />
            </div>
          </div>
        </>
      )}
    </section>
  )
}

export default DiplomaExamReadiness
