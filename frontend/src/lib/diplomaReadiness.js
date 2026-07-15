/**
 * Diploma exam readiness overview from existing Weakness Map API data.
 * Does not invent readiness percentages or pass predictions.
 */

const MIN_QUESTIONS_FOR_OVERVIEW = 8
const MIN_TOPICS_FOR_OVERVIEW = 2

/**
 * @param {object | null} weaknessMap
 * @returns {{
 *   courseName: string,
 *   hasPracticeData: boolean,
 *   sufficientForOverview: boolean,
 *   overallAccuracy: number | null,
 *   questionsCompleted: number,
 *   topicsPracticed: number,
 *   topicsTotal: number,
 *   coverageLabel: string,
 *   preparationLabel: string,
 *   strengthTopics: { topic_id: number, topic_name: string, accuracy: number }[],
 *   reviewTopics: { topic_id: number, topic_name: string, accuracy: number }[],
 * }}
 */
export function buildDiplomaReadiness(weaknessMap) {
  const courseName = weaknessMap?.course_name || 'This course'
  const topics = Array.isArray(weaknessMap?.topics) ? weaknessMap.topics : []
  const strong = Array.isArray(weaknessMap?.strong_topics)
    ? weaknessMap.strong_topics
    : []
  const review = Array.isArray(weaknessMap?.needs_practice)
    ? weaknessMap.needs_practice
    : []

  const questionsCompleted = topics.reduce(
    (sum, t) => sum + (Number(t.questions_attempted) || 0),
    0,
  )
  const topicsPracticed = topics.filter(
    (t) => (Number(t.questions_attempted) || 0) > 0,
  ).length
  const topicsTotal = topics.length
  const hasPracticeData = Boolean(weaknessMap?.has_attempted_topics) && questionsCompleted > 0

  const sufficientForOverview =
    hasPracticeData &&
    questionsCompleted >= MIN_QUESTIONS_FOR_OVERVIEW &&
    topicsPracticed >= MIN_TOPICS_FOR_OVERVIEW

  const coverageLabel =
    topicsTotal > 0
      ? `${topicsPracticed} of ${topicsTotal} topics practiced`
      : `${topicsPracticed} topic${topicsPracticed === 1 ? '' : 's'} practiced`

  const accuracy =
    hasPracticeData && weaknessMap?.overall_accuracy != null
      ? Number(weaknessMap.overall_accuracy)
      : null

  let preparationLabel = 'Not enough practice recorded yet'
  if (sufficientForOverview && accuracy != null) {
    const coverageRatio = topicsTotal > 0 ? topicsPracticed / topicsTotal : 0
    if (coverageRatio >= 0.6 && accuracy >= 70) {
      preparationLabel = 'Broader practice recorded across multiple topics'
    } else if (coverageRatio >= 0.35 || questionsCompleted >= 20) {
      preparationLabel = 'Preparation is underway — keep reviewing weak topics'
    } else {
      preparationLabel = 'Early preparation — expand practice across more topics'
    }
  } else if (hasPracticeData) {
    preparationLabel = 'Early practice recorded — more sessions will refine this overview'
  }

  return {
    courseName,
    hasPracticeData,
    sufficientForOverview,
    overallAccuracy: accuracy,
    questionsCompleted,
    topicsPracticed,
    topicsTotal,
    coverageLabel,
    preparationLabel,
    strengthTopics: strong.map((t) => ({
      topic_id: t.topic_id,
      topic_name: t.topic_name,
      accuracy: t.accuracy,
    })),
    reviewTopics: review.map((t) => ({
      topic_id: t.topic_id,
      topic_name: t.topic_name,
      accuracy: t.accuracy,
    })),
  }
}
