import { lazy, Suspense } from 'react'
import { BrowserRouter, Route, Routes } from 'react-router-dom'
import AuthGate from './components/auth/AuthGate'
import AdminRoute from './components/auth/AdminRoute'
import GoogleAnalytics from './components/analytics/GoogleAnalytics'
import RouteFallback from './components/a11y/RouteFallback'
import ErrorBoundary from './components/a11y/ErrorBoundary'
import OfflineBanner from './components/a11y/OfflineBanner'
import { AuthProvider } from './context/AuthContext'

// Eager: first-paint / auth entry paths only.
import Home from './pages/Home'
import Landing from './pages/Landing'
import Login from './pages/Login'
import Register from './pages/Register'
import NotFound from './pages/NotFound'

// Lazy: heavy or secondary routes — kept out of the initial bundle.
const About = lazy(() => import('./pages/About'))
const Dashboard = lazy(() => import('./pages/Dashboard'))
const DailyPractice = lazy(() => import('./pages/DailyPractice'))
const WeaknessMap = lazy(() => import('./pages/WeaknessMap'))
const Quiz = lazy(() => import('./pages/Quiz'))
const Admin = lazy(() => import('./pages/Admin'))

function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <BrowserRouter>
          <OfflineBanner />
          <GoogleAnalytics />
          <Suspense fallback={<RouteFallback />}>
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/about" element={<About />} />
              <Route path="/welcome" element={<Landing />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/quiz" element={<Quiz />} />
              <Route
                path="/daily-practice"
                element={
                  <AuthGate
                    pageTitle="Daily Practice"
                    title="Daily Practice"
                    description="Create a free account to save your progress and use Daily Practice — short sessions based on your previous results, not random questions."
                  >
                    <DailyPractice />
                  </AuthGate>
                }
              />
              <Route
                path="/weakness-map"
                element={
                  <AuthGate
                    pageTitle="Weakness Map"
                    title="Weakness Map"
                    description="Create a free account to save quiz results and see where you are strong, which topics need review, and how your accuracy changes over time."
                  >
                    <WeaknessMap />
                  </AuthGate>
                }
              />
              <Route
                path="/admin"
                element={
                  <AdminRoute>
                    <Admin />
                  </AdminRoute>
                }
              />
              <Route path="*" element={<NotFound />} />
            </Routes>
          </Suspense>
        </BrowserRouter>
      </AuthProvider>
    </ErrorBoundary>
  )
}

export default App
