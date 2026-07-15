function Logo({ size = 'md', showText = true, className = '' }) {
  const sizes = {
    sm: { icon: 24, text: 'text-sm' },
    md: { icon: 32, text: 'text-base sm:text-lg' },
    lg: { icon: 40, text: 'text-lg sm:text-xl' },
  }
  const { icon, text } = sizes[size] || sizes.md

  return (
    <span className={['inline-flex items-center gap-2.5', className].join(' ')}>
      <svg
        width={icon}
        height={icon}
        viewBox="0 0 40 40"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        aria-hidden="true"
        className="shrink-0"
      >
        <rect width="40" height="40" rx="10" fill="#2563EB" />
        <path
          d="M8 28 L14 18 L20 24 L26 14 L32 28"
          stroke="white"
          strokeWidth="2.5"
          strokeLinecap="round"
          strokeLinejoin="round"
          fill="none"
        />
        <circle cx="32" cy="12" r="4" fill="#F97316" />
        <path
          d="M30 12 L32 14 L34 10"
          stroke="white"
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
      {showText && (
        <span className={['font-bold tracking-tight text-gray-900', text].join(' ')}>
          ABDiploma Hub
        </span>
      )}
    </span>
  )
}

export default Logo
