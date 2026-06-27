# SingX Hermes Skills

Two security & SEO skills for [Hermes Agent](https://hermes-agent.nousresearch.com) — battle-tested on real Malaysian business sites.

## Skills

### 1. singx-security-hardening
One-command Nginx security hardening for static sites:
- 6 security headers (CSP, HSTS, X-Frame, X-Content, Referrer, Permissions)
- 15-class path blocking (`.env`, `wp-admin`, `xmlrpc`, Spring Boot actuators...)
- Known malicious IP deny list
- www → non-www 301 redirect
- SEO-friendly `Cache-Control: public, max-age=3600`
- `server_tokens off`
- Automated verification checklist

Includes `harden-site.py` — SCP to VPS and run, handles backup + nginx test + reload + verify.

### 2. singx-seo-specialist
Complete SEO tag injection for static single-page sites:
- Title, description, keywords (trilingual EN/BM/ZH)
- Open Graph + Twitter Card
- JSON-LD structured data (LocalBusiness / Organization / FAQPage)
- Canonical URL
- Sitemap.xml generation with daily auto-update cron
- IndexNow instant push to Bing
- robots.txt with proper Disallow rules
- Google Search Console / Bing Webmaster verification

## Install

See [INSTALL.md](INSTALL.md).

## License

MIT
