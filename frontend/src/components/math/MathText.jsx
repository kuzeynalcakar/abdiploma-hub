import katex from 'katex'
import 'katex/dist/katex.min.css'

// Matches $$...$$ (display math) first so its dollar signs are never
// consumed as two inline delimiters, then $...$ (inline math).
const MATH_PATTERN = /\$\$([\s\S]+?)\$\$|\$([^$\n]+?)\$/g

function renderMath(latex, displayMode) {
  return katex.renderToString(latex, {
    displayMode,
    throwOnError: false,
    strict: 'ignore',
  })
}

/**
 * Renders a string that mixes plain text with LaTeX math delimited by
 * $...$ (inline) or $$...$$ (display). Plain segments keep their line
 * breaks via whitespace-pre-line on the wrapper.
 *
 * KaTeX marks rendered math aria-hidden; each math segment gets an
 * accessible name from its LaTeX source so screen readers still hear it.
 */
function MathText({ text, className }) {
  if (typeof text !== 'string' || text.length === 0) {
    return null
  }

  const parts = []
  let lastIndex = 0
  let key = 0

  for (const match of text.matchAll(MATH_PATTERN)) {
    if (match.index > lastIndex) {
      parts.push(
        <span key={key++}>{text.slice(lastIndex, match.index)}</span>,
      )
    }
    const [, displayLatex, inlineLatex] = match
    const isDisplay = displayLatex !== undefined
    const latex = isDisplay ? displayLatex : inlineLatex
    parts.push(
      <span
        key={key++}
        role="math"
        aria-label={latex.trim()}
        className={
          isDisplay
            ? 'block max-w-full overflow-x-auto'
            : 'inline-block max-w-full overflow-x-auto align-baseline'
        }
      >
        <span
          aria-hidden="true"
          dangerouslySetInnerHTML={{
            __html: renderMath(latex, isDisplay),
          }}
        />
      </span>,
    )
    lastIndex = match.index + match[0].length
  }

  if (lastIndex < text.length) {
    parts.push(<span key={key++}>{text.slice(lastIndex)}</span>)
  }

  return (
    <span className={['whitespace-pre-line', className].filter(Boolean).join(' ')}>
      {parts}
    </span>
  )
}

export default MathText
