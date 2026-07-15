import { useEffect, useMemo } from 'react'
import { Link, Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import {
  usePageSeo,
  DEFAULT_DESCRIPTION,
  DEFAULT_TITLE,
  buildOrganizationJsonLd,
  buildWebSiteJsonLd,
  buildCourseJsonLd,
} from '../lib/seo'
import JsonLd from '../components/seo/JsonLd'
import SkipLink from '../components/a11y/SkipLink'
import { LINK_FOCUS } from '../lib/focusStyles'
import { prefetchLikelyRoutes, prefetchRoute } from '../lib/prefetchRoute'

// Mirrored from /api/v1/courses production banks (active + question_count > 0).
const AVAILABLE_COURSES = [
  { code: 'BIO30', name: 'Biology 30', area: 'Sciences', blurb: 'Genetics, systems, and cell processes' },
  { code: 'CHEM30', name: 'Chemistry 30', area: 'Sciences', blurb: 'Acids, bases, electrochemistry, and equilibrium' },
  { code: 'PHYS30', name: 'Physics 30', area: 'Sciences', blurb: 'Momentum, fields, and modern physics topics' },
  { code: 'SCI30', name: 'Science 30', area: 'Sciences', blurb: 'Biology, chemistry, and physics in one course' },
  { code: 'SCI10', name: 'Science 10', area: 'Sciences', blurb: 'Foundations across science disciplines' },
  { code: 'MATH20-1', name: 'Mathematics 20-1', area: 'Mathematics', blurb: 'Quadratics, sequences, and rational expressions' },
  { code: 'MATH30-1', name: 'Mathematics 30-1', area: 'Mathematics', blurb: 'Functions, trig, and diploma-style problem solving' },
  { code: 'MATH30-2', name: 'Mathematics 30-2', area: 'Mathematics', blurb: 'Probability, relations, and applied algebra' },
  { code: 'SOC30-1', name: 'Social Studies 30-1', area: 'Social Studies', blurb: 'Ideology, liberalism, and citizenship' },
]

const HOW_IT_WORKS = [
  {
    step: '01',
    title: 'Practice diploma-style questions',
    description:
      'Work through multiple-choice, numerical-response, and other exam-style items aligned to Alberta courses.',
  },
  {
    step: '02',
    title: 'See where marks are slipping',
    description:
      'Check accuracy by topic so you know where you are solid and where more review is needed.',
  },
  {
    step: '03',
    title: 'Focus on weaker topics',
    description:
      'Use Weakness Map and Daily Practice to prioritize the areas that need work in your next study block.',
  },
]

const ALBERTA_POINTS = [
  {
    title: 'Alberta curriculum alignment',
    description:
      'Questions are organized by Alberta course topics and units so practice matches what is taught in class—not a generic worksheet set.',
  },
  {
    title: 'Diploma exam preparation focus',
    description:
      'Practice includes diploma-style formats—multiple choice, numerical response, and explanations that show the reasoning behind each answer.',
  },
  {
    title: 'Free access',
    description:
      'Start as a guest or create a free account. Core practice tools do not require a paid subscription.',
  },
]

const areaAccent = {
  Mathematics: 'border-l-blue-600',
  Sciences: 'border-l-teal-600',
  'Social Studies': 'border-l-amber-600',
}

function Landing() {
  const { user, isLoading } = useAuth()
  usePageSeo({
    title: DEFAULT_TITLE,
    description: DEFAULT_DESCRIPTION,
    path: '/welcome',
    robots: 'index,follow',
  })

  const orgLd = useMemo(() => buildOrganizationJsonLd(), [])
  const siteLd = useMemo(() => buildWebSiteJsonLd(), [])
  const bioLd = useMemo(
    () =>
      buildCourseJsonLd({
        name: 'Biology 30 Alberta Diploma Practice',
        description:
          'Free Biology 30 diploma exam practice on ABDiploma Hub with curriculum-aligned questions and instant feedback.',
        urlPath: '/welcome',
      }),
    [],
  )
  const mathLd = useMemo(
    () =>
      buildCourseJsonLd({
        name: 'Mathematics 30-1 Alberta Diploma Practice',
        description:
          'Free Mathematics 30-1 diploma exam practice on ABDiploma Hub with curriculum-aligned questions and instant feedback.',
        urlPath: '/welcome',
      }),
    [],
  )

  useEffect(() => {
    prefetchLikelyRoutes(['dashboard', 'quiz'])
  }, [])

  if (!isLoading && user) {
    return <Navigate to="/dashboard" replace />
  }

  return (
    <div className="min-h-screen overflow-x-clip bg-[#f7f8fa] text-slate-900">
      <JsonLd id="ld-organization" data={orgLd} />
      <JsonLd id="ld-website" data={siteLd} />
      <JsonLd id="ld-course-bio30" data={bioLd} />
      <JsonLd id="ld-course-math301" data={mathLd} />
      <SkipLink />

      <header className="sticky top-0 z-20 border-b border-slate-200/90 bg-white/95 backdrop-blur-[6px]">
        <div className="mx-auto flex h-14 max-w-6xl items-center justify-between gap-3 px-4 sm:h-16 sm:px-6 lg:px-8">
          <span className="min-w-0 truncate text-lg font-semibold tracking-tight text-slate-900 sm:text-xl">
            ABDiploma Hub
          </span>
          <nav aria-label="Account" className="flex shrink-0 items-center gap-1.5 sm:gap-2">
            <Link
              to="/login"
              className={[
                'inline-flex min-h-10 items-center rounded-lg px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100 sm:px-4',
                LINK_FOCUS,
              ].join(' ')}
            >
              Log in
            </Link>
            <Link
              to="/register"
              className={[
                'inline-flex min-h-10 items-center rounded-lg bg-[#1865f2] px-3 py-2 text-sm font-semibold text-white hover:bg-[#0f4ec9] sm:px-4',
                LINK_FOCUS,
              ].join(' ')}
            >
              <span className="sm:hidden">Sign up</span>
              <span className="hidden sm:inline">Create free account</span>
            </Link>
          </nav>
        </div>
      </header>

      <main id="main-content" tabIndex={-1}>
        {/* Hero */}
        <section
          className="relative overflow-hidden border-b border-slate-200 bg-white"
          aria-labelledby="landing-heading"
        >
          <div
            className="pointer-events-none absolute inset-y-0 right-0 hidden w-1/2 bg-[radial-gradient(ellipse_at_top_right,_#e8eefc_0%,_transparent_55%)] lg:block"
            aria-hidden="true"
          />
          <div className="relative mx-auto grid max-w-6xl gap-10 px-4 pb-16 pt-12 sm:px-6 sm:pb-20 sm:pt-16 lg:grid-cols-[minmax(0,1.15fr)_minmax(0,0.85fr)] lg:items-center lg:gap-14 lg:px-8 lg:pb-24 lg:pt-20">
            <div>
              <p className="text-sm font-semibold text-[#1865f2]">ABDiploma Hub</p>
              <h1
                id="landing-heading"
                className="mt-3 max-w-xl text-[1.85rem] font-bold leading-[1.15] tracking-tight text-slate-900 sm:text-4xl lg:text-[2.75rem] lg:leading-[1.12]"
              >
                Free Alberta Diploma Exam preparation
              </h1>
              <p className="mt-5 max-w-lg text-base leading-relaxed text-slate-600 sm:text-lg">
                Practice Alberta curriculum questions, see which topics need review,
                and get a clear explanation after each answer.
              </p>
              <div className="mt-8 flex w-full max-w-md flex-col gap-3 sm:max-w-none sm:flex-row sm:items-center">
                <Link
                  to="/dashboard"
                  onFocus={() => prefetchRoute('dashboard')}
                  onPointerEnter={() => prefetchRoute('dashboard')}
                  className={[
                    'inline-flex min-h-12 w-full items-center justify-center rounded-lg bg-[#1865f2] px-7 py-3 text-center text-base font-semibold text-white shadow-sm hover:bg-[#0f4ec9] sm:w-auto',
                    LINK_FOCUS,
                  ].join(' ')}
                >
                  Start practicing free
                </Link>
                <Link
                  to="/register"
                  className={[
                    'inline-flex min-h-12 w-full items-center justify-center rounded-lg border border-slate-300 bg-white px-7 py-3 text-center text-base font-semibold text-slate-800 hover:border-slate-400 hover:bg-slate-50 sm:w-auto',
                    LINK_FOCUS,
                  ].join(' ')}
                >
                  Create free account
                </Link>
              </div>
              <p className="mt-5 text-sm text-slate-500">
                For Alberta high school students. Guest practice available — no payment required.
              </p>
              <p className="mt-3">
                <Link
                  to="/login"
                  className={['text-sm font-medium text-slate-600 underline-offset-2 hover:text-slate-900 hover:underline', LINK_FOCUS].join(' ')}
                >
                  Already have an account? Log in
                </Link>
              </p>
            </div>

            <aside
              className="rounded-2xl border border-slate-200 bg-[#f7f8fa] p-5 sm:p-6"
              aria-label="What you get"
            >
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                On the platform
              </p>
              <ul className="mt-4 space-y-4">
                {[
                  { title: 'Course practice banks', body: 'Diploma-style questions by Alberta course and topic' },
                  { title: 'Explanations after each answer', body: 'See the reasoning and common mistakes' },
                  { title: 'Weakness Map', body: 'Accuracy by topic so you know what to review' },
                  { title: 'Daily Practice', body: 'Short sessions focused on weaker topics' },
                ].map((item) => (
                  <li key={item.title} className="flex gap-3">
                    <span
                      className="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-[#1865f2]"
                      aria-hidden="true"
                    />
                    <div>
                      <p className="text-sm font-semibold text-slate-900">{item.title}</p>
                      <p className="mt-0.5 text-sm leading-snug text-slate-600">{item.body}</p>
                    </div>
                  </li>
                ))}
              </ul>
            </aside>
          </div>
        </section>

        {/* Courses */}
        <section className="border-b border-slate-200 bg-[#f7f8fa]" aria-labelledby="courses-heading">
          <div className="mx-auto max-w-6xl px-4 py-16 sm:px-6 sm:py-20 lg:px-8">
            <div className="max-w-2xl">
              <p className="text-sm font-semibold text-[#1865f2]">Courses</p>
              <h2
                id="courses-heading"
                className="mt-2 text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl"
              >
                What you can practice today
              </h2>
              <p className="mt-3 text-base leading-relaxed text-slate-600">
                Active Alberta courses with complete practice banks. Open any course
                from the dashboard to start a quiz, then use Daily Practice or Weakness
                Map after you create a free account.
              </p>
            </div>

            <ul className="mt-10 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {AVAILABLE_COURSES.map((course) => (
                <li key={course.code}>
                  <article
                    className={[
                      'flex h-full flex-col rounded-xl border border-slate-200 border-l-4 bg-white p-5 shadow-[0_1px_2px_rgba(15,23,42,0.04)]',
                      areaAccent[course.area] || 'border-l-slate-400',
                    ].join(' ')}
                  >
                    <div className="flex items-start justify-between gap-3">
                      <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                        {course.area}
                      </p>
                      <span className="rounded-md bg-slate-100 px-2 py-0.5 font-mono text-[11px] font-medium text-slate-700">
                        {course.code}
                      </span>
                    </div>
                    <h3 className="mt-3 text-lg font-semibold text-slate-900">
                      {course.name}
                    </h3>
                    <p className="mt-2 flex-1 text-sm leading-relaxed text-slate-600">
                      {course.blurb}
                    </p>
                    <p className="mt-4 text-xs font-medium text-slate-500">
                      Alberta Program of Studies aligned
                    </p>
                  </article>
                </li>
              ))}
            </ul>
          </div>
        </section>

        {/* How it works */}
        <section className="border-b border-slate-200 bg-white" aria-labelledby="how-heading">
          <div className="mx-auto max-w-6xl px-4 py-16 sm:px-6 sm:py-20 lg:px-8">
            <div className="max-w-2xl">
              <p className="text-sm font-semibold text-[#1865f2]">How it works</p>
              <h2
                id="how-heading"
                className="mt-2 text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl"
              >
                How practice turns into a study plan
              </h2>
            </div>
            <ol className="mt-12 grid list-none grid-cols-1 gap-6 p-0 sm:grid-cols-3 sm:gap-5">
              {HOW_IT_WORKS.map((item) => (
                <li
                  key={item.step}
                  className="rounded-xl border border-slate-200 bg-[#f7f8fa] p-6"
                >
                  <p className="font-mono text-sm font-semibold tabular-nums text-[#1865f2]">
                    {item.step}
                  </p>
                  <h3 className="mt-3 text-lg font-semibold text-slate-900">
                    {item.title}
                  </h3>
                  <p className="mt-2 text-sm leading-relaxed text-slate-600">
                    {item.description}
                  </p>
                </li>
              ))}
            </ol>
          </div>
        </section>

        {/* Study tools */}
        <section className="border-b border-slate-200 bg-[#f7f8fa]" aria-labelledby="tools-heading">
          <div className="mx-auto max-w-6xl px-4 py-16 sm:px-6 sm:py-20 lg:px-8">
            <div className="max-w-2xl">
              <p className="text-sm font-semibold text-[#1865f2]">Study tools</p>
              <h2
                id="tools-heading"
                className="mt-2 text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl"
              >
                Daily Practice and Weakness Map
              </h2>
              <p className="mt-3 text-base leading-relaxed text-slate-600">
                After a quiz, these two tools help you decide what to study next.
              </p>
            </div>

            <div className="mt-10 grid gap-5 lg:grid-cols-2">
              <article
                className="rounded-2xl border border-slate-200 bg-white p-6 shadow-[0_1px_2px_rgba(15,23,42,0.04)] sm:p-8"
                aria-labelledby="daily-practice-heading"
              >
                <div className="inline-flex rounded-lg bg-orange-50 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-orange-800">
                  Habit tool
                </div>
                <h3
                  id="daily-practice-heading"
                  className="mt-4 text-xl font-bold text-slate-900"
                >
                  Daily Practice
                </h3>
                <p className="mt-3 text-base leading-relaxed text-slate-600">
                  Daily Practice builds a short set of questions from your course. It
                  uses your previous results to emphasize topics where your accuracy
                  has been lower, so you are not only repeating what you already know.
                </p>
                <p className="mt-3 text-base leading-relaxed text-slate-600">
                  Treat it as a steady habit — short sessions between longer quizzes.
                </p>
                <ul className="mt-5 space-y-2 border-t border-slate-100 pt-5 text-sm text-slate-700">
                  <li className="flex gap-2">
                    <span className="font-semibold text-slate-900">Not random</span>
                    <span className="text-slate-500">— guided by your recent accuracy</span>
                  </li>
                  <li className="flex gap-2">
                    <span className="font-semibold text-slate-900">Short sessions</span>
                    <span className="text-slate-500">— easier to keep consistent</span>
                  </li>
                </ul>
              </article>

              <article
                className="rounded-2xl border border-slate-200 bg-white p-6 shadow-[0_1px_2px_rgba(15,23,42,0.04)] sm:p-8"
                aria-labelledby="weakness-map-heading"
              >
                <div className="inline-flex rounded-lg bg-teal-50 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-teal-800">
                  Review tool
                </div>
                <h3
                  id="weakness-map-heading"
                  className="mt-4 text-xl font-bold text-slate-900"
                >
                  Weakness Map
                </h3>
                <p className="mt-3 text-base leading-relaxed text-slate-600">
                  Weakness Map shows your accuracy by topic for a selected course. It
                  highlights where results are strongest and where marks keep slipping,
                  so you can prioritize review instead of studying every unit equally.
                </p>
                <p className="mt-3 text-base leading-relaxed text-slate-600">
                  From there, jump into targeted practice on the topics that need the
                  most work.
                </p>
                <ul className="mt-5 space-y-2 border-t border-slate-100 pt-5 text-sm text-slate-700">
                  <li className="flex gap-2">
                    <span className="font-semibold text-slate-900">By topic</span>
                    <span className="text-slate-500">— see strengths and review areas</span>
                  </li>
                  <li className="flex gap-2">
                    <span className="font-semibold text-slate-900">Track progress</span>
                    <span className="text-slate-500">— watch accuracy change over time</span>
                  </li>
                </ul>
              </article>
            </div>
          </div>
        </section>

        {/* Alberta */}
        <section className="border-b border-slate-200 bg-white" aria-labelledby="alberta-heading">
          <div className="mx-auto max-w-6xl px-4 py-16 sm:px-6 sm:py-20 lg:px-8">
            <div className="rounded-2xl border border-slate-200 bg-[#0f1c2e] px-6 py-10 text-white sm:px-10 sm:py-12">
              <p className="text-sm font-semibold text-sky-300">For Alberta students</p>
              <h2
                id="alberta-heading"
                className="mt-2 max-w-2xl text-2xl font-bold tracking-tight sm:text-3xl"
              >
                Built around Alberta curriculum and diploma prep
              </h2>
              <ul className="mt-10 grid gap-6 sm:grid-cols-3">
                {ALBERTA_POINTS.map((point) => (
                  <li key={point.title} className="rounded-xl bg-white/5 p-5 ring-1 ring-white/10">
                    <h3 className="text-base font-semibold text-white">{point.title}</h3>
                    <p className="mt-2 text-sm leading-relaxed text-slate-300">
                      {point.description}
                    </p>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </section>

        {/* Why + CTA */}
        <section className="bg-[#f7f8fa]" aria-labelledby="different-heading">
          <div className="mx-auto max-w-6xl px-4 py-16 sm:px-6 sm:py-20 lg:px-8">
            <div className="mx-auto max-w-3xl text-center">
              <p className="text-sm font-semibold text-[#1865f2]">Why ABDiploma Hub</p>
              <h2
                id="different-heading"
                className="mt-2 text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl"
              >
                Practice that follows Alberta course topics
              </h2>
              <div className="mt-6 space-y-4 text-left text-base leading-relaxed text-slate-600 sm:text-center">
                <p>
                  Questions are organized by Alberta course and topic, so you can
                  practice what you are actually studying — not a mix of random
                  worksheets.
                </p>
                <p>
                  After each answer you get an explanation and common mistakes to watch
                  for, whether you got it right or wrong.
                </p>
                <p>
                  The site is free for students. Weakness Map and Daily Practice use
                  your own results to help you decide what to review next.
                </p>
              </div>
              <div className="mt-10 flex flex-col items-stretch justify-center gap-3 sm:flex-row sm:items-center">
                <Link
                  to="/dashboard"
                  onFocus={() => prefetchRoute('dashboard')}
                  onPointerEnter={() => prefetchRoute('dashboard')}
                  className={[
                    'inline-flex min-h-12 items-center justify-center rounded-lg bg-[#1865f2] px-8 py-3 text-base font-semibold text-white hover:bg-[#0f4ec9]',
                    LINK_FOCUS,
                  ].join(' ')}
                >
                  Start practicing
                </Link>
                <Link
                  to="/about"
                  onFocus={() => prefetchRoute('about')}
                  onPointerEnter={() => prefetchRoute('about')}
                  className={[
                    'inline-flex min-h-12 items-center justify-center rounded-lg border border-slate-300 bg-white px-8 py-3 text-base font-semibold text-slate-800 hover:bg-slate-50',
                    LINK_FOCUS,
                  ].join(' ')}
                >
                  About the project
                </Link>
              </div>
            </div>
          </div>
        </section>
      </main>

      <footer className="border-t border-slate-200 bg-white">
        <div className="mx-auto flex max-w-6xl flex-col items-center gap-2 px-4 py-10 text-center text-sm text-slate-600 sm:px-6 lg:px-8">
          <p className="font-medium text-slate-800">
            ABDiploma Hub — Free Alberta Diploma Exam Preparation
          </p>
          <Link
            to="/about"
            onFocus={() => prefetchRoute('about')}
            onPointerEnter={() => prefetchRoute('about')}
            className={['font-medium text-[#1865f2] hover:text-[#0f4ec9]', LINK_FOCUS].join(' ')}
          >
            About ABDiploma Hub
          </Link>
        </div>
      </footer>
    </div>
  )
}

export default Landing
