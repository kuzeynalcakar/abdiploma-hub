import { useEffect, useRef } from 'react'
import Button from '../ui/Button'
import QuestionCard from './QuestionCard'
import AnswerChoiceGroup from './AnswerChoiceGroup'
import ResponseInput from './ResponseInput'
import MetadataBadge from './MetadataBadge'
import FeedbackPanel from './FeedbackPanel'
import QuestionReportForm from '../feedback/QuestionReportForm'
import { canSubmitAnswer } from '../../lib/quizHelpers'

const difficultyClasses = {
  easy: 'bg-green-100 text-green-800',
  medium: 'bg-yellow-100 text-yellow-900',
  hard: 'bg-red-100 text-red-800',
}

const typeLabels = {
  multiple_choice: 'Multiple Choice',
  numerical_response: 'Numerical Response',
  written_response: 'Written Response',
}

function QuizActiveView({
  quiz,
  currentIndex,
  selectedChoiceId,
  onSelectChoice,
  responseText,
  onResponseChange,
  feedback,
  isSubmitting,
  onSubmit,
  onNext,
  isLastQuestion,
  nextLabel = 'Next question',
}) {
  const question = quiz.questions[currentIndex]
  const totalQuestions = quiz.question_count ?? quiz.questions.length
  const answeredCount = feedback
    ? feedback.attempt_progress.answered
    : currentIndex
  const progressPercent = Math.round(
    (answeredCount / totalQuestions) * 100,
  )
  const canSubmit = canSubmitAnswer(
    question,
    selectedChoiceId,
    responseText,
  )
  const progressLabel = `Question ${currentIndex + 1} of ${totalQuestions}`

  const feedbackHeadingRef = useRef(null)
  const nextButtonRef = useRef(null)
  const choiceListRef = useRef(null)
  const responseInputRef = useRef(null)
  const prevFeedbackRef = useRef(null)
  const prevQuestionIdRef = useRef(null)

  const handleFormSubmit = (event) => {
    event.preventDefault()
    if (feedback || isSubmitting || !canSubmit) return
    onSubmit()
  }

  // After grading: announce feedback, then keyboard users reach Next on one Tab.
  useEffect(() => {
    if (feedback && !prevFeedbackRef.current) {
      feedbackHeadingRef.current?.focus()
    }
    prevFeedbackRef.current = feedback
  }, [feedback])

  // New question: move focus into the answer control (MC list or short-answer field).
  useEffect(() => {
    const questionChanged = prevQuestionIdRef.current !== question.id
    prevQuestionIdRef.current = question.id
    if (!questionChanged || feedback) return

    const frame = window.requestAnimationFrame(() => {
      if (question.question_type === 'multiple_choice') {
        const first =
          choiceListRef.current?.querySelector('[role="radio"][tabindex="0"]') ||
          choiceListRef.current?.querySelector('[role="radio"]')
        first?.focus()
      } else {
        responseInputRef.current?.focus()
      }
    })
    return () => window.cancelAnimationFrame(frame)
  }, [question.id, question.question_type, feedback])

  return (
    <div className="flex flex-col gap-6">
      <form
        className="flex flex-col gap-6"
        onSubmit={handleFormSubmit}
        noValidate
        aria-label="Answer this question"
      >
        <div>
          <div className="flex items-center justify-between text-sm text-gray-600">
            <span id="quiz-progress-label">{progressLabel}</span>
            <span aria-hidden="true">{progressPercent}% complete</span>
            <span className="sr-only">{progressPercent} percent complete</span>
          </div>
          <div
            role="progressbar"
            aria-valuenow={progressPercent}
            aria-valuemin={0}
            aria-valuemax={100}
            aria-labelledby="quiz-progress-label"
            className="mt-2 h-2 w-full rounded-full bg-gray-100"
          >
            <div
              className="h-2 rounded-full bg-blue-600 transition-[width]"
              style={{ width: `${progressPercent}%` }}
            />
          </div>
        </div>

        <ul className="flex list-none flex-wrap gap-2 p-0" aria-label="Question details">
          <li>
            <MetadataBadge
              value={quiz.course_code}
              className="bg-blue-100 text-blue-800"
            />
          </li>
          <li>
            <MetadataBadge
              value={typeLabels[question.question_type] || question.question_type}
              className="bg-purple-100 text-purple-900"
            />
          </li>
          <li>
            <MetadataBadge value={question.unit} />
          </li>
          <li>
            <MetadataBadge value={question.topic.name} />
          </li>
          <li>
            <MetadataBadge
              value={question.difficulty}
              className={
                difficultyClasses[question.difficulty] ||
                'bg-gray-100 text-gray-800'
              }
            />
          </li>
        </ul>

        <QuestionCard questionText={question.question_text}>
          {question.question_type === 'multiple_choice' ? (
            <AnswerChoiceGroup
              listRef={choiceListRef}
              choices={question.choices}
              selectedId={selectedChoiceId}
              onSelect={onSelectChoice}
              disabled={isSubmitting || Boolean(feedback)}
              feedback={feedback}
            />
          ) : (
            <ResponseInput
              key={question.id}
              inputRef={responseInputRef}
              questionType={question.question_type}
              responseFormat={question.response_format || 'numeric'}
              value={responseText}
              onChange={onResponseChange}
              disabled={isSubmitting || Boolean(feedback)}
              onSubmitAnswer={handleFormSubmit}
            />
          )}
        </QuestionCard>

        {isSubmitting && (
          <p className="sr-only" role="status" aria-live="polite">
            Checking your answer…
          </p>
        )}

        {!feedback && (
          <div className="flex flex-col items-stretch justify-end gap-3 sm:flex-row sm:items-center">
            <Button
              type="submit"
              className="w-full sm:w-auto"
              disabled={isSubmitting || !canSubmit}
              aria-busy={isSubmitting}
            >
              {isSubmitting ? 'Checking…' : 'Submit answer'}
            </Button>
          </div>
        )}
      </form>

      {feedback && (
        <>
          <FeedbackPanel ref={feedbackHeadingRef} feedback={feedback} />
          <div className="flex flex-col items-stretch justify-end gap-3 sm:flex-row sm:items-center">
            <Button
              ref={nextButtonRef}
              type="button"
              className="w-full sm:w-auto"
              onClick={onNext}
              aria-label={isLastQuestion ? 'See results' : nextLabel}
            >
              {isLastQuestion ? 'See results' : nextLabel}
            </Button>
          </div>
          <QuestionReportForm questionId={question.id} />
        </>
      )}
    </div>
  )
}

export default QuizActiveView
