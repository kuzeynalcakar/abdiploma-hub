import { Component } from 'react'
import Button from '../ui/Button'
import { reportError } from '../../lib/errors'
import { LINK_FOCUS } from '../../lib/focusStyles'

function GlobalFallback({ onReload }) {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gray-50 px-6 text-center">
      <main id="main-content" tabIndex={-1} className="max-w-md">
        <p className="text-sm font-medium text-blue-700">Something went wrong</p>
        <h1 className="mt-2 text-2xl font-semibold text-gray-900">
          ABDiploma Hub hit an unexpected error
        </h1>
        <p className="mt-3 text-sm text-gray-600">
          Your progress is safe. Reload the page to continue practicing.
        </p>
        <div className="mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row">
          <Button type="button" onClick={onReload}>
            Reload page
          </Button>
          <a
            href="/dashboard"
            className={[
              'inline-flex min-h-10 items-center justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-900 hover:bg-gray-50',
              LINK_FOCUS,
            ].join(' ')}
          >
            Go to dashboard
          </a>
        </div>
      </main>
    </div>
  )
}

/**
 * Catches render errors so users never see a blank white screen.
 */
class ErrorBoundary extends Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError() {
    return { hasError: true }
  }

  componentDidCatch(error, info) {
    reportError(error, {
      source: 'ErrorBoundary',
      componentStack: String(info?.componentStack || '').slice(0, 400),
    })
  }

  handleReload = () => {
    this.setState({ hasError: false })
    window.location.reload()
  }

  render() {
    if (this.state.hasError) {
      return <GlobalFallback onReload={this.handleReload} />
    }
    return this.props.children
  }
}

export default ErrorBoundary
