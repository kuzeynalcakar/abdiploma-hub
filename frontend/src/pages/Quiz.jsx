import { useEffect, useRef, useState } from 'react'

import { useNavigate, useSearchParams } from 'react-router-dom'

import AppLayout from '../components/layout/AppLayout'

import GuestQuizPrompt from '../components/auth/GuestQuizPrompt'

import Button from '../components/ui/Button'

import Card from '../components/ui/Card'

import EmptyState from '../components/ui/EmptyState'

import QuizActiveView from '../components/quiz/QuizActiveView'

import QuizResultsView from '../components/quiz/QuizResultsView'
import QuizFeedbackForm from '../components/feedback/QuizFeedbackForm'

import QuizSetupForm, {

  defaultCountForMax,

} from '../components/quiz/QuizSetupForm'

import { useAuth } from '../context/AuthContext'
import ErrorAlert from '../components/ui/ErrorAlert'
import { api } from '../lib/api'
import { trackEvent } from '../lib/analytics'
import { toUserMessage } from '../lib/errors'
import { courseDocumentTitle } from '../lib/pageTitle'
import {
  buildAnswerPayload,
  buildGuestResults,
} from '../lib/quizHelpers'

function buildAvailabilityParams({ courseId, topicMode, selectedTopicIds, difficulty }) {

  const params = new URLSearchParams({ course_id: courseId })

  if (difficulty) params.set('difficulty', difficulty)

  if (topicMode === 'selected') {

    selectedTopicIds.forEach((id) => {

      params.append('topic_ids', String(id))

    })

  }

  return params

}



