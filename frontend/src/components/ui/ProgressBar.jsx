function ProgressBar({ value, max = 100, tone = 'blue', label }) {
  const pct = max > 0 ? Math.min(100, Math.max(0, (value / max) * 100)) : 0
  const tones = {
    blue: 'bg-blue-600',
    green: 'bg-green-600',
    red: 'bg-red-500',
    amber: 'bg-amber-500',
  }
  return (
    <div
      role="progressbar"
      aria-valuenow={Math.round(pct)}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-label={label || `Progress ${Math.round(pct)} percent`}
      className="h-2 w-full overflow-hidden rounded-full bg-gray-100"
    >
      <div
        className={['h-full rounded-full transition-all', tones[tone] || tones.blue].join(
          ' ',
        )}
        style={{ width: `${pct}%` }}
      />
    </div>
  )
}

export default ProgressBar
