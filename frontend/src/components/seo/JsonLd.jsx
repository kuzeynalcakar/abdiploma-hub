import { useEffect } from 'react'
import { upsertJsonLd, removeJsonLd } from '../../lib/seo'

/**
 * Injects JSON-LD into document.head and removes it on unmount.
 * Renders nothing — keeps SEO structured data out of the visual DOM.
 */
function JsonLd({ id, data }) {
  useEffect(() => {
    upsertJsonLd(id, data)
    return () => removeJsonLd(id)
  }, [id, data])

  return null
}

export default JsonLd
