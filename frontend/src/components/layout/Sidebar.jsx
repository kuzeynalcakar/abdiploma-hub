import { useCallback, useEffect } from 'react'
import { Link } from 'react-router-dom'
import Logo from '../brand/Logo'
import SidebarNavItem from './SidebarNavItem'
import { ADMIN_NAV_ITEM, GUEST_NAV_ITEMS, NAV_ITEMS } from '../../config/navigation'
import { useAuth } from '../../context/AuthContext'
import { useFocusTrap } from '../../hooks/useFocusTrap'
import { LINK_FOCUS } from '../../lib/focusStyles'

function Sidebar({ id, isOpen, onClose }) {
  const { user } = useAuth()
  const navItems = user
    ? user.is_admin
      ? [...NAV_ITEMS, ADMIN_NAV_ITEM]
      : NAV_ITEMS
    : GUEST_NAV_ITEMS

  // Mobile drawer is open; on md+ the sidebar is always visible (no trap).
  const trapActive = isOpen
  const handleEscape = useCallback(() => {
    if (isOpen) onClose?.()
  }, [isOpen, onClose])
  const panelRef = useFocusTrap(trapActive, handleEscape)

  useEffect(() => {
    if (!isOpen) return undefined
    const previousOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    return () => {
      document.body.style.overflow = previousOverflow
    }
  }, [isOpen])

  return (
    <>
      {isOpen && (
        <div
          onClick={onClose}
          aria-hidden="true"
          className="fixed inset-0 z-30 bg-gray-900/50 md:hidden"
        />
      )}

      <aside
        id={id}
        ref={panelRef}
        aria-label="Application sidebar"
        className={[
          'fixed inset-y-0 left-0 z-40 w-60 flex-col border-r border-gray-200 bg-gray-50',
          // Mobile: shown only when open. Desktop: always visible (`md:flex`).
          // `hidden` removes the drawer from the a11y tree when closed on mobile.
          isOpen ? 'flex' : 'hidden',
          'md:flex',
        ].join(' ')}
      >
        <div className="flex h-14 items-center border-b border-gray-200 px-4">
          <Link
            to="/dashboard"
            onClick={onClose}
            className={['min-w-0 rounded-md', LINK_FOCUS].join(' ')}
            aria-label="ABDiploma Hub"
          >
            <Logo size="sm" />
          </Link>
        </div>

        <nav aria-label="Main navigation" className="flex flex-1 flex-col gap-1 overflow-y-auto p-3 sm:p-4">
          {navItems.map((item) => (
            <SidebarNavItem
              key={item.path}
              label={item.label}
              path={item.path}
              icon={item.icon}
              primary={item.primary}
              subtitle={item.subtitle}
              onClick={onClose}
            />
          ))}

          {!user && (
            <div className="mt-auto border-t border-gray-200 pt-4">
              <div className="flex flex-col gap-1">
                <Link
                  to="/login"
                  onClick={onClose}
                  className={[
                    'rounded-md px-4 py-2.5 text-sm font-medium text-gray-600 hover:bg-gray-100',
                    LINK_FOCUS,
                  ].join(' ')}
                >
                  Log in
                </Link>
                <Link
                  to="/register"
                  onClick={onClose}
                  className={[
                    'rounded-md bg-blue-600 px-4 py-2.5 text-center text-sm font-medium text-white hover:bg-blue-700',
                    LINK_FOCUS,
                  ].join(' ')}
                >
                  Create Account
                </Link>
              </div>
            </div>
          )}
        </nav>
      </aside>
    </>
  )
}

export default Sidebar
