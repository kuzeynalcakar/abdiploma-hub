import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import AppLayout from '../components/layout/AppLayout'
import Button from '../components/ui/Button'
import Card from '../components/ui/Card'
import EmptyState from '../components/ui/EmptyState'
import ErrorAlert from '../components/ui/ErrorAlert'
import DiplomaExamReadiness from '../components/weakness/DiplomaExamReadiness'
import { api } from '../lib/api'
import { toUserMessage } from '../lib/errors'
import { trackEvent } from '../lib/analytics'

const selectClasses =
  'h-10 w-full rounded-md border border-gray-300 bg-white px-4 text-base text-gray-900 focus:border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-600'

function StrongAreaRow({ topic }) {
  return (
    <li className="flex items-center justify-between gap-3 rounded-lg border border-green-100 bg-green-50/60 px-4 py-3">
      <div className="min-w-0">
        <p className="text-sm font-semibold break-words text-gray-900">
          {topic.topic_name}
        </p>
          <p className="mt-0.5 text-xs text-gray-500">
            {topic.questions_attempted} question
            {topic.questions_attempted === 1 ? '' : 's'} completed
          </p>
      </div>
      <span className="shrink-0 rounded-full bg-green-100 px-3 py-1 text-sm font-bold text-green-800">
        {topic.accuracy}%
      </span>
    </li>
  )
}

function NeedsPracticeCard({ topic, onPractice }) {
  return (
    <li className="rounded-xl border-2 border-orange-200 bg-gradient-to-br from-orange-50 via-white to-red-50 p-4 shadow-sm sm:p-5">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0 flex-1">
          <p className="text-xs font-semibold uppercase tracking-wide text-orange-700">
            Topic
          </p>
          <h4 className="mt-1 text-lg font-bold break-words text-gray-900">
            {topic.topic_name}
          </h4>
        </div>
        <div className="shrink-0 text-left sm:text-right">
          <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">
            Accuracy
          </p>
          <p className="mt-1 text-3xl font-bold text-red-600">{topic.accuracy}%</p>
        </div>
      </div>

      <div className="mt-4 space-y-3">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">
            Why
          </p>
          <p className="mt-1 text-sm leading-relaxed text-gray-800">{topic.why}</p>
        </div>
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">
            Action
          </p>
          <p className="mt-1 text-sm font-medium text-gray-900">
            {topic.recommended_action}
          </p>
        </div>
      </div>

      <div className="mt-5">
        <Button className="w-full sm:w-auto" onClick={() => onPractice(topic.topic_id)}>
          Practice This Topic
        </Button>
      </div>
    </li>
  )
}

