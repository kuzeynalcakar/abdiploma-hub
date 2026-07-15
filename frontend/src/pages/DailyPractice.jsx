import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import AppLayout from '../components/layout/AppLayout'
import DailyPracticeHero from '../components/dashboard/DailyPracticeHero'
import Button from '../components/ui/Button'
import Card from '../components/ui/Card'
import EmptyState from '../components/ui/EmptyState'
import QuizActiveView from '../components/quiz/QuizActiveView'
import QuizResultsView from '../components/quiz/QuizResultsView'
import TopicWeaknessCard from '../components/weakness/TopicWeaknessCard'
import ErrorAlert from '../components/ui/ErrorAlert'
import { api } from '../lib/api'
import { toUserMessage } from '../lib/errors'
import { trackEvent } from '../lib/analytics'
import { buildAnswerPayload } from '../lib/quizHelpers'

function DailyPractice() {
  const navigate = useNavigate()

  // phase: landing -> active -> results
  const [phase, setPhase] = useState('landing')
  const [error, setError] = useState(null)
  const [courses, setCourses] = useState([])
  const [courseId, setCourseId] = useState('')
  const [status, setStatus] = useState(null)
  const [loading, setLoading] = useState(false)

  const [quiz, setQuiz] = useState(null)
  const [currentIndex, setCurrentIndex] = useState(0)
  const [selectedChoiceId, setSelectedChoiceId] = useState(null)
  const [responseText, setResponseText] = useState('')
  const [feedback, setFeedback] = useState(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const submittingRef = useRef(false)
  const resultsHeadingRef = useRef(null)
  const [results, setResults] = useState(null)
  const [weaknessMap, setWeaknessMap] = useState(null)
  const [hasQuizHistory, setHasQuizHistory] = useState(null)

  useEffect(() => {
    api('/progress')
      .then((data) => {
        const completed = data.courses.some((c) => c.quizzes_completed > 0)
        setHasQuizHistory(completed)
      })
      .catch((err) => {
        setHasQuizHistory(null)
        setError(toUserMessage(err, 'Could not check your quiz history. Please try again.'))
      })
  }, [])

  const loadStatus = async (id) => {
    if (!id) return
    setLoading(true)
    setError(null)
    try {
      const data = await api(`/daily-practice?course_id=${id}`)
      setStatus(data)
      if (data.is_completed && data.quiz_attempt_id) {
        const [summary, map] = await Promise.all([
          api(`/quiz/attempt/${data.quiz_attempt_id}/results`),
          api(`/weakness-map?course_id=${id}`),
        ])
        setResults(summary)
        setWeaknessMap(map)
        setPhase('results')
      } else if (!data.is_completed) {
        setPhase('landing')
      }
    } catch (err) {
      setError(toUserMessage(err, 'Something went wrong. Please try again.'))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    api('/courses')
      .then((data) => {
        const available = data.courses.filter((c) => c.question_count > 0)
        setCourses(available)
        if (available.length > 0) {
          setCourseId(String(available[0].id))
        }
      })
      .catch((err) => setError(toUserMessage(err, 'Something went wrong. Please try again.')))
  }, [])

  useEffect(() => {
    if (!courseId || hasQuizHistory !== true) return
    loadStatus(courseId)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [courseId, hasQuizHistory])

  const startPractice = async () => {
    setLoading(true)
    setError(null)
    try {
      let data
      if (status?.is_started && !status?.is_completed) {
        data = await api(`/daily-practice/resume?course_id=${courseId}`)
      } else {
        data = await api(`/daily-practice/start?course_id=${courseId}`, {
          method: 'POST',
        })
      }
      setQuiz({
        quiz_attempt_id: data.quiz_attempt_id,
        course_code: data.course_code,
        questions: data.questions,
      })
      setCurrentIndex(
        status?.completed_count && status.completed_count < data.questions.length
          ? status.completed_count
          : 0,
      )
      setSelectedChoiceId(null)
      setResponseText('')
      setFeedback(null)
      setResults(null)
      trackEvent('daily_practice_started', { course_id: courseId })
      setPhase('active')
    } catch (err) {
      setError(toUserMessage(err, 'Something went wrong. Please try again.'))
    } finally {
      setLoading(false)
    }
  }

  const submitAnswer = async () => {
    if (submittingRef.current || feedback) return
    const question = quiz.questions[currentIndex]
    submittingRef.current = true
    setIsSubmitting(true)
    setError(null)
    try {
      const result = await api('/quiz/answer', {
        method: 'POST',
        body: {
          quiz_attempt_id: quiz.quiz_attempt_id,
          question_id: question.id,
          ...buildAnswerPayload(question, selectedChoiceId, responseText),
        },
      })
      setFeedback(result)
    } catch (err) {
      setError(toUserMessage(err, 'Something went wrong. Please try again.'))
    } finally {
      submittingRef.current = false
      setIsSubmitting(false)
    }
  }

  const goToNext = async () => {
    if (feedback?.attempt_progress?.completed) {
      setError(null)
      try {
        const [summary, map] = await Promise.all([
          api(`/quiz/attempt/${quiz.quiz_attempt_id}/results`),
          api(`/weakness-map?course_id=${courseId}`),
        ])
        setResults(summary)
        setWeaknessMap(map)
        setStatus((prev) =>
          prev
            ? {
                ...prev,
                is_completed: true,
                completed_count: summary.total_questions,
              }
            : prev,
        )
        trackEvent('daily_practice_completed', { course_id: courseId })
        setPhase('results')
      } catch (err) {
        setError(toUserMessage(err, 'Something went wrong. Please try again.'))
      }
      return
    }
    setCurrentIndex(currentIndex + 1)
    setSelectedChoiceId(null)
    setResponseText('')
    setFeedback(null)
  }

  const improvedTopics =
    results?.topics?.filter((t) => t.accuracy >= 60) || []

  const topicFeedback = (results?.topics || []).map((topic) => ({
    topic_id: topic.topic_id,
    topic_name: topic.topic_name,
    message:
      topic.accuracy >= 60
        ? `You improved your ${topic.topic_name} accuracy`
        : `Keep practicing ${topic.topic_name}`,
    improved: topic.accuracy >= 60,
  }))

  const isLastQuestion =
    quiz && currentIndex === quiz.questions.length - 1

  useEffect(() => {
    if (phase === 'results' && results) {
      const frame = window.requestAnimationFrame(() => {
        resultsHeadingRef.current?.focus()
      })
      return () => window.cancelAnimationFrame(frame)
    }
    return undefined
  }, [phase, results])

  return (
    <AppLayout pageTitle="Daily Practice">
      <div className="mx-auto flex max-w-2xl flex-col gap-6">
        {hasQuizHistory === null && !error && (
          <p className="text-center text-sm text-gray-600" role="status" aria-live="polite">
            Checking your practice history…
          </p>
        )}

        {hasQuizHistory === false && (
          <>
            <DailyPracticeHero
              locked
              lockReason="Daily Practice builds short sessions from your previous results. Complete your first practice quiz so we can prioritize topics that need improvement."
              onTakeFirstQuiz={() => navigate('/quiz')}
            />
            <div className="flex justify-center">
              <Button variant="ghost" onClick={() => navigate('/dashboard')}>
                Back to Dashboard
              </Button>
            </div>
          </>
        )}

        {hasQuizHistory !== false && error && (
          <ErrorAlert
            message={error}
            onRetry={() => {
              setError(null)
              if (hasQuizHistory === null) {
                api('/progress')
                  .then((data) => {
                    const completed = data.courses.some((c) => c.quizzes_completed > 0)
                    setHasQuizHistory(completed)
                  })
                  .catch((err) => {
                    setHasQuizHistory(null)
                    setError(
                      toUserMessage(err, 'Could not check your quiz history. Please try again.'),
                    )
                  })
                return
              }
              if (courseId) loadStatus(courseId)
            }}
          />
        )}

        {hasQuizHistory !== false && phase === 'landing' && (
          <>
            {status && !status.is_completed && (
              <Card className="border-2 border-orange-200 bg-gradient-to-br from-orange-50 to-white">
                <h2 className="text-xl font-bold text-gray-900 sm:text-2xl">
                  Today&apos;s Practice
                </h2>
                <p className="mt-2 text-sm leading-relaxed text-gray-700">
                  Daily Practice builds short sessions from your previous results. It is
                  not a random question list—it prioritizes topics where you need
                  improvement and helps you practice regularly.
                </p>

                {status.focus_message && (
                  <p className="mt-4 rounded-lg border border-orange-200 bg-orange-50 px-4 py-3 text-sm leading-relaxed text-orange-900">
                    {status.focus_message}
                  </p>
                )}

                {courses.length > 1 && (
                  <div className="mt-4">
                    <label
                      htmlFor="dp-course"
                      className="text-xs font-medium text-gray-500"
                    >
                      Course
                    </label>
                    <select
                      id="dp-course"
                      className="mt-1 h-10 w-full rounded-md border border-gray-300 bg-white px-4 text-base focus:border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-600"
                      value={courseId}
                      onChange={(e) => setCourseId(e.target.value)}
                    >
                      {courses.map((course) => (
                        <option key={course.id} value={course.id}>
                          {course.name}
                        </option>
                      ))}
                    </select>
                  </div>
                )}

                {status.target_areas?.length > 0 ? (
                  <div className="mt-6">
                    <h3 className="text-sm font-semibold text-gray-900">
                      Topics to focus on today
                    </h3>
                    <p className="mt-1 text-xs text-gray-500">
                      Chosen from your recent accuracy by topic:
                    </p>
                    <ol className="mt-3 flex flex-col gap-2">
                      {status.target_areas.map((area, index) => (
                        <li
                          key={area.topic_id}
                          className="flex items-center justify-between gap-3 rounded-lg border border-orange-100 bg-white px-3 py-2 text-sm"
                        >
                          <span className="min-w-0 break-words font-medium text-gray-900">
                            {index + 1}. {area.topic_name}
                          </span>
                          <span className="shrink-0 text-xs font-semibold text-red-600">
                            {area.accuracy}% accurate
                          </span>
                        </li>
                      ))}
                    </ol>
                  </div>
                ) : (
                  !status.has_history && (
                    <p className="mt-4 rounded-md bg-yellow-50 px-3 py-2 text-sm text-yellow-800">
                      Finish a few more practice questions for a clearer focus list.
                      Today&apos;s set will cover a mix of topics so we can see where
                      you need support.
                    </p>
                  )
                )}

                <div className="mt-6 flex flex-col gap-3 rounded-lg bg-white/80 p-4 sm:flex-row sm:items-center sm:justify-between">
                  <div>
                    <p className="text-xs font-medium uppercase tracking-wide text-gray-500">
                      Questions
                    </p>
                    <p className="text-3xl font-bold text-gray-900">
                      {status.total_questions}
                    </p>
                    <p className="text-xs text-gray-500">
                      ~{status.estimated_time_minutes} min · {status.practice_date}
                    </p>
                  </div>
                  {status.is_started && (
                    <p className="text-sm text-gray-600">
                      {status.completed_count} / {status.total_questions} completed
                    </p>
                  )}
                </div>

                <div className="mt-6">
                  <Button
                    className="w-full sm:w-auto"
                    onClick={startPractice}
                    disabled={loading}
                  >
                    {loading
                      ? 'Loading…'
                      : status.is_started
                        ? 'Resume Daily Practice'
                        : 'Start Daily Practice'}
                  </Button>
                </div>
              </Card>
            )}

            {status?.is_completed && (
              <Card>
                <EmptyState
                  title="Today's practice is complete"
                  description="Good work staying consistent. Come back tomorrow for a new focused set based on how you are doing."
                />
                <div className="mt-4 flex flex-col gap-3 sm:flex-row">
                  <Button
                    variant="secondary"
                    onClick={() => navigate('/weakness-map')}
                  >
                    View Weakness Map
                  </Button>
                  <Button variant="ghost" onClick={() => navigate('/quiz')}>
                    Take a Quiz
                  </Button>
                </div>
              </Card>
            )}

            {courses.length === 0 && !error && (
              <Card>
                <EmptyState
                  title="Courses are still being prepared"
                  description="Practice questions for Alberta courses will appear here when they are ready. Check back soon."
                />
              </Card>
            )}
          </>
        )}

        {hasQuizHistory !== false && phase === 'active' && quiz && (
          <QuizActiveView
            quiz={quiz}
            currentIndex={currentIndex}
            selectedChoiceId={selectedChoiceId}
            onSelectChoice={setSelectedChoiceId}
            responseText={responseText}
            onResponseChange={setResponseText}
            feedback={feedback}
            isSubmitting={isSubmitting}
            onSubmit={submitAnswer}
            onNext={goToNext}
            isLastQuestion={isLastQuestion}
          />
        )}

        {hasQuizHistory !== false && phase === 'results' && results && (
          <>
            <QuizResultsView
              title="Daily Practice Complete"
              subtitle={`${results.correct}/${results.correct + results.wrong} auto-graded correct`}
              results={results}
              headingRef={resultsHeadingRef}
            />

            {topicFeedback.length > 0 && (
              <Card>
                <h3 className="text-base font-semibold text-gray-900">
                  How you did today
                </h3>
                <ul className="mt-3 flex flex-col gap-2">
                  {topicFeedback.map((item) => (
                    <li
                      key={item.topic_id}
                      className={[
                        'rounded-lg px-3 py-2 text-sm',
                        item.improved
                          ? 'bg-green-50 text-green-800'
                          : 'bg-amber-50 text-amber-900',
                      ].join(' ')}
                    >
                      {item.message}
                    </li>
                  ))}
                </ul>
              </Card>
            )}

            {improvedTopics.length > 0 && (
              <Card>
                <h3 className="text-base font-semibold text-gray-900">
                  Topics you handled well today
                </h3>
                <ul className="mt-3 flex flex-col gap-2">
                  {improvedTopics.map((topic) => (
                    <li
                      key={topic.topic_id}
                      className="flex items-start justify-between gap-2 text-sm"
                    >
                      <span className="min-w-0 break-words text-gray-900">
                        {topic.topic_name}
                      </span>
                      <span className="shrink-0 font-medium text-green-700">
                        {topic.accuracy}%
                      </span>
                    </li>
                  ))}
                </ul>
              </Card>
            )}

            {weaknessMap && (
              <section>
                <h3 className="text-base font-semibold text-gray-900">
                  Your Weakness Map after today
                </h3>
                <p className="mt-1 text-sm text-gray-500">
                  Topics that still need review, based on your accuracy so far
                </p>
                <div className="mt-4 flex flex-col gap-3">
                  {weaknessMap.topics
                    .filter((t) =>
                      ['weak', 'critical', 'improving'].includes(t.mastery_level),
                    )
                    .slice(0, 3)
                    .map((topic) => (
                      <TopicWeaknessCard key={topic.topic_id} topic={topic} />
                    ))}
                  {weaknessMap.topics.filter((t) =>
                    ['weak', 'critical'].includes(t.mastery_level),
                  ).length === 0 && (
                    <Card className="border border-green-200 bg-green-50">
                      <p className="text-sm text-green-800">
                        No urgent weak topics right now—keep practicing to stay strong.
                      </p>
                    </Card>
                  )}
                </div>
              </section>
            )}

            <Card className="border border-blue-200 bg-blue-50 text-center">
              <p className="text-lg font-semibold text-blue-900">
                Come back tomorrow
              </p>
              <p className="mt-2 text-sm text-blue-800">
                A new focused practice set will be ready when you return. Short,
                regular sessions help reinforce topics that need more work.
              </p>
            </Card>

            <div className="flex flex-col justify-center gap-3 sm:flex-row">
              <Button
                className="w-full sm:w-auto"
                onClick={() => navigate('/weakness-map')}
              >
                View Full Weakness Map
              </Button>
              <Button
                className="w-full sm:w-auto"
                variant="ghost"
                onClick={() => navigate('/dashboard')}
              >
                Back to Dashboard
              </Button>
            </div>
          </>
        )}
      </div>
    </AppLayout>
  )
}

export default DailyPractice
