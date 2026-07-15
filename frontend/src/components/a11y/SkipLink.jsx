/**
 * Visually hidden until focused — lets keyboard users jump to main content.
 */
function SkipLink({ href = '#main-content', children = 'Skip to main content' }) {
  return (
    <a href={href} className="skip-link">
      {children}
    </a>
  )
}

export default SkipLink
