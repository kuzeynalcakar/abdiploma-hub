import { Link, useNavigate } from 'react-router-dom'
import Avatar from './Avatar'
import { useAuth } from '../../context/AuthContext'
import { FOCUS_RING, LINK_FOCUS } from '../../lib/focusStyles'

function Header({ title, onMenuClick, isSidebarOpen, menuButtonRef, sidebarId }) {
  const navigate = useNavigate()
  const { user, logout } = useAuth()

  const handleLogout = async () => {
    await logout()
    navigate('/dashboard')
  }

  return (
    <header className="sticky top-0 z-30 flex h-14 min-w-0 items-center justify-between gap-2 border-b border-gray-200 bg-white px-3 sm:gap-3 sm:px-4">
      <div className="flex min-w-0 flex-1 items-center gap-2 sm:gap-3">
        <button
          ref={menuButtonRef}
          type="button"
          onClick={onMenuClick}
          aria-label="Open navigation menu"
          aria-expanded={isSidebarOpen}
          aria-controls={sidebarId}
          className={[
            'flex h-10 w-10 shrink-0 items-center justify-center rounded-md text-gray-600 hover:bg-gray-100 md:hidden',
            FOCUS_RING,
          ].join(' ')}
        >
          <span className="flex flex-col gap-1" aria-hidden="true">
            <span className="block h-0.5 w-5 rounded-full bg-current" />
            <span className="block h-0.5 w-5 rounded-full bg-current" />
            <span className="block h-0.5 w-5 rounded-full bg-current" />
          </span>
        </button>
        <h1 className="min-w-0 truncate text-base font-semibold text-gray-900 sm:text-xl">
          {title}
        </h1>
      </div>

      <div className="flex shrink-0 items-center gap-1.5 sm:gap-3">
        {user ? (
          <>
            <span className="hidden max-w-[10rem] truncate text-sm text-gray-600 sm:block">
              {user.name}
            </span>
            <Avatar name={user.name} />
            <button
              type="button"
              onClick={handleLogout}
              className={[
                'min-h-10 rounded-md px-2.5 py-1.5 text-sm font-medium text-gray-600 hover:bg-gray-100 hover:text-gray-900 sm:px-3',
                FOCUS_RING,
              ].join(' ')}
            >
              Log out
            </button>
          </>
        ) : (
          <>
            <span className="hidden rounded-full bg-gray-100 px-2.5 py-0.5 text-xs font-medium text-gray-700 sm:inline">
              Guest
            </span>
            <Link
              to="/login"
              className={[
                'inline-flex min-h-10 items-center rounded-md px-2.5 py-1.5 text-sm font-medium text-gray-600 hover:bg-gray-100 sm:px-3',
                LINK_FOCUS,
              ].join(' ')}
            >
              Log in
            </Link>
            <Link
              to="/register"
              className={[
                'inline-flex min-h-10 items-center rounded-md bg-blue-600 px-2.5 py-1.5 text-sm font-medium text-white hover:bg-blue-700 sm:px-3',
                LINK_FOCUS,
              ].join(' ')}
            >
              Sign up
            </Link>
          </>
        )}
      </div>
    </header>
  )
}

export default Header
