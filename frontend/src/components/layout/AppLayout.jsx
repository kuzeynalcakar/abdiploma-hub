import { useCallback, useEffect, useId, useRef, useState } from 'react'
import Sidebar from './Sidebar'
import Header from './Header'
import SkipLink from '../a11y/SkipLink'
import { useAppPageSeo } from '../../lib/pageTitle'

function AppLayout({ pageTitle, documentTitle, children }) {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)
  const menuButtonRef = useRef(null)
  const sidebarId = useId()
  useAppPageSeo(pageTitle, documentTitle)

  const closeSidebar = useCallback(() => {
    setIsSidebarOpen(false)
  }, [])

  const openSidebar = useCallback(() => {
    setIsSidebarOpen(true)
  }, [])

  useEffect(() => {
    if (isSidebarOpen) return undefined
    // Return focus to the menu button after closing (mobile).
    if (menuButtonRef.current && document.activeElement !== menuButtonRef.current) {
      const wasInSidebar = document
        .getElementById(sidebarId)
        ?.contains(document.activeElement)
      if (wasInSidebar) {
        menuButtonRef.current.focus()
      }
    }
    return undefined
  }, [isSidebarOpen, sidebarId])

  return (
    <div className="min-h-screen overflow-x-clip bg-white">
      <SkipLink />
      <Sidebar
        id={sidebarId}
        isOpen={isSidebarOpen}
        onClose={closeSidebar}
      />

      <div className="min-w-0 md:pl-60">
        <Header
          title={pageTitle}
          onMenuClick={openSidebar}
          isSidebarOpen={isSidebarOpen}
          menuButtonRef={menuButtonRef}
          sidebarId={sidebarId}
        />
        <main id="main-content" tabIndex={-1} className="min-w-0 p-4 sm:p-6 md:p-8">
          {children}
        </main>
      </div>
    </div>
  )
}

export default AppLayout
