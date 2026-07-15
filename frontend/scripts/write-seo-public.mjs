/**
 * Writes robots.txt and sitemap.xml into public/ from VITE_SITE_URL.
 * Invoked before production builds so crawl files match the deploy domain.
 */
import { writeFileSync, mkdirSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { loadEnv } from 'vite'

const __dirname = dirname(fileURLToPath(import.meta.url))
const root = join(__dirname, '..')

const mode = process.env.NODE_ENV === 'production' ? 'production' : 'development'
const env = loadEnv(mode, root, 'VITE_')
const siteUrl = String(env.VITE_SITE_URL || process.env.VITE_SITE_URL || 'https://abdiplomahub.com')
  .trim()
  .replace(/\/$/, '')

if (!/^https?:\/\//i.test(siteUrl)) {
  console.error(`Invalid VITE_SITE_URL: ${siteUrl}`)
  process.exit(1)
}

const publicDir = join(root, 'public')
mkdirSync(publicDir, { recursive: true })

const robots = `User-agent: *
Allow: /
Allow: /welcome
Allow: /about
Allow: /login
Allow: /register

# Private / authenticated product surfaces
Disallow: /admin
Disallow: /dashboard
Disallow: /quiz
Disallow: /profile
Disallow: /daily-practice
Disallow: /weakness-map

Sitemap: ${siteUrl}/sitemap.xml
`

const paths = [
  { loc: '/welcome', changefreq: 'weekly', priority: '1.0' },
  { loc: '/about', changefreq: 'monthly', priority: '0.8' },
  { loc: '/login', changefreq: 'yearly', priority: '0.3' },
  { loc: '/register', changefreq: 'yearly', priority: '0.4' },
]

const urlEntries = paths
  .map(
    ({ loc, changefreq, priority }) => `  <url>
    <loc>${siteUrl}${loc}</loc>
    <changefreq>${changefreq}</changefreq>
    <priority>${priority}</priority>
  </url>`,
  )
  .join('\n')

const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urlEntries}
</urlset>
`

writeFileSync(join(publicDir, 'robots.txt'), robots, 'utf8')
writeFileSync(join(publicDir, 'sitemap.xml'), sitemap, 'utf8')
console.log(`SEO public files written for ${siteUrl}`)
