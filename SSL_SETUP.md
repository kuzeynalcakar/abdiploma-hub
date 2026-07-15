# SSL / HTTPS setup — ABDiploma Hub

Terminate TLS at the reverse proxy or platform edge (nginx, Caddy, Cloudflare, Fly, Render, etc.). The FastAPI process should typically see plain HTTP from the proxy on a private network.

## Goals

- Public traffic only on HTTPS
- HTTP requests redirect to HTTPS
- Session and guest-quiz cookies use the `Secure` flag in production
- HSTS is enabled **only** when HTTPS is correctly configured (production)

## Domain connection

1. Point DNS for `abdiplomahub.com` (and `www` if desired) to your host:
   - **A / AAAA** to the load balancer or VM, or
   - **CNAME** to the platform hostname (e.g. `*.onrender.com`, Cloudflare)
2. Set application URLs to match DNS:
   - Frontend build: `VITE_SITE_URL=https://abdiplomahub.com`
   - Backend: `FRONTEND_URL=https://abdiplomahub.com` (add `,https://www.abdiplomahub.com` if both are used)
3. Prefer a single canonical host (apex **or** www). Redirect the other at the edge.

## Certificate setup

### Option A — Platform managed (recommended)

Most PaaS providers issue and renew certificates when a custom domain is attached. Follow the host’s “Custom domain + TLS” docs.

### Option B — Caddy

```caddyfile
abdiplomahub.com {
  reverse_proxy localhost:8000
}
```

Caddy obtains and renews Let’s Encrypt certificates automatically.

### Option C — nginx + Certbot

1. Obtain a certificate:

```bash
sudo certbot --nginx -d abdiplomahub.com -d www.abdiplomahub.com
```

2. Ensure HTTP → HTTPS redirect (Certbot usually adds this):

```nginx
server {
  listen 80;
  server_name abdiplomahub.com www.abdiplomahub.com;
  return 301 https://$host$request_uri;
}
```

3. Proxy to the API / static site over HTTPS:

```nginx
server {
  listen 443 ssl http2;
  server_name abdiplomahub.com;

  ssl_certificate     /etc/letsencrypt/live/abdiplomahub.com/fullchain.pem;
  ssl_certificate_key /etc/letsencrypt/live/abdiplomahub.com/privkey.pem;

  # Static SPA (adjust root)
  root /var/www/abdiplomahub/dist;
  location / {
    try_files $uri $uri/ /index.html;
  }

  # API (same-origin /api)
  location /api/ {
    proxy_pass http://127.0.0.1:8000/api/;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
  }
}
```

## Application settings (after HTTPS works)

| Setting | Production value | Notes |
|--------|------------------|-------|
| `ENVIRONMENT` | `production` | Enables safe defaults |
| Cookie `Secure` | auto `true` | Via `cookie_secure` when env is production |
| `ENABLE_HSTS` | default on | Or set at nginx/Caddy/CDN |
| `FRONTEND_URL` | `https://…` | CORS allowlist |

Confirm with:

```bash
cd backend
python scripts/check_production_config.py
```

## HTTP → HTTPS redirect

Configure at the edge (examples above). Do **not** rely on the FastAPI app alone for redirects when TLS terminates at the proxy.

## HSTS

- The API sets `Strict-Transport-Security: max-age=31536000; includeSubDomains` when `ENVIRONMENT=production` (or `ENABLE_HSTS=true`).
- Also set HSTS on the CDN/static host for HTML responses.
- Only enable after HTTPS is verified for all hostnames you serve; otherwise browsers will refuse HTTP.

## Renewal

| Method | Renewal |
|--------|---------|
| Platform TLS | Automatic |
| Caddy | Automatic |
| Certbot | `certbot renew` (timer usually installed); test with `certbot renew --dry-run` |

After renewal, reload nginx if required: `sudo systemctl reload nginx`.

## Checklist

- [ ] DNS points to the correct host
- [ ] Valid certificate for all public hostnames
- [ ] HTTP redirects to HTTPS
- [ ] `VITE_SITE_URL` and `FRONTEND_URL` use `https://`
- [ ] Production config check passes
- [ ] Cookies show `Secure` in browser DevTools after login
- [ ] HSTS present on HTTPS responses (API and static)