function WeaknessMap() {
  const navigate = useNavigate()
  const [courses, setCourses] = useState([])
  const [courseId, setCourseId] = useState('')
  const [weaknessMap, setWeaknessMap] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  const loadCourses = () => {
    setError(null)
    api('/courses')
      .then((data) => {
        const available = data.courses.filter((c) => c.question_count > 0)
        setCourses(available)
        if (available.length > 0) {
          setCourseId(String(available[0].id))
        }
      })
      .catch((err) =>
        setError(toUserMessage(err, 'Could not load courses. Please try again.')),
      )
  }

  const loadWeaknessMap = (id = courseId) => {
    if (!id) return
    setLoading(true)
    setError(null)
    api(`/weakness-map?course_id=${id}`)
      .then((data) => {
        setWeaknessMap(data)
        trackEvent('weakness_map_viewed', { course_id: id })
      })
      .catch((err) =>
        setError(toUserMessage(err, 'Could not load your weakness map. Please try again.')),
      )
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    loadCourses()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    loadWeaknessMap(courseId)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [courseId])

  const pageHeading = useMemo(() => {
    if (weaknessMap?.course_name) {
      return `My ${weaknessMap.course_name} Weakness Map`
    }
    return 'My Weakness Map'
  }, [weaknessMap])

  const practiceTopic = (topicId) => {
    navigate(`/quiz?course_id=${courseId}&topic_id=${topicId}`)
  }

  return (
    <AppLayout pageTitle="Weakness Map">
      <div className="mx-auto flex max-w-3xl flex-col gap-6">
        <Card className="border border-blue-100 bg-gradient-to-br from-slate-50 to-white">
          <h2 className="text-xl font-bold text-gray-900 sm:text-2xl">{pageHeading}</h2>
          <p className="mt-2 text-sm leading-relaxed text-gray-700">
            Weakness Map shows your accuracy by topic from your practice answers —
            where you are strong, and where more review is needed.
          </p>
          <ul className="mt-3 space-y-1.5 text-sm text-gray-600">
            <li>• Accuracy by topic from saved practice answers</li>
            <li>• Topics that need review and focused practice</li>
            <li>• Progress you can track as accuracy changes over time</li>
          </ul>

          {courses.length > 0 && (
            <div className="mt-4 max-w-sm">
              <label htmlFor="course" className="text-xs font-medium text-gray-700">
                Course
              </label>
              <select
                id="course"
                className={`${selectClasses} mt-1`}
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

          {weaknessMap && weaknessMap.has_attempted_topics && (
            <p className="mt-4 text-sm text-gray-600">
              Overall accuracy:{' '}
              <span className="font-semibold text-gray-900">
                {weaknessMap.overall_accuracy}%
              </span>
            </p>
          )}
        </Card>

        {error && (
          <ErrorAlert
            message={error}
            onRetry={() => {
              if (!courseId) loadCourses()
              else loadWeaknessMap(courseId)
            }}
          />
        )}

        {loading && (
          <p className="text-center text-sm text-gray-500">
            Reviewing your practice by topic…
          </p>
        )}

        {weaknessMap && !loading && (
          <>
            <DiplomaExamReadiness weaknessMap={weaknessMap} />

            {weaknessMap.has_attempted_topics ? (
              <div className="flex flex-col gap-6">
                {weaknessMap.needs_practice.length > 0 && (
                  <section>
                    <h3 className="text-sm font-semibold uppercase tracking-wide text-orange-700">
                      Needs Practice
                    </h3>
                    <p className="mt-1 text-sm text-gray-500">
                      Start here—these topics need more review based on your accuracy.
                    </p>
                    <ul className="mt-4 flex flex-col gap-4">
                      {weaknessMap.needs_practice.map((topic) => (
                        <NeedsPracticeCard
                          key={topic.topic_id}
                          topic={topic}
                          onPractice={practiceTopic}
                        />
                      ))}
                    </ul>
                  </section>
                )}

                <Card>
                  <h3 className="text-sm font-semibold uppercase tracking-wide text-green-700">
                    Strong Areas
                  </h3>
                  {weaknessMap.strong_topics.length === 0 ? (
                    <p className="mt-3 text-sm text-gray-500">
                      Strong topics will appear here as your accuracy improves.
                      Keep practicing to build them.
                    </p>
                  ) : (
                    <ul className="mt-4 flex flex-col gap-2">
                      {weaknessMap.strong_topics.map((topic) => (
                        <StrongAreaRow key={topic.topic_id} topic={topic} />
                      ))}
                    </ul>
                  )}
                </Card>
              </div>
            ) : (
              <Card>
                <EmptyState
                  title="Complete your first practice session to see your topic overview"
                  description="After you finish a quiz, your Weakness Map will show accuracy by topic, highlight what needs review, and help you track improvement over time."
                />
                <div className="mt-4 flex justify-center">
                  <Button onClick={() => navigate('/quiz')}>Start Practice Quiz</Button>
                </div>
              </Card>
            )}

            {weaknessMap.has_attempted_topics && (
              <div className="flex flex-col items-center gap-2">
                <Button onClick={() => navigate('/daily-practice')}>
                  Start Daily Practice
                </Button>
                <p className="max-w-md text-center text-xs text-gray-500">
                  Daily Practice builds a short session focused on topics from your
                  Weakness Map—not random questions.
                </p>
              </div>
            )}
          </>
        )}

        {courses.length === 0 && !error && (
          <Card>
            <EmptyState
              title="Courses are still being prepared"
              description="Once practice questions are available for a course, your Weakness Map will be ready to use here."
            />
          </Card>
        )}
      </div>
    </AppLayout>
  )
}

export default WeaknessMap
