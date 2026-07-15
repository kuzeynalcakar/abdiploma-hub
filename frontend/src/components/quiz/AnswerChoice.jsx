import { forwardRef, memo } from 'react'
import MathText from '../math/MathText'

// status: null (unanswered), 'correct', 'incorrect', or 'muted'
const statusClasses = {
  correct: 'border-green-600 bg-green-50 text-gray-900',
  incorrect: 'border-red-500 bg-red-50 text-gray-900',
  muted: 'border-gray-200 bg-white text-gray-400',
}

const AnswerChoice = memo(
  forwardRef(function AnswerChoice(
    {
      label,
      isSelected,
      onSelect,
      onKeyDown,
      onFocus,
      disabled,
      status,
      tabIndex,
    },
    ref,
  ) {
    const stateClass = status
      ? statusClasses[status]
      : isSelected
        ? 'border-blue-600 bg-blue-50 text-gray-900 ring-1 ring-blue-600'
        : 'border-gray-300 bg-white text-gray-900 hover:bg-gray-50'

    return (
      <button
        ref={ref}
        type="button"
        role="radio"
        aria-checked={isSelected}
        tabIndex={tabIndex}
        onClick={onSelect}
        onKeyDown={onKeyDown}
        onFocus={onFocus}
        disabled={disabled}
        className={[
          'flex w-full items-center justify-between gap-3 rounded-md border px-4 py-4 text-left text-base focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-600 focus-visible:ring-offset-2 disabled:cursor-not-allowed',
          stateClass,
        ].join(' ')}
      >
        <span className="min-w-0 overflow-x-auto">
          <MathText text={label} />
        </span>
        {status === 'correct' && (
          <span className="shrink-0 text-sm font-medium text-green-700">
            Correct
          </span>
        )}
        {status === 'incorrect' && (
          <span className="shrink-0 text-sm font-medium text-red-600">
            Your answer
          </span>
        )}
      </button>
    )
  }),
)

export default AnswerChoice
