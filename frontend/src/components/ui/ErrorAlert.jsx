import Button from './Button'

/**
 * Consistent failure banner with optional Retry — matches existing red alert styling.
 */
function ErrorAlert({ message, onRetry, retryLabel = 'Try again', className = '' }) {
  if (!message) return null

  return (
    <div
      role="alert"
      className={[
        'rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800',
        className,
      ]
        .filter(Boolean)
        .join(' ')}
    >
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <p className="min-w-0 flex-1">{message}</p>
        {onRetry && (
          <Button
            type="button"
            variant="secondary"
            className="shrink-0 border-red-200 bg-white text-red-900 hover:bg-red-50"
            onClick={onRetry}
          >
            {retryLabel}
          </Button>
        )}
      </div>
    </div>
  )
}

export default ErrorAlert
