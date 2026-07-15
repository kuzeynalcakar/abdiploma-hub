import { useId } from 'react'
import Button from '../ui/Button'
import Card from '../ui/Card'
import { FOCUS_RING } from '../../lib/focusStyles'

const selectClasses =
  'h-10 w-full rounded-md border border-gray-300 bg-white px-4 text-base text-gray-900 focus:border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-600'

const QUESTION_COUNTS = [10, 20, 30, 50]

export function buildCountOptions(maxQuestions) {
  if (maxQuestions > 0 && maxQuestions < 10) {
    return [maxQuestions]
  }
  return QUESTION_COUNTS
}

export function defaultCountForMax(maxQuestions) {
  if (maxQuestions <= 0) return 10
  const options = buildCountOptions(maxQuestions)
  const valid = options.filter((count) => count <= maxQuestions)
  return valid[valid.length - 1] ?? maxQuestions
}

const DIFFICULTIES = [
  { value: '', label: 'Any' },
  { value: 'easy', label: 'Easy' },
  { value: 'medium', label: 'Medium' },
  { value: 'hard', label: 'Hard' },
]

function QuizSetupForm({
  courses,
  topics,
  courseId,
  onCourseChange,
  topicMode,
  onTopicModeChange,
  selectedTopicIds,
  onTopicToggle,
  onSelectAllTopics,
  difficulty,
  onDifficultyChange,
  questionCount,
  onQuestionCountChange,
  availableCount,
  topicAvailabilityMessage,
  onStart,
  isStarting,
  isGuest = false,
  maxQuestions = 0,
}) {
  const topicsLegendId = useId()
  const countGroupId = useId()
  const availabilityId = useId()
  const countHelpId = useId()

  const allSelected =
    topics.length > 0 && selectedTopicIds.length === topics.length

  const countOptions = buildCountOptions(
    availableCount > 0 ? availableCount : maxQuestions,
  )
  const effectiveMax = availableCount > 0 ? availableCount : maxQuestions
  const hasDisabledCounts =
    effectiveMax > 0 && countOptions.some((count) => count > effectiveMax)

  return (
    <Card>
      <form
        onSubmit={(event) => {
          event.preventDefault()
          if (
            !courseId ||
            isStarting ||
            (topicMode === 'selected' && selectedTopicIds.length === 0)
          ) {
            return
          }
          onStart()
        }}
        noValidate
      >
      <h2 className="text-lg font-semibold text-gray-900">Set up your quiz</h2>
      <p className="mt-1 text-sm text-gray-600">
        Choose your course, topics, difficulty, and question count before you
        begin.
        {isGuest && ' No account required.'}
      </p>
      {maxQuestions > 0 && (
        <p className="mt-2 text-sm font-medium text-blue-800" role="status">
          You have {maxQuestions} available questions
        </p>
      )}

      <div className="mt-6 flex flex-col gap-2">
        <label htmlFor="course" className="text-xs font-medium text-gray-700">
          Course <span className="text-red-700" aria-hidden="true">*</span>
          <span className="sr-only">(required)</span>
        </label>
        <select
          id="course"
          className={selectClasses}
          value={courseId}
          required
          onChange={(e) => onCourseChange(e.target.value)}
        >
          {courses.map((course) => (
            <option key={course.id} value={course.id}>
              {course.name}
              {course.question_count === 0 ? ' (no questions yet)' : ''}
            </option>
          ))}
        </select>
      </div>

      {topics.length > 0 && (
        <fieldset className="mt-6 border-0 p-0">
          <legend id={topicsLegendId} className="text-xs font-medium text-gray-700">
            Topics
          </legend>

          <div
            className="mt-2 flex flex-col gap-2"
            role="radiogroup"
            aria-labelledby={topicsLegendId}
          >
            <label className="flex cursor-pointer items-center gap-3 text-sm text-gray-800">
              <input
                type="radio"
                name="topic-mode"
                className="h-4 w-4 border-gray-300 text-blue-600 focus:ring-blue-600"
                checked={topicMode === 'all'}
                onChange={() => onTopicModeChange('all')}
              />
              <span>All topics</span>
            </label>
            <label className="flex cursor-pointer items-center gap-3 text-sm text-gray-800">
              <input
                type="radio"
                name="topic-mode"
                className="h-4 w-4 border-gray-300 text-blue-600 focus:ring-blue-600"
                checked={topicMode === 'selected'}
                onChange={() => onTopicModeChange('selected')}
              />
              <span>Select specific topics</span>
            </label>
          </div>

          {topicMode === 'selected' && (
            <div className="mt-3">
              <div className="flex items-center justify-between gap-2">
                <span className="text-xs text-gray-600">Choose one or more</span>
                <button
                  type="button"
                  onClick={onSelectAllTopics}
                  className={[
                    'rounded text-xs font-medium text-blue-700 hover:text-blue-800',
                    FOCUS_RING,
                  ].join(' ')}
                >
                  {allSelected ? 'Deselect all' : 'Select all topics'}
                </button>
              </div>
              <div
                className="mt-2 max-h-48 space-y-2 overflow-y-auto rounded-md border border-gray-200 p-3"
                role="group"
                aria-label="Topic checklist"
              >
                {topics.map((topic) => (
                  <label
                    key={topic.id}
                    className="flex cursor-pointer items-start gap-3 text-sm text-gray-800"
                  >
                    <input
                      type="checkbox"
                      className="mt-0.5 h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-600"
                      checked={selectedTopicIds.includes(topic.id)}
                      onChange={() => onTopicToggle(topic.id)}
                    />
                    <span>{topic.name}</span>
                  </label>
                ))}
              </div>
            </div>
          )}

          {topicAvailabilityMessage && (
            <p
              id={availabilityId}
              role="status"
              className="mt-3 rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-900"
            >
              {topicAvailabilityMessage}
            </p>
          )}
        </fieldset>
      )}

      <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div className="flex flex-col gap-2">
          <label htmlFor="difficulty" className="text-xs font-medium text-gray-700">
            Difficulty
          </label>
          <select
            id="difficulty"
            className={selectClasses}
            value={difficulty}
            onChange={(e) => onDifficultyChange(e.target.value)}
          >
            {DIFFICULTIES.map((option) => (
              <option key={option.value || 'any'} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>

        <fieldset className="flex flex-col gap-2 border-0 p-0">
          <legend id={countGroupId} className="text-xs font-medium text-gray-700">
            Number of questions
          </legend>
          {effectiveMax > 0 && (
            <p id={countHelpId} className="text-xs text-gray-600">
              {availableCount > 0
                ? `${availableCount} question${availableCount === 1 ? '' : 's'} available for your current filters.`
                : `Up to ${maxQuestions} questions available for this course.`}
            </p>
          )}
          <div
            className="grid grid-cols-2 gap-2 sm:grid-cols-4"
            role="group"
            aria-labelledby={countGroupId}
            aria-describedby={effectiveMax > 0 ? countHelpId : undefined}
          >
            {countOptions.map((count) => {
              const isDisabled = effectiveMax > 0 && count > effectiveMax
              const isSelected = questionCount === count
              return (
                <button
                  key={count}
                  type="button"
                  onClick={() => !isDisabled && onQuestionCountChange(count)}
                  disabled={isDisabled}
                  aria-pressed={isSelected}
                  aria-label={`${count} questions`}
                  title={
                    isDisabled
                      ? `Only ${effectiveMax} questions available`
                      : undefined
                  }
                  className={[
                    'min-h-10 rounded-md border px-3 py-2 text-sm font-medium transition-colors',
                    FOCUS_RING,
                    isDisabled
                      ? 'cursor-not-allowed border-gray-200 bg-gray-50 text-gray-500'
                      : isSelected
                        ? 'border-blue-600 bg-blue-50 text-blue-800'
                        : 'border-gray-300 bg-white text-gray-800 hover:bg-gray-50',
                  ].join(' ')}
                >
                  {count}
                </button>
              )
            })}
          </div>
          {hasDisabledCounts && (
            <p className="text-xs text-amber-800">
              Some lengths are unavailable for your selected topics and
              difficulty.
            </p>
          )}
        </fieldset>
      </div>

      <div className="mt-6">
        <Button
          type="submit"
          className="w-full sm:w-auto"
          aria-busy={isStarting}
          disabled={
            !courseId ||
            isStarting ||
            (topicMode === 'selected' && selectedTopicIds.length === 0)
          }
        >
          {isStarting ? 'Loading questions…' : 'Start Quiz'}
        </Button>
      </div>
      </form>
    </Card>
  )
}

export default QuizSetupForm
