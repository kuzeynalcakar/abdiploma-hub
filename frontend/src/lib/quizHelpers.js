export function isValidNumericalInput(value) {
  if (typeof value !== 'string') return false
  const trimmed = value.trim()
  if (!trimmed) return false
  // Match backend float()-style parsing (strip surrounding $ only).
  const normalized = trimmed.replace(/^\$/, '').replace(/\$$/, '').trim()
  if (!normalized) return false
  // Reject values Number() accepts but Python float() rejects (e.g. 0x10).
  if (!/^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$/.test(normalized)) {
    return false
  }
  return Number.isFinite(Number(normalized))
}

export function buildAnswerPayload(question, selectedChoiceId, responseText) {
  if (question.question_type === 'multiple_choice') {
    return { answer_choice_id: selectedChoiceId }
  }
  return { response_text: String(responseText ?? '').trim() }
}

export function canSubmitAnswer(question, selectedChoiceId, responseText) {
  if (question.question_type === 'multiple_choice') {
    return selectedChoiceId !== null
  }
  if (question.question_type === 'numerical_response') {
    if (question.response_format === 'text') {
      return typeof responseText === 'string' && responseText.trim().length > 0
    }
    return isValidNumericalInput(responseText)
  }
  if (question.question_type === 'written_response') {
    return typeof responseText === 'string' && responseText.trim().length > 0
  }
  return false
}

export function buildGuestResults(quiz, guestAnswers) {
  const total = quiz.question_count ?? quiz.questions.length
  const graded = guestAnswers.filter((a) => a.auto_graded !== false)
  const correct = graded.filter((a) => a.is_correct).length
  const wrong = graded.filter((a) => a.is_correct === false).length
  const reviewRequired = guestAnswers.filter((a) => a.requires_review).length
  const gradedTotal = correct + wrong
  const byTopic = {}

  graded.forEach((answer) => {
    const entry = byTopic[answer.topic_id] || {
      topic_id: answer.topic_id,
      topic_name: answer.topic_name,
      correct: 0,
      total: 0,
    }
    entry.total += 1
    if (answer.is_correct) entry.correct += 1
    byTopic[answer.topic_id] = entry
  })

  const topics = Object.values(byTopic)
    .map((topic) => ({
      ...topic,
      accuracy: topic.total
        ? Math.round((topic.correct / topic.total) * 1000) / 10
        : 0,
    }))
    .sort((a, b) => a.accuracy - b.accuracy)

  const questionTypes = {
    multiple_choice: 0,
    numerical_response: 0,
    written_response: 0,
  }
  guestAnswers.forEach((answer) => {
    if (questionTypes[answer.question_type] !== undefined) {
      questionTypes[answer.question_type] += 1
    }
  })

  return {
    quiz_attempt_id: 0,
    course_id: quiz.course_id,
    total_questions: total,
    answered: guestAnswers.length,
    correct,
    wrong,
    review_required: reviewRequired,
    score_percent: gradedTotal
      ? Math.round((correct / gradedTotal) * 1000) / 10
      : 0,
    completed: true,
    question_types: questionTypes,
    topics,
  }
}
