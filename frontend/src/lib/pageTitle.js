import { useEffect } from 'react'
import { applyPageSeo, DEFAULT_TITLE } from './seo'

export const DEFAULT_DOCUMENT_TITLE = DEFAULT_TITLE

const COURSE_TITLES = {
  BIO30: 'ABDiploma Hub — Biology 30 Practice',
  'MATH30-1': 'ABDiploma Hub — Math 30-1 Practice',
}

export function courseDocumentTitle(courseCode, courseName) {
  if (courseCode && COURSE_TITLES[courseCode]) {
    return COURSE_TITLES[courseCode]
  }
  if (courseName) {
    return `ABDiploma Hub — ${courseName} Practice`
  }
  return DEFAULT_DOCUMENT_TITLE
}

export function pageDocumentTitle(pageTitle) {
  if (!pageTitle) return DEFAULT_DOCUMENT_TITLE
  return `${pageTitle} | ABDiploma Hub`
}

/**
 * Keep document title in sync. Prefer `usePageSeo` on public/indexable routes.
 */
export function useDocumentTitle(title) {
  useEffect(() => {
    const previous = document.title
    document.title = title || DEFAULT_DOCUMENT_TITLE
    return () => {
      document.title = previous
    }
  }, [title])
}

/** Title + noindex for authenticated / private app-shell pages. */
export function useAppPageSeo(pageTitle, documentTitle) {
  const title = documentTitle || pageDocumentTitle(pageTitle)
  useEffect(() => {
    applyPageSeo({
      title,
      description:
        'Practice Alberta Diploma Exam questions on ABDiploma Hub — curriculum-aligned quiz, feedback, and progress tracking.',
      path: typeof window !== 'undefined' ? window.location.pathname : '/',
      robots: 'noindex,nofollow',
    })
  }, [title])
}

export {
  usePageSeo,
  applyPageSeo,
  SITE_URL,
  DEFAULT_DESCRIPTION,
} from './seo'
