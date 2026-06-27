# Sitemap Cron：VPS 本地 crontab 模式

> 不要依赖本地 Hermes cron SSH 到 VPS 跑 sitemap——SSH 一断 sitemap 就停更。

## 脚本：`/opt/batch-sitemap.py`

```python
#!/usr/bin/env python3
"""Batch sitemap updater — updates lastmod for all sites."""
import xml.etree.ElementTree as ET
from datetime import datetime
import os, glob

NOW = datetime.now().strftime("%Y-%m-%d")

# All customer sites under demo/
SITES = glob.glob("/var/www/singxai.tech/demo/*/sitemap.xml")

# Also update singxai.tech main site
main_site = "/var/www/singxai.tech/sitemap.xml"
if os.path.exists(main_site):
    SITES.append(main_site)

for sitemap_path in SITES:
    try:
        tree = ET.parse(sitemap_path)
        root = tree.getroot()
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        updated = False
        for url in root.findall("sm:url", ns):
            lastmod = url.find("sm:lastmod", ns)
            if lastmod is not None and lastmod.text != NOW:
                lastmod.text = NOW
                updated = True
        if updated:
            tree.write(sitemap_path, xml_declaration=True, encoding="utf-8")
            print(f"[{NOW}] Updated: {sitemap_path}")
    except Exception as e:
        print(f"[ERROR] {sitemap_path}: {e}")
```

## VPS crontab

```bash
# 每天 8:00 AM 更新所有站点 sitemap lastmod
0 8 * * * python3 /opt/batch-sitemap.py >> /var/log/sitemap-cron.log 2>&1
```

## 本地 cron 处理

VPS 接管后，本地 `singx-sitemap-batch` cron 应暂停：
```bash
cronjob pause <job_id>
```

## 验证

```bash
# 检查 sitemap lastmod 是否是今天
curl -s https://域名.com/sitemap.xml | grep lastmod

# 检查 crontab 是否在跑
grep sitemap /var/log/sitemap-cron.log | tail -5
```
