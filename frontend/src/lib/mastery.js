export const MASTERY_CONFIG = {
  excellent: {
    label: 'Excellent',
    color: 'green',
    bg: 'bg-green-100',
    text: 'text-green-800',
    bar: 'bg-green-500',
    border: 'border-green-200',
  },
  strong: {
    label: 'Strong',
    color: 'green',
    bg: 'bg-green-50',
    text: 'text-green-700',
    bar: 'bg-green-400',
    border: 'border-green-200',
  },
  improving: {
    label: 'Improving',
    color: 'yellow',
    bg: 'bg-yellow-100',
    text: 'text-yellow-800',
    bar: 'bg-yellow-500',
    border: 'border-yellow-200',
  },
  weak: {
    label: 'Weak',
    color: 'orange',
    bg: 'bg-orange-100',
    text: 'text-orange-800',
    bar: 'bg-orange-500',
    border: 'border-orange-200',
  },
  critical: {
    label: 'Critical',
    color: 'red',
    bg: 'bg-red-100',
    text: 'text-red-800',
    bar: 'bg-red-500',
    border: 'border-red-200',
  },
  not_attempted: {
    label: 'Not Attempted',
    color: 'gray',
    bg: 'bg-gray-100',
    text: 'text-gray-600',
    bar: 'bg-gray-300',
    border: 'border-gray-200',
  },
}

export const CONFIDENCE_LABELS = {
  not_attempted: 'N/A',
  low: 'Low',
  medium: 'Medium',
  high: 'High',
}

export function masteryStyle(level) {
  return MASTERY_CONFIG[level] || MASTERY_CONFIG.not_attempted
}
