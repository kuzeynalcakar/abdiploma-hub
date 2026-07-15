/**
 * Warm the Vite/Rollup chunk for a lazy route after the browser is idle
 * or when the user shows intent (hover / focus on a nav link).
 */
const prefetched = new Set()

const LOADERS = {
  dashboard: () => import('../pages/Dashboard'),
  quiz: () => import('../pages/Quiz'),
  about: () => import('../pages/About'),
  'daily-practice': () => import('../pages/DailyPractice'),
  'weakness-map': () => import('../pages/WeaknessMap'),
  admin: () => import('../pages/Admin'),
}

export function prefetchRoute(name) {
  const loader = LOADERS[name]
  if (!loader || prefetched.has(name)) return
  prefetched.add(name)
  loader().catch(() => {
    prefetched.delete(name)
  })
}

export function prefetchLikelyRoutes(names) {
  const run = () => {
    names.forEach((name) => prefetchRoute(name))
  }
  if (typeof window !== 'undefined' && typeof window.requestIdleCallback === 'function') {
    window.requestIdleCallback(run, { timeout: 3000 })
  } else {
    setTimeout(run, 200)
  }
}
