import { NavLink } from 'react-router-dom'
import { LINK_FOCUS } from '../../lib/focusStyles'
import { prefetchRoute } from '../../lib/prefetchRoute'

const PATH_TO_PREFETCH = {
  '/dashboard': 'dashboard',
  '/quiz': 'quiz',
  '/about': 'about',
  '/daily-practice': 'daily-practice',
  '/weakness-map': 'weakness-map',
  '/admin': 'admin',
}

function warmRoute(path) {
  const name = PATH_TO_PREFETCH[path]
  if (name) prefetchRoute(name)
}

function SidebarNavItem({ label, path, icon, primary, subtitle, onClick }) {
  if (primary) {
    return (
      <NavLink
        to={path}
        onClick={onClick}
        onFocus={() => warmRoute(path)}
        onPointerEnter={() => warmRoute(path)}
        className={({ isActive }) =>
          [
            'mb-3 block rounded-xl border-2 px-4 py-5 shadow-md transition-all',
            LINK_FOCUS,
            isActive
              ? 'border-orange-400 bg-gradient-to-br from-orange-500 to-orange-600 text-white shadow-md'
              : 'border-orange-300 bg-gradient-to-br from-orange-100 to-amber-100 text-orange-950 hover:border-orange-400 hover:shadow-md',
          ].join(' ')
        }
      >
        <span className="text-base font-bold leading-tight sm:text-lg">
          {icon && (
            <span className="mr-1" aria-hidden="true">
              {icon}{' '}
            </span>
          )}
          {label}
        </span>
        {subtitle && (
          <span className="mt-1.5 block text-xs font-medium leading-snug opacity-90">
            {subtitle}
          </span>
        )}
      </NavLink>
    )
  }

  return (
    <NavLink
      to={path}
      onClick={onClick}
      onFocus={() => warmRoute(path)}
      onPointerEnter={() => warmRoute(path)}
      className={({ isActive }) =>
        [
          'rounded-md px-4 py-2.5 text-sm font-medium transition-colors',
          LINK_FOCUS,
          isActive
            ? 'bg-blue-50 text-blue-700'
            : 'text-gray-600 hover:bg-gray-100',
        ].join(' ')
      }
    >
      {icon && (
        <span className="mr-1" aria-hidden="true">
          {icon}{' '}
        </span>
      )}
      {label}
    </NavLink>
  )
}

export default SidebarNavItem
