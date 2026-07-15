function Avatar({ name }) {
  const initials = (name || '')
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0].toUpperCase())
    .join('')

  return (
    <div
      role="img"
      aria-label={name ? `Avatar for ${name}` : 'User avatar'}
      className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-blue-100 text-xs font-semibold text-blue-700"
    >
      {initials || '?'}
    </div>
  )
}

export default Avatar
