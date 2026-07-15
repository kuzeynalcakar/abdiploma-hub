import { useId, useState } from 'react'
import Button from '../ui/Button'
import { api } from '../../lib/api'
import { trackEvent } from '../../lib/analytics'
import { FOCUS_RING } from '../../lib/focusStyles'

function QuizFeedbackForm({ courseId, quizAttemptId, onSubmitted }) {
  const [rating, setRating] = useState(null)
  const [message, setMessage] = useState('')
  const [status, setStatus] = useState('idle')
  const [error, setError] = useState(null)
  const headingId = useId()
  const errorId = useId()

  const submit = async (selectedRating) => {
    setRating(selectedRating)
    setError(null)
    setStatus('submitting')
    try {
      await api('/feedback', {
        method: 'POST',
        body: {
          course_id: courseId,
          quiz_attempt_id: quizAttemptId || null,
          rating: selectedRating,
          message: message.trim() || null,
        },
      })
      trackEvent('feedback_submitted', { rating: selectedRating, course_id: courseId })
      setStatus('done')
      onSubmitted?.()
    } catch (err) {
      setError(
        typeof err?.message === 'string' && err.message
          ? err.message
          : 'Could not send feedback. Please try again.',
      )
      setStatus('idle')
      setRating(null)
    }
  }

  if (status === 'done') {
    return (
      <div
        role="status"
        aria-live="polite"
        className="rounded-lg border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-800"
      >
        Thanks for the feedback.
      </div>
    )
  }

  return (
    <section
      className="rounded-lg border border-gray-200 bg-gray-50 px-4 py-4"
      aria-labelledby={headingId}
    >
      <h3 id={headingId} className="text-sm font-medium text-gray-900">
        Help us improve ABDiploma Hub
      </h3>
      <p className="mt-1 text-xs text-gray-600">
        Your feedback helps make practice better for Alberta students.
      </p>

      <div
        className="mt-3 flex flex-col gap-2 sm:flex-row sm:flex-wrap"
        role="group"
        aria-label="How was this practice?"
      >
        <button
          type="button"
          onClick={() => submit('positive')}
          disabled={status === 'submitting'}
          aria-pressed={rating === 'positive'}
          aria-busy={status === 'submitting' && rating === 'positive'}
          className={[
            'inline-flex min-h-11 w-full items-center justify-center rounded-lg border px-4 py-2 text-sm font-medium transition-colors sm:w-auto',
            FOCUS_RING,
            rating === 'positive'
              ? 'border-green-300 bg-green-100 text-green-800'
              : 'border-gray-200 bg-white text-gray-800 hover:bg-gray-100',
          ].join(' ')}
        >
          <span aria-hidden="true">👍 </span>
          This practice helped me
        </button>
        <button
          type="button"
          onClick={() => submit('negative')}
          disabled={status === 'submitting'}
          aria-pressed={rating === 'negative'}
          aria-busy={status === 'submitting' && rating === 'negative'}
          className={[
            'inline-flex min-h-11 w-full items-center justify-center rounded-lg border px-4 py-2 text-sm font-medium transition-colors sm:w-auto',
            FOCUS_RING,
            rating === 'negative'
              ? 'border-amber-300 bg-amber-100 text-amber-900'
              : 'border-gray-200 bg-white text-gray-800 hover:bg-gray-100',
          ].join(' ')}
        >
          <span aria-hidden="true">👎 </span>
          I found an issue
        </button>
      </div>

      <label className="mt-4 block text-xs font-medium text-gray-700" htmlFor="quiz-feedback">
        What should we improve? (optional)
      </label>
      <textarea
        id="quiz-feedback"
        rows={2}
        value={message}
        onChange={(event) => setMessage(event.target.value)}
        placeholder="Tell us what worked or what we should fix…"
        className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm text-gray-900 placeholder:text-gray-500 focus:border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-600"
        aria-describedby={error ? errorId : undefined}
      />

      {error && (
        <p id={errorId} role="alert" className="mt-2 text-xs text-red-700">
          {error}
        </p>
      )}
    </section>
  )
}

export default QuizFeedbackForm
