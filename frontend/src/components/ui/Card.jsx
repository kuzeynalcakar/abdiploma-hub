function Card({ children, className }) {
  return (
    <div
      className={[
        'min-w-0 rounded-lg border border-gray-200 bg-white p-4 shadow-sm sm:p-6',
        className,
      ]
        .filter(Boolean)
        .join(' ')}
    >
      {children}
    </div>
  )
}

export default Card
