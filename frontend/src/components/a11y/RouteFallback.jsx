/**
 * Suspense fallback aligned with AppLayout geometry to limit CLS when
 * lazy routes resolve into the application shell.
 */
function RouteFallback() {
  return (
    <div className="min-h-screen overflow-x-clip bg-white" role="status" aria-live="polite">
      <div className="min-w-0 md:pl-60">
        <div className="h-14 border-b border-gray-200 bg-white" aria-hidden="true" />
        <div className="min-w-0 p-4 sm:p-6 md:p-8">
          <p className="text-sm text-gray-600">Loading…</p>
        </div>
      </div>
    </div>
  )
}

export default RouteFallback
