function MetadataBadge({ value, className }) {
  if (!value) return null
  return (
    <span
      className={[
        'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium capitalize',
        className || 'bg-gray-100 text-gray-700',
      ].join(' ')}
    >
      {value}
    </span>
  )
}

export default MetadataBadge