function Quiz() {

  const navigate = useNavigate()

  const { user } = useAuth()

  const isGuest = !user

  const [searchParams, setSearchParams] = useSearchParams()

  const initialParamsApplied = useRef(false)

  const skipTopicReset = useRef(false)



  const [phase, setPhase] = useState('setup')

  const [error, setError] = useState(null)



  const [courses, setCourses] = useState([])

  const [topics, setTopics] = useState([])

  const [courseId, setCourseId] = useState(searchParams.get('course_id') || '')

  const [topicMode, setTopicMode] = useState('all')

  const [selectedTopicIds, setSelectedTopicIds] = useState([])

  const [difficulty, setDifficulty] = useState('')

  const [questionCount, setQuestionCount] = useState(10)

  const [availableCount, setAvailableCount] = useState(null)

  const [isStarting, setIsStarting] = useState(false)



  const [quiz, setQuiz] = useState(null)

  const [lastSetup, setLastSetup] = useState(null)

  const [currentIndex, setCurrentIndex] = useState(0)

  const [selectedChoiceId, setSelectedChoiceId] = useState(null)
  const [responseText, setResponseText] = useState('')
  const [feedback, setFeedback] = useState(null)

  const [isSubmitting, setIsSubmitting] = useState(false)
  const submittingRef = useRef(false)
  const resultsHeadingRef = useRef(null)

  const [guestAnswers, setGuestAnswers] = useState([])

  const [results, setResults] = useState(null)

  const [quizNotice, setQuizNotice] = useState(null)



  useEffect(() => {

    api('/courses')

      .then((data) => {

        const available = data.courses.filter((c) => c.question_count > 0)

        setCourses(available)

        if (!searchParams.get('course_id') && available.length > 0) {

          setCourseId(String(available[0].id))

        }

      })

      .catch((err) => setError(toUserMessage(err, 'Could not load quiz data. Please try again.')))

    // eslint-disable-next-line react-hooks/exhaustive-deps

  }, [])



  useEffect(() => {

    if (!courseId) return

    api(`/courses/${courseId}/topics`)

      .then((data) => setTopics(data.topics))

      .catch((err) => setError(toUserMessage(err, 'Could not load quiz data. Please try again.')))

    if (skipTopicReset.current) {

      skipTopicReset.current = false

    } else {

      setSelectedTopicIds([])

      setTopicMode('all')

    }

  }, [courseId])



  useEffect(() => {

    if (initialParamsApplied.current) return

    const paramCourseId = searchParams.get('course_id')

    if (!paramCourseId) return



    const topicParam = searchParams.get('topic_id')

    setCourseId(paramCourseId)

    if (topicParam) {

      setTopicMode('selected')

      setSelectedTopicIds([Number(topicParam)])

    }

    skipTopicReset.current = true

    initialParamsApplied.current = true

    setSearchParams({}, { replace: true })

    // eslint-disable-next-line react-hooks/exhaustive-deps

  }, [searchParams])



  useEffect(() => {

    if (!courseId) return

    if (topicMode === 'selected' && selectedTopicIds.length === 0) {

      setAvailableCount(0)

      return

    }



    const params = buildAvailabilityParams({

      courseId,

      topicMode,

      selectedTopicIds,

      difficulty,

    })



    api(`/quiz/available-count?${params}`)

      .then((data) => {

        setAvailableCount(data.available_count)

        setQuestionCount((prev) => {

          if (data.available_count <= 0) return prev

          if (prev > data.available_count) {

            return defaultCountForMax(data.available_count)

          }

          return prev

        })

      })

      .catch((err) => {

      setAvailableCount(null)

      setError(toUserMessage(err, 'Could not check question availability. Please try again.'))

    })

  }, [courseId, topicMode, selectedTopicIds, difficulty])



  const buildQueryParams = (setup) => {

    const params = new URLSearchParams({

      course_id: setup.courseId,

      count: String(Number(setup.questionCount)),

    })

    if (setup.difficulty) params.set('difficulty', setup.difficulty)

    if (setup.topicMode === 'selected') {

      setup.selectedTopicIds.forEach((id) => {

        params.append('topic_ids', String(id))

      })

    }

    return params

  }



  const startQuiz = async (setup) => {

    setIsStarting(true)

    setError(null)

    try {

      const params = buildQueryParams(setup)

      const endpoint = isGuest

        ? `/quiz/guest/questions?${params}`

        : `/quiz/questions?${params}`

      const data = await api(endpoint)

      setQuiz(data)

      setLastSetup(setup)

      setCurrentIndex(0)
      setSelectedChoiceId(null)
      setResponseText('')
      setFeedback(null)

      setGuestAnswers([])

      setResults(null)

      if (data.partial_fulfillment) {

        setQuizNotice(

          `Only ${data.question_count} question${data.question_count === 1 ? '' : 's'} match your filters (${data.requested_count} requested). The quiz will use all available questions.`,

        )

      } else {

        setQuizNotice(null)

      }

      trackEvent('quiz_started', {
        course_id: setup.courseId,
        guest: Boolean(isGuest),
        question_count: data.question_count,
      })
      if (isGuest) {
        trackEvent('guest_quiz', { course_id: setup.courseId })
      }

      setPhase('active')

    } catch (err) {

      setError(toUserMessage(err, 'Something went wrong. Please try again.'))

      setPhase('setup')

    } finally {

      setIsStarting(false)

    }

  }



  const handleStart = () => {

    startQuiz({

      courseId,

      topicMode,

      selectedTopicIds,

      difficulty,

      questionCount,

    })

  }



  const question = quiz?.questions[currentIndex]

  const isLastQuestion = quiz && currentIndex === quiz.questions.length - 1

  useEffect(() => {
    if (phase === 'results' && results) {
      const frame = window.requestAnimationFrame(() => {
        resultsHeadingRef.current?.focus()
      })
      return () => window.cancelAnimationFrame(frame)
    }
    return undefined
  }, [phase, results])

  const submitAnswer = async () => {
    if (submittingRef.current || feedback) return

    submittingRef.current = true
    setIsSubmitting(true)
    setError(null)

    try {
      const payload = {
        question_id: question.id,
        ...buildAnswerPayload(question, selectedChoiceId, responseText),
      }

      if (isGuest) {
        const result = await api('/quiz/guest/grade', {
          method: 'POST',
          body: payload,
        })
        const answered = guestAnswers.length + 1
        const total = quiz.question_count ?? quiz.questions.length
        setFeedback({
          ...result,
          attempt_progress: {
            answered,
            total,
            completed: answered >= total,
          },
        })
      } else {
        const result = await api('/quiz/answer', {
          method: 'POST',
          body: {
            quiz_attempt_id: quiz.quiz_attempt_id,
            ...payload,
          },
        })
        setFeedback(result)
      }

    } catch (err) {

      setError(toUserMessage(err, 'Something went wrong. Please try again.'))

    } finally {
      submittingRef.current = false
      setIsSubmitting(false)
    }

  }



  const goToNext = async () => {

    if (isGuest) {

      const newAnswer = {
        question_id: question.id,
        topic_id: question.topic.id,
        topic_name: question.topic.name,
        question_type: question.question_type,
        is_correct: feedback.is_correct,
        auto_graded: feedback.auto_graded,
        requires_review: feedback.requires_review,
      }

      const updatedAnswers = [...guestAnswers, newAnswer]



      if (feedback?.attempt_progress?.completed) {

        setGuestAnswers(updatedAnswers)

        setResults(buildGuestResults(quiz, updatedAnswers))

        trackEvent('quiz_completed', {
          guest: true,
          course_id: quiz?.course_id,
        })

        setPhase('results')

        return

      }



      setGuestAnswers(updatedAnswers)
      setCurrentIndex(currentIndex + 1)
      setSelectedChoiceId(null)
      setResponseText('')
      setFeedback(null)
      return

    }



    if (feedback?.attempt_progress?.completed) {

      setError(null)

      try {

        const summary = await api(

          `/quiz/attempt/${quiz.quiz_attempt_id}/results`,

        )

        setResults(summary)

        trackEvent('quiz_completed', {
          guest: false,
          course_id: quiz?.course_id,
          quiz_attempt_id: quiz.quiz_attempt_id,
        })

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



  const resetToSetup = () => {

    setPhase('setup')

    setQuiz(null)

    setResults(null)

    setFeedback(null)

    setGuestAnswers([])

    setError(null)

    setQuizNotice(null)

  }



  const practiceWeakTopics = () => {

    const weakest = results?.topics?.[0]

    if (!weakest) return

    setTopicMode('selected')

    setSelectedTopicIds([weakest.topic_id])

    startQuiz({

      courseId: String(results.course_id),

      topicMode: 'selected',

      selectedTopicIds: [weakest.topic_id],

      difficulty: '',

      questionCount: lastSetup?.questionCount || 10,

    })

  }



  const practiceAgain = () => {

    if (!lastSetup) {

      resetToSetup()

      return

    }

    startQuiz(lastSetup)

  }



  const handleTopicToggle = (topicId) => {

    setSelectedTopicIds((prev) =>

      prev.includes(topicId)

        ? prev.filter((id) => id !== topicId)

        : [...prev, topicId],

    )

  }



  const handleSelectAllTopics = () => {

    if (selectedTopicIds.length === topics.length) {

      setSelectedTopicIds([])

    } else {

      setSelectedTopicIds(topics.map((t) => t.id))

    }

  }



  const handleTopicModeChange = (mode) => {

    setTopicMode(mode)

    if (mode === 'all') {

      setSelectedTopicIds([])

    }

  }



  const weakTopics = results?.topics?.filter((t) => t.accuracy < 75) || []

  const selectedCourse = courses.find((c) => String(c.id) === String(courseId))

  const quizDocumentTitle = selectedCourse
    ? courseDocumentTitle(selectedCourse.code, selectedCourse.name)
    : undefined

  const maxQuestions = selectedCourse?.question_count ?? 0



  let topicAvailabilityMessage = null

  if (topicMode === 'selected' && selectedTopicIds.length > 0) {

    if (availableCount === 0) {

      topicAvailabilityMessage =

        'No questions are available for these topics with the current filters.'

    } else if (availableCount != null && availableCount < questionCount) {

      topicAvailabilityMessage = `Only ${availableCount} question${availableCount === 1 ? '' : 's'} are available for these topics.`

    }

  } else if (topicMode === 'all' && availableCount > 0 && availableCount < questionCount) {

    topicAvailabilityMessage = `Only ${availableCount} question${availableCount === 1 ? '' : 's'} are available for this course.`

  }



  return (

    <AppLayout pageTitle="Practice Quiz" documentTitle={quizDocumentTitle}>

      <div className="mx-auto flex max-w-2xl flex-col gap-6">

        {error && (

          <ErrorAlert

            message={error}

            onRetry={() => {

              setError(null)

              if (phase === 'setup') {

                api('/courses')

                  .then((data) => {

                    const available = data.courses.filter((c) => c.question_count > 0)

                    setCourses(available)

                    if (!searchParams.get('course_id') && available.length > 0) {

                      setCourseId(String(available[0].id))

                    }

                  })

                  .catch((err) => setError(toUserMessage(err, 'Could not load courses. Please try again.')))

              }

            }}

          />

        )}



        {phase === 'setup' && (

          <QuizSetupForm

            courses={courses}

            topics={topics}

            courseId={courseId}

            onCourseChange={setCourseId}

            topicMode={topicMode}

            onTopicModeChange={handleTopicModeChange}

            selectedTopicIds={selectedTopicIds}

            onTopicToggle={handleTopicToggle}

            onSelectAllTopics={handleSelectAllTopics}

            difficulty={difficulty}

            onDifficultyChange={setDifficulty}

            questionCount={questionCount}

            onQuestionCountChange={setQuestionCount}

            availableCount={availableCount}

            topicAvailabilityMessage={topicAvailabilityMessage}

            onStart={handleStart}

            isStarting={isStarting}

            isGuest={isGuest}

            maxQuestions={maxQuestions}

          />

        )}



        {phase === 'active' && quizNotice && (

          <div

            role="status"

            className="rounded-md border border-yellow-200 bg-yellow-50 px-4 py-3 text-sm text-yellow-800"

          >

            {quizNotice}

          </div>

        )}



        {phase === 'active' && !question && isStarting && (

          <p className="text-center text-sm text-gray-600" role="status" aria-live="polite">

            Loading questions…

          </p>

        )}



        {phase === 'active' && question && (

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



        {phase === 'results' && results && (

          <>

            <QuizResultsView

              title="Quiz results"

              subtitle={`${results.correct}/${results.correct + results.wrong} auto-graded correct`}

              results={results}

              headingRef={resultsHeadingRef}

            />

            <QuizFeedbackForm
              courseId={results.course_id || quiz?.course_id}
              quizAttemptId={isGuest ? null : quiz?.quiz_attempt_id}
            />

            {isGuest && <GuestQuizPrompt />}



              <div className="flex flex-col justify-center gap-3 sm:flex-row sm:flex-wrap">

              <Button className="w-full sm:w-auto" onClick={practiceAgain} disabled={isStarting}>

                {isStarting ? 'Loading…' : 'Practice Again'}

              </Button>

              {!isGuest && weakTopics.length > 0 && (

                <Button

                  className="w-full sm:w-auto"

                  variant="secondary"

                  onClick={practiceWeakTopics}

                  disabled={isStarting}

                >

                  Practice Weak Topics

                </Button>

              )}

              <Button className="w-full sm:w-auto" variant="ghost" onClick={() => navigate('/dashboard')}>

                {isGuest ? 'Back to Courses' : 'Return to Dashboard'}

              </Button>

            </div>

          </>

        )}



        {phase === 'setup' && courses.length === 0 && !error && (

          <Card>

            <EmptyState

              title="Loading courses…"

              description="Fetching the available Alberta courses."

            />

          </Card>

        )}

      </div>

    </AppLayout>

  )

}



export default Quiz


