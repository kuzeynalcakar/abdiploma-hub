import Card from '../ui/Card'
import { CONFIDENCE_LABELS, masteryStyle } from '../../lib/mastery'

function TopicWeaknessCard({ topic }) {
  const style = masteryStyle(topic.mastery_level)

  return (
    <Card className={`border ${style.border}`}>
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0 flex-1">
          <h4 className="text-base font-semibold break-words text-gray-900">
            {topic.topic_name}
          </h4>
          <div className="mt-2 flex flex-wrap gap-2">
            <span
              className={[
                'rounded-full px-2.5 py-0.5 text-xs font-medium',
                style.bg,
                style.text,
              ].join(' ')}
            >
              {topic.mastery_label}
            </span>
            <span className="rounded-full bg-gray-100 px-2.5 py-0.5 text-xs font-medium text-gray-600">
              Confidence: {CONFIDENCE_LABELS[topic.confidence_level] || topic.confidence_level}
            </span>
          </div>
        </div>
        <div className="text-left sm:text-right">
          <p className="text-2xl font-bold text-gray-900">
            {topic.questions_attempted === 0 ? '—' : `${topic.accuracy}%`}
          </p>
          <p className="text-xs text-gray-500">Accuracy</p>
        </div>
      </div>

      <div className="mt-4">
        <div className="flex items-center justify-between text-xs text-gray-500">
          <span>
            {topic.questions_correct}/{topic.questions_attempted} correct
          </span>
          <span>{topic.questions_attempted} attempted</span>
        </div>
        <div className="mt-1.5 h-2 w-full rounded-full bg-gray-100">
          <div
            className={['h-2 rounded-full transition-[width]', style.bar].join(' ')}
            style={{
              width: `${topic.questions_attempted === 0 ? 0 : topic.accuracy}%`,
            }}
          />
        </div>
      </div>
    </Card>
  )
}

export default TopicWeaknessCard
