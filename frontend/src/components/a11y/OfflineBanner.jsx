import { useOnlineStatus } from '../../hooks/useOnlineStatus'

function OfflineBanner() {
  const online = useOnlineStatus()
  if (online) return null

  return (
    <div
      role="status"
      aria-live="polite"
      className="border-b border-amber-200 bg-amber-50 px-4 py-2 text-center text-sm text-amber-950"
    >
      You are offline. Some actions will not work until your connection returns.
    </div>
  )
}

export default OfflineBanner
