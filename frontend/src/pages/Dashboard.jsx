import { lazy, Suspense, useEffect, useState, memo } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import AppLayout from '../components/layout/AppLayout'
import GuestSignupCTA from '../components/auth/GuestSignupCTA'
import DailyPracticeHero from '../components/dashboard/DailyPracticeHero'
import Button from '../components/ui/Button'
import Card from '../components/ui/Card'
import EmptyState from '../components/ui/EmptyState'
import ErrorAlert from '../components/ui/ErrorAlert'
import { useAuth } from '../context/AuthContext'
import { api } from '../lib/api'
import { toUserMessage } from '../lib/errors'
import { LINK_FOCUS } from '../lib/focusStyles'
import { prefetchRoute } from '../lib/prefetchRoute'

const LearningImpact = lazy(() => import('../components/dashboard/LearningImpact'))

const ProgressCard = memo(function ProgressCard({ progress, onPracticeWeak }) {
  const stats = [
    { label: 'Quizzes completed', value: progress.quizzes_completed },
    { label: 'Questions answered', value: progress.questions_answered },
    { label: 'Correct answers', value: progress.correct_answers },
    { label: 'Accuracy', value: `${progress.accuracy_percent}%` },
  ]

  return (
    <article>
    <Card>
      <h3 className="text-lg font-semibold text-gray-900">
        {progress.course_name} Progress
      </h3>

      <dl className="mt-4 grid grid-cols-2 gap-4 sm:grid-cols-4">
        {stats.map((stat) => (
          <div key={stat.label} className="rounded-md bg-gray-50 p-3">
            <dd className="text-xl font-semibold text-gray-900">{stat.value}</dd>
            <dt className="mt-1 text-xs font-medium text-gray-600">{stat.label}</dt>
          </div>
        ))}
      </dl>

      <div className="mt-5 grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div>
          <h4 className="text-sm font-semibold text-green-800">Strong topics</h4>
          {progress.strong_topics.length === 0 ? (
            <p className="mt-2 text-sm text-gray-500">None yet — keep practicing.</p>
          ) : (
            <ul className="mt-2 flex flex-col gap-1.5">
              {progress.strong_topics.map((topic) => (
                <li
                  key={topic.topic_id}
                  className="flex items-start justify-between gap-2 text-sm"
                >
                  <span className="min-w-0 break-words text-gray-900">
                    {topic.topic_name}
                  </span>
                  <span className="shrink-0 text-xs font-medium text-green-700">
                    {topic.accuracy}%
                  </span>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div>
          <h4 className="text-sm font-semibold text-red-700">Needs practice</h4>
          {progress.weak_topics.length === 0 ? (
            <p className="mt-2 text-sm text-gray-500">Nothing flagged for review.</p>
          ) : (
            <ul className="mt-2 flex flex-col gap-1.5">
              {progress.weak_topics.map((topic) => (
                <li
                  key={topic.topic_id}
                  className="flex items-start justify-between gap-2 text-sm"
                >
                  <span className="min-w-0 break-words text-gray-900">
                    {topic.topic_name}
                  </span>
                  <span className="shrink-0 text-xs font-medium text-red-600">
                    {topic.accuracy}%
                  </span>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>

      {progress.weak_topics.length > 0 && (
        <div className="mt-5">
          <Button
            variant="secondary"
            onClick={() =>
              onPracticeWeak(progress.course_id, progress.weak_topics[0].topic_id)
            }
          >
            Practice weakest topic
          </Button>
        </div>
      )}
    </Card>
    </article>
  )
})

function Dashboard() {
  const navigate = useNavigate()
  const { user } = useAuth()
  const isGuest = !user

  const [courses, setCourses] = useState(null)
  const [progress, setProgress] = useState(null)
  const [impact, setImpact] = useState(null)
  const [practiceStreak, setPracticeStreak] = useState(0)
  const [dailyStatus, setDailyStatus] = useState(null)
  const [dailyLoading, setDailyLoading] = useState(false)
  const [error, setError] = useState(null)
  const [progressError, setProgressError] = useState(null)

  const availableCourses = courses?.filter((c) => c.question_count > 0) || []
  const defaultCourseId = availableCourses[0]?.id

  const loadCourses = () => {
    setError(null)
    api('/courses')
      .then((data) => setCourses(data.courses))
      .catch((err) => {
        setCourses(null)
        setError(toUserMessage(err, 'Could not load courses. Please try again.'))
      })
  }

  const loadProgress = () => {
    if (!user) return
    setProgressError(null)
    api('/progress')
      .then((data) => {
        setProgress(data.courses)
        setPracticeStreak(data.practice_streak || 0)
        setImpact(data.impact || null)
      })
      .catch((err) => {
        setProgress(null)
        setPracticeStreak(0)
        setImpact(null)
        setProgressError(
          toUserMessage(err, 'Could not load your progress. Please try again.'),
        )
      })
  }

  useEffect(() => {
    loadCourses()
    if (user) loadProgress()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user])

  useEffect(() => {
    if (!user || !defaultCourseId) return
    setDailyLoading(true)
    api(`/daily-practice?course_id=${defaultCourseId}`)
      .then(setDailyStatus)
      .catch(() => setDailyStatus(null))
      .finally(() => setDailyLoading(false))
  }, [user, defaultCourseId])

  const hasQuizHistory =
    progress?.some((p) => p.quizzes_completed > 0) ?? false

  const handlePracticeWeak = (courseId, topicId) => {
    navigate(`/quiz?course_id=${courseId}&topic_id=${topicId}`)
  }

  const comingSoonCourses = courses?.filter((c) => c.question_count === 0)

  return (
    <AppLayout pageTitle="Dashboard">
      <div className="mx-auto flex max-w-4xl flex-col gap-8">
        <Card>
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div className="min-w-0">
              {isGuest ? (
                <>
                  <h2 className="text-xl font-semibold break-words text-gray-900 sm:text-2xl">
                    Welcome to ABDiploma Hub
                  </h2>
                  <p className="mt-1 text-sm text-gray-600">
                    Start practicing Alberta Diploma Exam questions for free — Biology
                    30, Chemistry 30, Physics 30, Math, Science, and Social Studies
                    courses available now.
                  </p>
                </>
              ) : (
                <>
                  <h2 className="text-xl font-semibold break-words text-gray-900 sm:text-2xl">
                    Welcome back, {user?.name}
                  </h2>
                  <p className="mt-1 truncate text-sm text-gray-500">{user?.email}</p>
                  {practiceStreak > 0 && (
                    <p className="mt-2 text-sm font-semibold text-orange-800">
                      {practiceStreak} day practice streak
                    </p>
                  )}
                </>
              )}
            </div>
            {isGuest && (
              <div className="flex shrink-0 flex-col gap-2 sm:flex-row">
                <Link
                  to="/register"
                  className={[
                    'inline-flex min-h-10 items-center justify-center rounded-lg bg-blue-600 px-4 text-sm font-semibold text-white hover:bg-blue-700',
                    LINK_FOCUS,
                  ].join(' ')}
                >
                  Create free account
                </Link>
                <Link
                  to="/login"
                  className={[
                    'inline-flex min-h-10 items-center justify-center rounded-lg border border-gray-300 px-4 text-sm font-medium text-gray-700 hover:bg-gray-50',
                    LINK_FOCUS,
                  ].join(' ')}
                >
                  Log in
                </Link>
              </div>
            )}
          </div>
        </Card>

        {isGuest ? (
          <DailyPracticeHero guestMode />
        ) : (
          <DailyPracticeHero
            status={dailyStatus}
            loading={dailyLoading}
            locked={!hasQuizHistory}
            lockReason="Complete your first practice quiz to use Daily Practice. It focuses on topics where you need improvement and helps you keep a steady study habit."
            onStart={() => navigate('/daily-practice')}
            onTakeFirstQuiz={() => navigate('/quiz')}
          />
        )}

          <section aria-labelledby="your-courses-heading">
            <h2 id="your-courses-heading" className="text-xl font-semibold text-gray-900">
              Your courses
            </h2>
          <p className="mt-1 text-sm text-gray-500">
            {isGuest
              ? 'Pick a course and customize your quiz — topics, difficulty, and length.'
              : 'Pick a course and start practicing with instant feedback.'}
          </p>

          {error && (
            <ErrorAlert className="mt-4" message={error} onRetry={loadCourses} />
          )}

          {progressError && (
            <ErrorAlert className="mt-4" message={progressError} onRetry={loadProgress} />
          )}

          {!courses && !error && (
            <p className="mt-6 text-sm text-gray-600" role="status" aria-live="polite">
              Loading courses…
            </p>
          )}

          {courses && availableCourses.length === 0 && (
            <Card className="mt-4">
              <EmptyState
                title="Courses are still being prepared"
                description="Practice questions will appear here when a course is ready. Then you can use Weakness Map and Daily Practice after you answer a few."
              />
            </Card>
          )}

          {availableCourses.length > 0 && (
            <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
              {availableCourses.map((course) => (
                <Card key={course.id} className="flex flex-col gap-3">
                  <div className="flex items-start justify-between gap-2">
                    <h3 className="min-w-0 text-lg font-semibold break-words text-gray-900">
                      {course.name}
                    </h3>
                    <span className="shrink-0 rounded-full bg-blue-100 px-2.5 py-0.5 text-xs font-medium text-blue-800">
                      {course.code}
                    </span>
                  </div>
                  <p className="flex-1 text-sm text-gray-500">
                    {`${course.question_count} practice question${
                      course.question_count === 1 ? '' : 's'
                    } available`}
                  </p>
                  <Button
                    onClick={() => navigate(`/quiz?course_id=${course.id}`)}
                    onPointerEnter={() => prefetchRoute('quiz')}
                    onFocus={() => prefetchRoute('quiz')}
                  >
                    Set Up Quiz
                  </Button>
                </Card>
              ))}
            </div>
          )}
        </section>

        {!isGuest && (
          <Suspense fallback={null}>
            <LearningImpact
              impact={impact}
              practiceStreak={practiceStreak}
              courseProgress={progress || []}
            />
          </Suspense>
        )}

        {isGuest && (
          <GuestSignupCTA
            title="Save your progress"
            description="Create a free account to keep quiz results, open your Weakness Map, and use Daily Practice on the topics you need most."
          />
        )}

        {!isGuest && progress && progress.length > 0 && (
          <section aria-labelledby="course-progress-heading">
            <h2 id="course-progress-heading" className="text-xl font-semibold text-gray-900">
              Course progress
            </h2>
            <div className="mt-4 flex flex-col gap-4">
              {progress.map((courseProgress) => (
                <ProgressCard
                  key={courseProgress.course_id}
                  progress={courseProgress}
                  onPracticeWeak={handlePracticeWeak}
                />
              ))}
            </div>
          </section>
        )}

        {comingSoonCourses && comingSoonCourses.length > 0 && (
          <section aria-labelledby="coming-soon-heading">
            <h2 id="coming-soon-heading" className="text-base font-semibold text-gray-800">
              Coming soon
            </h2>
            <p className="mt-1 text-sm text-gray-500">
              These Alberta courses are on the platform but don&apos;t have practice
              questions yet.
            </p>
            <div className="mt-3 flex flex-wrap gap-2">
              {comingSoonCourses.map((course) => (
                <span
                  key={course.id}
                  className="rounded-full border border-gray-200 bg-gray-50 px-3 py-1 text-xs text-gray-500"
                >
                  {course.name}
                </span>
              ))}
            </div>
          </section>
        )}

        <Card className="border border-gray-200 bg-gray-50">
          <h2 className="text-base font-semibold text-gray-900">About ABDiploma Hub</h2>
          <p className="mt-2 text-sm leading-6 text-gray-600">
            ABDiploma Hub is free Alberta diploma exam practice for high school
            students. Take quizzes, check accuracy by topic on Weakness Map, and use
            Daily Practice to review areas that need more work.
          </p>
          <Link
            to="/about"
            className={[
              'mt-3 inline-block rounded text-sm font-medium text-blue-700 hover:text-blue-800',
              LINK_FOCUS,
            ].join(' ')}
          >
            Learn more
          </Link>
        </Card>
      </div>
    </AppLayout>
  )
}

export default Dashboard
