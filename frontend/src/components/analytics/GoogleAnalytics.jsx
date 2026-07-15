import { useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import { initGoogleAnalytics, trackPageView } from '../../lib/analytics'

/**
 * Loads GA4 when VITE_GA_MEASUREMENT_ID is set and tracks SPA page views.
 */
function GoogleAnalytics() {
  const location = useLocation()

  useEffect(() => {
    initGoogleAnalytics()
  }, [])

  useEffect(() => {
    trackPageView(`${location.pathname}${location.search}`)
  }, [location.pathname, location.search])

  return null
}

export default GoogleAnalytics
