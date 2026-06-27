# IndexNow Setup for SingX Customer Sites

## What is IndexNow

IndexNow is a push protocol that instantly notifies search engines (Bing, Yandex, etc.) when a site's content changes. Instead of waiting for crawlers to discover updates via sitemap polling (hours to days), IndexNow tells search engines immediately.

## Setup for a new customer site

### 1. Generate an IndexNow key

```bash
ssh root@YOUR_VPS_IP
KEY=$(openssl rand -hex 16)
echo "Key: $KEY"
```

### 2. Place the key file on the site

```bash
# For demo sites (served from singxai.tech/demo/SITENAME/)
echo $KEY > /var/www/singxai.tech/demo/SITENAME/${KEY}.txt

# Verify
curl -sI https://DOMAIN.com/${KEY}.txt
# Expect: HTTP/2 200
```

### 3. Add domain+key to batch-sitemap.py

Edit `/opt/batch-sitemap.py` on the VPS, add to `DOMAIN_KEYS` dict:

```python
DOMAIN_KEYS = {
    "singxai.tech": "...",
    "johormaid.com": "...",
    "NEWDOMAIN.com": "NEW_KEY_HERE",  # ← add this line
}
```

### 4. Test

```bash
python3 /opt/batch-sitemap.py
# Expect: [DATE] IndexNow NEWDOMAIN.com: 200 or 202
```

### 5. Done

The daily cron at 8:00 AM will now auto-ping IndexNow for this domain every time the sitemap updates.

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| HTTP 400 | `keyLocation` URL doesn't match key file location | Verify key file is at exact URL in the JSON |
| HTTP 403 | Key file not accessible | Check permissions, nginx config |
| HTTP 404 | Key file doesn't exist | Re-upload key file |

## Current Keys (2026-06-14)

| Domain | Key |
|--------|-----|
| singxai.tech | YOUR_INDEXNOW_KEY |
| johormaid.com | YOUR_INDEXNOW_KEY |
