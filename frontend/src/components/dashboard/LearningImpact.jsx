import Card from '../ui/Card'

function ProgressBar({ value, max = 100, colorClass = 'bg-blue-600', label }) {
  const width = max > 0 ? Math.min(100, Math.round((value / max) * 100)) : 0
  return (
    <div>
      {label && (
        <div className="mb-1 flex items-center justify-between text-xs text-gray-600">
          <span>{label}</span>
          <span className="font-medium text-gray-900">{value}%</span>
        </div>
      )}
      <div
        role="progressbar"
        aria-valuenow={width}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label={label ? `${label}: ${value}%` : `${width} percent`}
        className="h-2.5 w-full rounded-full bg-gray-100"
      >
        <div
          className={`h-2.5 rounded-full transition-[width] ${colorClass}`}
          style={{ width: `${width}%` }}
        />
      </div>
    </div>
  )
}

function SessionIndicator({ count }) {
  const visible = Math.min(count, 10)
  const overflow = count - visible

  return (
    <div className="flex flex-wrap items-center gap-1.5">
      {Array.from({ length: visible }).map((_, index) => (
        <span
          key={index}
          className="inline-block h-3 w-3 rounded-full bg-blue-500"
          aria-hidden="true"
        />
      ))}
      {overflow > 0 && (
        <span className="text-xs font-medium text-gray-500">+{overflow} more</span>
      )}
      {count === 0 && (
        <span className="text-xs text-gray-500">No completed sessions yet</span>
      )}
    </div>
  )
}

