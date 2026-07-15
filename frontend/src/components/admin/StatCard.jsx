function StatCard({ label, value, note }) {
  const display =
    value === null || value === undefined
      ? '—'
      : typeof value === 'number' && !Number.isInteger(value)
        ? value.toLocaleString(undefined, { maximumFractionDigits: 1 })
        : typeof value === 'number'
          ? value.toLocaleString()
          : value

  return (
    <div className="min-w-0 rounded-lg border border-gray-200 bg-white p-3 shadow-sm sm:p-4">
      <p className="break-words text-xs font-medium text-gray-500">{label}</p>
      <p className="mt-1 break-words text-xl font-semibold text-gray-900 sm:text-2xl">
        {display}
      </p>
      {note && (
        <p className="mt-1 break-words text-xs text-gray-400">{note}</p>
      )}
    </div>
  )
}

export default StatCard
