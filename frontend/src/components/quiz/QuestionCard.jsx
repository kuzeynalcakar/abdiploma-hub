import Card from '../ui/Card'
import MathText from '../math/MathText'

function QuestionCard({ questionText, topicLabel, children }) {
  return (
    <Card>
      {topicLabel && (
        <p className="text-xs font-medium text-gray-400">{topicLabel}</p>
      )}
      <h2 className="mt-2 max-w-full overflow-x-auto text-lg font-semibold break-words text-gray-900 sm:text-xl">
        <MathText text={questionText} />
      </h2>
      <div className="mt-6">{children}</div>
    </Card>
  )
}

export default QuestionCard