function LearningImpact({ impact, practiceStreak, courseProgress = [] }) {
  const hasData = impact && impact.questions_completed > 0
  const practicedSubjects = courseProgress.filter(
    (course) => course.questions_answered > 0 || course.quizzes_completed > 0,
  )
  const subjectNames = practicedSubjects.map((course) => course.course_name)

  const strongTopicCount =
    practicedSubjects.reduce((sum, course) => sum + course.strong_topics.length, 0) ||
    impact?.topics_improved ||
    0
  const weakTopicCount =
    practicedSubjects.reduce((sum, course) => sum + course.weak_topics.length, 0) ||
    impact?.weaknesses_identified ||
    0
  const topicTotal = strongTopicCount + weakTopicCount

  if (!hasData) {
    return (
      <section aria-labelledby="learning-impact-heading">
        <h2 id="learning-impact-heading" className="text-xl font-semibold text-gray-900">
          Your practice summary
        </h2>
        <p className="mt-1 text-sm text-gray-500">
          See how your practice is going so far.
        </p>

        <Card className="mt-4 border border-dashed border-gray-200 bg-gray-50">
          <p className="text-sm font-medium text-gray-800">
            Complete your first practice session to see a summary based on your answers.
          </p>
          <p className="mt-2 text-sm text-gray-600">
            After you finish a quiz, you can check accuracy by topic on your Weakness
            Map and use Daily Practice to review areas that need more work.
          </p>
          <ul className="mt-3 space-y-1.5 text-sm text-gray-600">
            <li>• Questions answered and practice sessions completed</li>
            <li>• Topics that are improving vs. topics that need review</li>
            <li>• Accuracy trends as you keep practicing</li>
          </ul>
        </Card>
      </section>
    )
  }

  const stats = [
    { label: 'Questions answered', value: impact.questions_completed },
    { label: 'Practice sessions', value: impact.practice_sessions },
    {
      label: 'Subjects practiced',
      value: impact.subjects_practiced ?? practicedSubjects.length,
      detail: subjectNames.length > 0 ? subjectNames.join(', ') : null,
    },
    { label: 'Stronger topics', value: impact.topics_improved },
    { label: 'Topics needing review', value: impact.weaknesses_identified },
    { label: 'Targeted practice questions', value: impact.targeted_questions_completed },
  ]

  const hasAccuracyTrend =
    impact.early_accuracy != null && impact.recent_accuracy != null

  return (
    <section aria-labelledby="learning-impact-heading">
      <h2 id="learning-impact-heading" className="text-xl font-semibold text-gray-900">
        Your practice summary
      </h2>
      <p className="mt-1 text-sm text-gray-500">
        Based on your saved practice history.
      </p>

      <Card className="mt-4 border border-blue-100 bg-gradient-to-br from-slate-50 to-white">
        <div className="rounded-lg border border-blue-100 bg-blue-50/70 px-4 py-3">
          <p className="text-sm text-blue-900">
            Your Weakness Map shows accuracy by topic. Daily Practice then focuses on
            the areas that need more work.
          </p>
          <p className="mt-2 text-sm text-blue-800">
            Explanations after each answer help you learn from mistakes.
          </p>
        </div>

        <dl className="mt-5 grid grid-cols-2 gap-4 sm:grid-cols-3">
          {stats.map((stat) => (
            <div key={stat.label} className="rounded-lg bg-white p-3 shadow-sm">
              <dd className="text-2xl font-bold text-gray-900">{stat.value}</dd>
              <dt className="mt-1 text-xs font-medium text-gray-500">{stat.label}</dt>
              {stat.detail && (
                <dd className="mt-1 text-xs break-words text-gray-500">
                  {stat.detail}
                </dd>
              )}
            </div>
          ))}
          <div className="rounded-lg bg-white p-3 shadow-sm">
            <dd className="text-2xl font-bold text-gray-900">{impact.overall_accuracy}%</dd>
            <dt className="mt-1 text-xs font-medium text-gray-500">Overall accuracy</dt>
          </div>
        </dl>

        <div className="mt-6 space-y-5">
          {hasAccuracyTrend && (
            <div>
              <h4 className="text-sm font-semibold text-gray-900">Accuracy trend</h4>
              <p className="mt-1 text-xs text-gray-500">
                Comparing your earlier answers to your more recent ones (same account,
                real stored results).
              </p>
              <div className="mt-3 space-y-3">
                <ProgressBar
                  value={impact.early_accuracy}
                  colorClass="bg-gray-400"
                  label="Earlier practice"
                />
                <ProgressBar
                  value={impact.recent_accuracy}
                  colorClass="bg-green-600"
                  label="Recent practice"
                />
              </div>
              {impact.accuracy_change != null && (
                <p className="mt-2 text-sm text-gray-700">
                  Change:{' '}
                  <span
                    className={
                      impact.accuracy_change >= 0
                        ? 'font-semibold text-green-700'
                        : 'font-semibold text-amber-700'
                    }
                  >
                    {impact.accuracy_change > 0 ? '+' : ''}
                    {impact.accuracy_change}%
                  </span>
                  {impact.accuracy_change < 0 &&
                    ' — Daily Practice can help you close the gap.'}
                </p>
              )}
            </div>
          )}

          {!hasAccuracyTrend && impact.accuracy_change == null && (
            <p className="text-sm text-gray-600">
              Answer at least 10 auto-graded questions to see your accuracy trend.
            </p>
          )}

          {topicTotal > 0 && (
            <div>
              <h4 className="text-sm font-semibold text-gray-900">Topics at a glance</h4>
              <p className="mt-1 text-xs text-gray-500">
                Strong topics (75%+ accuracy) vs. topics that need more practice.
              </p>
              <div className="mt-3 flex h-3 w-full overflow-hidden rounded-full bg-gray-100">
                {strongTopicCount > 0 && (
                  <div
                    className="bg-green-500"
                    style={{ width: `${(strongTopicCount / topicTotal) * 100}%` }}
                    title={`${strongTopicCount} improving`}
                  />
                )}
                {weakTopicCount > 0 && (
                  <div
                    className="bg-orange-400"
                    style={{ width: `${(weakTopicCount / topicTotal) * 100}%` }}
                    title={`${weakTopicCount} need practice`}
                  />
                )}
              </div>
              <div className="mt-2 flex flex-wrap gap-4 text-xs text-gray-600">
                <span>
                  <span className="mr-1 inline-block h-2 w-2 rounded-full bg-green-500" />
                  {strongTopicCount} improving
                </span>
                <span>
                  <span className="mr-1 inline-block h-2 w-2 rounded-full bg-orange-400" />
                  {weakTopicCount} need practice
                </span>
              </div>
            </div>
          )}

          <div>
            <h4 className="text-sm font-semibold text-gray-900">Practice sessions</h4>
            <p className="mt-1 text-xs text-gray-500">
              Each dot is one completed quiz or Daily Practice session.
            </p>
            <div className="mt-2">
              <SessionIndicator count={impact.practice_sessions} />
            </div>
          </div>

          <div className="grid gap-3 sm:grid-cols-2">
            <div className="rounded-lg border border-orange-100 bg-orange-50 px-4 py-3">
              <p className="text-xs font-semibold uppercase tracking-wide text-orange-700">
                Practice streak
              </p>
              <p className="mt-1 text-sm text-orange-900">
                {practiceStreak > 0 ? (
                  <>
                    <span className="font-semibold">{practiceStreak} day</span>
                    {practiceStreak === 1 ? '' : 's'} in a row — keep it going.
                  </>
                ) : (
                  'Complete a Daily Practice session to start your streak.'
                )}
              </p>
              {impact.daily_practice_sessions > 0 && (
                <p className="mt-2 text-sm text-orange-900">
                  <span className="font-semibold">{impact.daily_practice_sessions}</span>{' '}
                  targeted Daily Practice session
                  {impact.daily_practice_sessions === 1 ? '' : 's'} completed.
                </p>
              )}
            </div>

            {impact.accuracy_change != null && !hasAccuracyTrend && (
              <div className="rounded-lg border border-green-100 bg-green-50 px-4 py-3">
                <p className="text-xs font-semibold uppercase tracking-wide text-green-700">
                  Accuracy change
                </p>
                <p className="mt-1 text-sm text-green-900">
                  Recent practice is{' '}
                  <span className="font-semibold">
                    {impact.accuracy_change > 0 ? '+' : ''}
                    {impact.accuracy_change}%
                  </span>{' '}
                  compared to your earlier answers.
                </p>
              </div>
            )}
          </div>
        </div>
      </Card>
    </section>
  )
}

export default LearningImpact
