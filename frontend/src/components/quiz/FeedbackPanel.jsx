import { forwardRef } from 'react'
import MathText from '../math/MathText'

/**
 * Post-submit feedback: explanations + status. Focusable heading for keyboard flow.
 * (Question reporting lives outside the answer form so Enter cannot nest forms.)
 */
const FeedbackPanel = forwardRef(function FeedbackPanel({ feedback }, ref) {
  const isReview = feedback.requires_review
  const isCorrect = feedback.is_correct === true
  const isIncorrect = feedback.is_correct === false

  let heading = 'Submitted'
  let toneClasses = 'border-blue-200 bg-blue-50'
  let headingClasses = 'text-blue-800'

  if (isReview) {
    heading = 'Compare your response with the solution guide'
    toneClasses = 'border-blue-200 bg-blue-50'
    headingClasses = 'text-blue-900'
  } else if (isCorrect) {
    heading = 'Correct'
    toneClasses = 'border-green-200 bg-green-50'
    headingClasses = 'text-green-800'
  } else if (isIncorrect) {
    heading = 'Not quite.'
    toneClasses = 'border-red-200 bg-red-50'
    headingClasses = 'text-red-800'
  }

  return (
    <div
      className={['rounded-lg border p-5', toneClasses].join(' ')}
      role="status"
      aria-live="polite"
      aria-atomic="true"
    >
      <p
        ref={ref}
        tabIndex={-1}
        className={[
          'text-base font-semibold outline-none focus-visible:ring-2 focus-visible:ring-blue-600 focus-visible:ring-offset-2',
          headingClasses,
        ].join(' ')}
      >
        {heading}
      </p>

      {isReview && (
        <p className="mt-2 text-sm text-blue-800">
          Review required — compare your work with the model solution below.
        </p>
      )}

      {feedback.expected_answer && (
        <div className="mt-3">
          <p className="text-xs font-semibold uppercase tracking-wide text-gray-600">
            {feedback.question_type === 'written_response'
              ? 'Model solution'
              : 'Expected answer'}
          </p>
          <p className="mt-1 text-sm leading-6 text-gray-800">
            <MathText text={feedback.expected_answer} />
          </p>
        </div>
      )}

      {feedback.explanation && (
        <div className="mt-3">
          <p className="text-xs font-semibold uppercase tracking-wide text-gray-600">
            {feedback.question_type === 'written_response'
              ? 'Solution guide / rubric'
              : 'Explanation'}
          </p>
          <p className="mt-1 text-sm leading-6 text-gray-800">
            <MathText text={feedback.explanation} />
          </p>
        </div>
      )}

      {feedback.common_mistake && !isReview && (
        <div className="mt-4">
          <p className="text-xs font-semibold uppercase tracking-wide text-gray-600">
            Common mistake
          </p>
          <p className="mt-1 text-sm leading-6 text-gray-800">
            <MathText text={feedback.common_mistake} />
          </p>
        </div>
      )}
    </div>
  )
})

export default FeedbackPanel
