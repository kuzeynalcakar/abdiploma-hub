import { useEffect } from 'react'

/** Production site origin — override with VITE_SITE_URL (no trailing slash). */
export const SITE_URL = (
  import.meta.env.VITE_SITE_URL || 'https://abdiplomahub.com'
).replace(/\/$/, '')

export const DEFAULT_TITLE =
  'ABDiploma Hub — Free Alberta Diploma Exam Preparation'

export const DEFAULT_DESCRIPTION =
  'Free Alberta Diploma Exam preparation for Biology 30, Math 30-1, and other Alberta courses. Curriculum-aligned practice questions, clear explanations, Weakness Map, and Daily Practice.'

export const OG_IMAGE_PATH = '/og-image.jpg'

function absoluteUrl(pathOrUrl) {
  if (!pathOrUrl) return SITE_URL
  if (/^https?:\/\//i.test(pathOrUrl)) return pathOrUrl
  const path = pathOrUrl.startsWith('/') ? pathOrUrl : `/${pathOrUrl}`
  return `${SITE_URL}${path}`
}

function ensureMeta(attr, key, content) {
  if (content == null || content === '') return
  let el = document.head.querySelector(`meta[${attr}="${key}"]`)
  if (!el) {
    el = document.createElement('meta')
    el.setAttribute(attr, key)
    document.head.appendChild(el)
  }
  el.setAttribute('content', content)
}

function ensureLink(rel, href, attributes = {}) {
  if (!href) return
  let el = document.head.querySelector(`link[rel="${rel}"]`)
  if (!el) {
    el = document.createElement('link')
    el.setAttribute('rel', rel)
    document.head.appendChild(el)
  }
  el.setAttribute('href', href)
  Object.entries(attributes).forEach(([name, value]) => {
    if (value != null) el.setAttribute(name, value)
  })
}

/**
 * Apply document SEO tags for the current route.
 * Safe to call repeatedly; upserts tags in <head>.
 */
export function applyPageSeo({
  title = DEFAULT_TITLE,
  description = DEFAULT_DESCRIPTION,
  path = '/',
  image = OG_IMAGE_PATH,
  type = 'website',
  robots = 'index,follow',
  noCanonical = false,
} = {}) {
  const url = absoluteUrl(path)
  const imageUrl = absoluteUrl(image)

  document.title = title

  ensureMeta('name', 'description', description)
  ensureMeta('name', 'robots', robots)
  ensureMeta('name', 'theme-color', '#2563EB')

  if (!noCanonical) {
    ensureLink('canonical', url)
  }

  ensureMeta('property', 'og:title', title)
  ensureMeta('property', 'og:description', description)
  ensureMeta('property', 'og:image', imageUrl)
  ensureMeta('property', 'og:url', url)
  ensureMeta('property', 'og:type', type)
  ensureMeta('property', 'og:site_name', 'ABDiploma Hub')
  ensureMeta('property', 'og:locale', 'en_CA')

  ensureMeta('name', 'twitter:card', 'summary_large_image')
  ensureMeta('name', 'twitter:title', title)
  ensureMeta('name', 'twitter:description', description)
  ensureMeta('name', 'twitter:image', imageUrl)
}

/**
 * Hook: keep title + social/meta tags in sync for a page.
 */
export function usePageSeo(options) {
  const {
    title,
    description,
    path,
    image,
    type,
    robots,
    noCanonical,
  } = options || {}

  useEffect(() => {
    applyPageSeo({
      title,
      description,
      path,
      image,
      type,
      robots,
      noCanonical,
    })
  }, [title, description, path, image, type, robots, noCanonical])
}

/** JSON-LD script manager — replaces node when id matches. */
export function upsertJsonLd(id, data) {
  let el = document.getElementById(id)
  if (!data) {
    el?.remove()
    return
  }
  if (!el) {
    el = document.createElement('script')
    el.type = 'application/ld+json'
    el.id = id
    document.head.appendChild(el)
  }
  el.textContent = JSON.stringify(data)
}

export function removeJsonLd(id) {
  document.getElementById(id)?.remove()
}

export function buildOrganizationJsonLd() {
  return {
    '@context': 'https://schema.org',
    '@type': 'EducationalOrganization',
    name: 'ABDiploma Hub',
    url: SITE_URL,
    description: DEFAULT_DESCRIPTION,
    logo: absoluteUrl('/favicon.svg'),
    areaServed: {
      '@type': 'AdministrativeArea',
      name: 'Alberta, Canada',
    },
  }
}

export function buildWebSiteJsonLd() {
  return {
    '@context': 'https://schema.org',
    '@type': 'WebSite',
    name: 'ABDiploma Hub',
    url: SITE_URL,
    description: DEFAULT_DESCRIPTION,
    inLanguage: 'en-CA',
    publisher: {
      '@type': 'EducationalOrganization',
      name: 'ABDiploma Hub',
      url: SITE_URL,
    },
  }
}

export function buildCourseJsonLd({ name, description, urlPath }) {
  return {
    '@context': 'https://schema.org',
    '@type': 'Course',
    name,
    description,
    provider: {
      '@type': 'EducationalOrganization',
      name: 'ABDiploma Hub',
      url: SITE_URL,
    },
    url: absoluteUrl(urlPath || '/welcome'),
    isAccessibleForFree: true,
    inLanguage: 'en-CA',
    educationalLevel: 'High School',
    about: {
      '@type': 'Thing',
      name: 'Alberta Diploma Exam',
    },
  }
}
