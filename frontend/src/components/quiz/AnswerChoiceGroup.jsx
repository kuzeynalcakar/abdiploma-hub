import { useCallback, useEffect, useRef, useState } from 'react'
import AnswerChoice from './AnswerChoice'

function statusFor(choice, feedback, selectedId) {
  if (!feedback) return null
  if (choice.id === feedback.correct_choice_id) return 'correct'
  if (choice.id === selectedId) return 'incorrect'
  return 'muted'
}

/**
 * Keyboard-friendly multiple-choice list (radiogroup + roving tabindex).
 * Arrow keys move focus; Space/Enter select without moving focus away.
 */
function AnswerChoiceGroup({
  choices,
  selectedId,
  onSelect,
  disabled,
  feedback,
  listRef,
}) {
  const buttonRefs = useRef([])
  const [focusIndex, setFocusIndex] = useState(0)

  useEffect(() => {
    buttonRefs.current = buttonRefs.current.slice(0, choices.length)
    const selectedIndex = choices.findIndex((choice) => choice.id === selectedId)
    setFocusIndex(selectedIndex >= 0 ? selectedIndex : 0)
  }, [choices, selectedId])

  const moveFocus = useCallback(
    (nextIndex) => {
      const bound =
        ((nextIndex % choices.length) + choices.length) % choices.length
      setFocusIndex(bound)
      buttonRefs.current[bound]?.focus()
    },
    [choices.length],
  )

  const handleKeyDown = (event, index) => {
    if (disabled) return

    switch (event.key) {
      case 'ArrowDown':
      case 'ArrowRight':
        event.preventDefault()
        moveFocus(index + 1)
        break
      case 'ArrowUp':
      case 'ArrowLeft':
        event.preventDefault()
        moveFocus(index - 1)
        break
      case 'Home':
        event.preventDefault()
        moveFocus(0)
        break
      case 'End':
        event.preventDefault()
        moveFocus(choices.length - 1)
        break
      case ' ':
      case 'Enter':
        event.preventDefault()
        onSelect(choices[index].id)
        break
      default:
        break
    }
  }

  return (
    <div
      ref={listRef}
      className="flex flex-col gap-2"
      role="radiogroup"
      aria-label="Answer choices"
      aria-disabled={disabled || undefined}
    >
      {choices.map((choice, index) => (
        <AnswerChoice
          key={choice.id}
          ref={(node) => {
            buttonRefs.current[index] = node
          }}
          label={choice.label}
          isSelected={choice.id === selectedId}
          onSelect={() => {
            setFocusIndex(index)
            onSelect(choice.id)
          }}
          onFocus={() => setFocusIndex(index)}
          onKeyDown={(event) => handleKeyDown(event, index)}
          disabled={disabled}
          status={statusFor(choice, feedback, selectedId)}
          tabIndex={disabled ? -1 : focusIndex === index ? 0 : -1}
        />
      ))}
    </div>
  )
}

export default AnswerChoiceGroup
