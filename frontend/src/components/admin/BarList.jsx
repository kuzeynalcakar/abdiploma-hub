function BarList({ items, valueKey = 'value', labelKey = 'label', maxBars = 10 }) {
  const rows = (items || []).slice(0, maxBars)
  const max = Math.max(1, ...rows.map((row) => Number(row[valueKey]) || 0))

  if (rows.length === 0) {
    return <p className="text-sm text-gray-600">No data yet.</p>
  }

  return (
    <ul className="flex flex-col gap-3">
      {rows.map((row) => {
        const value = Number(row[valueKey]) || 0
        const pct = Math.round((value / max) * 100)
        const label = String(row[labelKey])
        return (
          <li key={`${label}-${value}`}>
            <div className="mb-1 flex items-start justify-between gap-2 text-sm">
              <span className="min-w-0 break-words text-gray-900">{label}</span>
              <span className="shrink-0 font-medium text-gray-700">
                {typeof value === 'number' && !Number.isInteger(value)
                  ? value.toFixed(1)
                  : value}
                {row.suffix || ''}
              </span>
            </div>
            <div
              role="progressbar"
              aria-valuenow={pct}
              aria-valuemin={0}
              aria-valuemax={100}
              aria-label={`${label}: ${value}${row.suffix || ''}`}
              className="h-2 overflow-hidden rounded-full bg-gray-100"
            >
              <div
                className="h-full rounded-full bg-blue-600"
                style={{ width: `${pct}%` }}
              />
            </div>
          </li>
        )
      })}
    </ul>
  )
}

export default BarList
