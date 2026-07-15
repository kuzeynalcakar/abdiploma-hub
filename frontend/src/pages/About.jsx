import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import Logo from '../components/brand/Logo'
import SkipLink from '../components/a11y/SkipLink'
import JsonLd from '../components/seo/JsonLd'
import { api } from '../lib/api'
import {
  usePageSeo,
  buildOrganizationJsonLd,
  buildCourseJsonLd,
} from '../lib/seo'
import { LINK_FOCUS } from '../lib/focusStyles'

const FLOW_STEPS = [
  {
    title: 'Practice questions',
    detail: 'Alberta curriculum-aligned multiple-choice, numerical, and written-response items',
  },
  { title: 'Check your answers', detail: 'Explanations after each question' },
  { title: 'Find weak topics', detail: 'Accuracy tracked by course topic on Weakness Map' },
  { title: 'Focus your review', detail: 'Daily Practice prioritizes what needs work' },
]

const ABOUT_DESCRIPTION =
  'Learn how ABDiploma Hub helps Alberta Grade 12 students prepare for diploma exams with free course practice, topic review, and Daily Practice.'

function About() {
  usePageSeo({
    title: 'About ABDiploma Hub | Free Alberta Diploma Exam Prep',
    description: ABOUT_DESCRIPTION,
    path: '/about',
    robots: 'index,follow',
  })
  const [stats, setStats] = useState(null)
  const orgLd = useMemo(() => buildOrganizationJsonLd(), [])
  const coursesLd = useMemo(
    () => [
      buildCourseJsonLd({
        name: 'Biology 30',
        description:
          'Alberta Biology 30 diploma exam practice with free curriculum-aligned questions on ABDiploma Hub.',
        urlPath: '/about',
      }),
      buildCourseJsonLd({
        name: 'Mathematics 30-1',
        description:
          'Alberta Mathematics 30-1 diploma exam practice with free curriculum-aligned questions on ABDiploma Hub.',
        urlPath: '/about',
      }),
    ],
    [],
  )

  useEffect(() => {
    api('/stats/platform')
      .then(setStats)
      .catch(() => setStats(null))
  }, [])

  return (
    <div className="min-h-screen overflow-x-clip bg-white">
      <JsonLd id="ld-about-organization" data={orgLd} />
      <JsonLd id="ld-about-course-bio" data={coursesLd[0]} />
      <JsonLd id="ld-about-course-math" data={coursesLd[1]} />
      <SkipLink />
      <header className="border-b border-gray-200">
        <div className="mx-auto flex h-14 max-w-5xl items-center justify-between gap-2 px-4 sm:h-16 sm:px-6">
          <Link
            to="/dashboard"
            className={['min-w-0 shrink rounded-md', LINK_FOCUS].join(' ')}
          >
            <Logo />
          </Link>
          <nav aria-label="Primary" className="flex shrink-0 items-center gap-1 sm:gap-3">
            <Link
              to="/dashboard"
              className={[
                'hidden min-h-10 items-center rounded-md px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 sm:inline-flex',
                LINK_FOCUS,
              ].join(' ')}
            >
              Practice
            </Link>
            <Link
              to="/login"
              className={[
                'inline-flex min-h-10 items-center rounded-md px-2.5 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 sm:px-3',
                LINK_FOCUS,
              ].join(' ')}
            >
              Log in
            </Link>
            <Link
              to="/register"
              className={[
                'inline-flex min-h-10 items-center rounded-md bg-blue-600 px-3 py-2 text-sm font-medium text-white hover:bg-blue-700 sm:px-4',
                LINK_FOCUS,
              ].join(' ')}
            >
              <span className="sm:hidden">Sign up</span>
              <span className="hidden sm:inline">Create free account</span>
            </Link>
          </nav>
        </div>
      </header>

      <main id="main-content" tabIndex={-1} className="mx-auto max-w-5xl px-4 py-12 sm:px-6 sm:py-16">
        <section className="max-w-3xl">
          <p className="text-sm font-semibold uppercase tracking-wide text-blue-600">
            Built by an Alberta student, for Alberta students
          </p>
          <h1 className="mt-3 text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
            Free Alberta Diploma Exam preparation
          </h1>
          <p className="mt-4 text-base leading-7 text-gray-600">
            ABDiploma Hub is a free practice site for Alberta diploma courses. It was
            started by a student who wanted clearer practice for Biology 30, Math 30-1,
            and other Alberta courses — with explanations, topic review, and a simple
            Daily Practice habit.
          </p>
        </section>

        <section className="mt-12 grid gap-8 lg:grid-cols-2">
          <div className="rounded-xl border border-gray-200 bg-gray-50 p-6">
            <h2 className="text-lg font-semibold text-gray-900">The problem</h2>
            <p className="mt-3 text-sm leading-7 text-gray-600">
              Alberta diploma prep can be expensive or scattered. Many students know
              their overall score but not which course topics they miss most, so study
              time stays unfocused.
            </p>
          </div>
          <div className="rounded-xl border border-blue-200 bg-blue-50 p-6">
            <h2 className="text-lg font-semibold text-gray-900">What this site does</h2>
            <p className="mt-3 text-sm leading-7 text-gray-700">
              ABDiploma Hub offers free, curriculum-aligned practice. Weakness Map shows
              accuracy by topic, and Daily Practice focuses on the areas that need more
              work.
            </p>
          </div>
        </section>

        <section className="mt-12">
          <h2 className="text-xl font-semibold text-gray-900">How ABDiploma Hub works</h2>
          <ol className="mt-6 grid list-none grid-cols-1 gap-3 p-0 sm:grid-cols-2 lg:grid-cols-4 lg:gap-2">
            {FLOW_STEPS.map((step, index) => (
              <li key={step.title} className="flex min-w-0 flex-col items-center text-center">
                <div className="w-full rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
                  <h3 className="text-sm font-semibold break-words text-gray-900">
                    {step.title}
                  </h3>
                  <p className="mt-1 text-xs leading-5 text-gray-600">{step.detail}</p>
                </div>
                {index < FLOW_STEPS.length - 1 && (
                  <span
                    className="my-1 text-gray-400 lg:hidden"
                    aria-hidden="true"
                  >
                    ↓
                  </span>
                )}
              </li>
            ))}
          </ol>
        </section>

        <section className="mt-12 rounded-xl border border-slate-200 bg-slate-50 p-6 sm:p-8">
          <h2 className="text-xl font-semibold text-gray-900">Student practice so far</h2>
          <p className="mt-2 text-sm text-gray-600">
            Totals from real practice on the site.
          </p>
          {stats ? (
            <dl className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-3">
              <div className="rounded-lg bg-white p-4 shadow-sm">
                <dd className="text-3xl font-bold text-gray-900">{stats.students_helped}</dd>
                <dt className="mt-1 text-sm text-gray-500">Students who practiced</dt>
              </div>
              <div className="rounded-lg bg-white p-4 shadow-sm">
                <dd className="text-3xl font-bold text-gray-900">
                  {stats.questions_completed.toLocaleString()}
                </dd>
                <dt className="mt-1 text-sm text-gray-500">Questions completed</dt>
              </div>
              <div className="rounded-lg bg-white p-4 shadow-sm">
                <dd className="text-3xl font-bold text-gray-900">{stats.practice_sessions}</dd>
                <dt className="mt-1 text-sm text-gray-500">Practice sessions</dt>
              </div>
            </dl>
          ) : (
            <p className="mt-4 text-sm text-gray-500">
              Practice totals will show here once students start answering questions.
            </p>
          )}
        </section>

        <section className="mt-12">
          <h2 className="text-xl font-semibold text-gray-900">Courses available now</h2>
          <div className="mt-4 flex flex-wrap gap-3">
            {[
              'Biology 30',
              'Chemistry 30',
              'Physics 30',
              'Science 30',
              'Science 10',
              'Mathematics 20-1',
              'Mathematics 30-1',
              'Mathematics 30-2',
              'Social Studies 30-1',
            ].map((course) => (
              <span
                key={course}
                className="rounded-full border border-blue-200 bg-blue-50 px-4 py-1.5 text-sm font-medium text-blue-800"
              >
                {course}
              </span>
            ))}
          </div>
        </section>

        <section className="mt-12 rounded-xl border border-gray-200 bg-white p-6 text-center sm:p-8">
          <h2 className="text-xl font-semibold text-gray-900">Start practicing now</h2>
          <p className="mx-auto mt-2 max-w-lg text-sm text-gray-600">
            No account needed to try questions. Create a free account to save progress,
            open Weakness Map, and use Daily Practice.
          </p>
          <div className="mt-6 flex flex-col items-center justify-center gap-3 sm:flex-row">
            <Link
              to="/dashboard"
              className={[
                'w-full rounded-lg bg-blue-600 px-8 py-3 text-center text-sm font-semibold text-white hover:bg-blue-700 sm:w-auto',
                LINK_FOCUS,
              ].join(' ')}
            >
              Go to Dashboard
            </Link>
            <Link
              to="/register"
              className={[
                'w-full rounded-lg border border-gray-300 bg-white px-8 py-3 text-center text-sm font-semibold text-gray-900 hover:bg-gray-50 sm:w-auto',
                LINK_FOCUS,
              ].join(' ')}
            >
              Create free account
            </Link>
          </div>
        </section>
      </main>

      <footer className="border-t border-gray-200">
        <div className="mx-auto max-w-5xl px-4 py-8 text-center text-sm text-gray-600 sm:px-6">
          ABDiploma Hub — Free Alberta Diploma Exam Preparation
        </div>
      </footer>
    </div>
  )
}

export default About
