import { useId, useState } from 'react'
import Button from '../ui/Button'
import { api } from '../../lib/api'
import { trackEvent } from '../../lib/analytics'
import { FOCUS_RING } from '../../lib/focusStyles'

const REASONS = [
  { id: 'incorrect_answer', label: 'Incorrect answer' },
  { id: 'confusing_wording', label: 'Confusing wording' },
  { id: 'wrong_explanation', label: 'Wrong explanation' },
  { id: 'other', label: 'Other' },
]

function QuestionReportForm({ questionId, onClose }) {
  const [isOpen, setIsOpen] = useState(false)
  const [reason, setReason] = useState('')
  const [comment, setComment] = useState('')
  const [status, setStatus] = useState('idle')
  const [error, setError] = useState(null)
  const headingId = useId()
  const commentId = useId()
  const errorId = useId()

  const handleSubmit = async (event) => {
    event.preventDefault()
    if (!reason) return
    setError(null)
    setStatus('submitting')
    try {
      await api('/question-reports', {
        method: 'POST',
        body: {
          question_id: questionId,
          reason,
          comment: comment.trim() || null,
        },
      })
      trackEvent('question_reported', { question_id: questionId, reason })
      setStatus('done')
      onClose?.()
    } catch (err) {
      setError(
        typeof err?.message === 'string' && err.message
          ? err.message
          : 'Could not send your report. Please try again.',
      )
      setStatus('idle')
    }
  }

  if (status === 'done') {
    return (
      <p role="status" aria-live="polite" className="mt-3 text-xs text-green-800">
        Report submitted — thank you for helping improve this question.
      </p>
    )
  }

  if (!isOpen) {
    return (
      <button
        type="button"
        onClick={() => setIsOpen(true)}
        className={[
          'mt-4 text-xs font-medium text-gray-700 underline-offset-2 hover:text-gray-900 hover:underline',
          FOCUS_RING,
          'rounded',
        ].join(' ')}
        aria-label="Report this question"
      >
        Report this question
      </button>
    )
  }

  return (
    <form
      className="mt-4 rounded-md border border-gray-200 bg-white p-3"
      onSubmit={handleSubmit}
      aria-labelledby={headingId}
    >
      <p id={headingId} className="text-xs font-semibold text-gray-800">
        Report this question
      </p>
      <fieldset className="mt-2 border-0 p-0">
        <legend className="sr-only">Reason for report</legend>
        <div className="flex flex-col gap-1.5" role="radiogroup" aria-required="true">
          {REASONS.map((item) => (
            <label key={item.id} className="flex items-center gap-2 text-xs text-gray-800">
              <input
                type="radio"
                name="report-reason"
                value={item.id}
                required
                checked={reason === item.id}
                onChange={() => setReason(item.id)}
              />
              {item.label}
            </label>
          ))}
        </div>
      </fieldset>
      <label htmlFor={commentId} className="mt-2 block text-xs font-medium text-gray-700">
        Additional details (optional)
      </label>
      <textarea
        id={commentId}
        rows={2}
        value={comment}
        onChange={(event) => setComment(event.target.value)}
        placeholder="Additional details (optional)"
        className="mt-1 w-full rounded-md border border-gray-300 px-2 py-1.5 text-xs text-gray-900 placeholder:text-gray-500 focus:border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-600"
        aria-describedby={error ? errorId : undefined}
      />
      <div className="mt-2 flex flex-col gap-2 sm:flex-row">
        <Button
          className="w-full sm:w-auto"
          type="submit"
          disabled={!reason || status === 'submitting'}
          aria-busy={status === 'submitting'}
        >
          {status === 'submitting' ? 'Sending…' : 'Submit report'}
        </Button>
        <Button
          className="w-full sm:w-auto"
          type="button"
          variant="ghost"
          onClick={() => {
            setIsOpen(false)
            setReason('')
            setComment('')
          }}
        >
          Cancel
        </Button>
      </div>
      {error && (
        <p id={errorId} role="alert" className="mt-2 text-xs text-red-700">
          {error}
        </p>
      )}
    </form>
  )
}

export default QuestionReportForm
