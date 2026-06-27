#!/usr/bin/env python3
"""Batch sitemap updater + IndexNow ping for search engines.
Deployed on VPS at /opt/batch-sitemap.py, runs daily via crontab.
"""
import xml.etree.ElementTree as ET
from datetime import datetime
import os, glob, json, urllib.request
from urllib.parse import urlparse

NOW = datetime.now().strftime("%Y-%m-%d")

# Domain -> IndexNow key mapping (add new customer domains here)
DOMAIN_KEYS = {
    "singxai.tech": "CHANGE_ME",
    "johormaid.com": "CHANGE_ME",
}

# Sites to update
SITES = glob.glob("/var/www/singxai.tech/demo/*/sitemap.xml")
if os.path.exists("/var/www/singxai.tech/sitemap.xml"):
    SITES.append("/var/www/singxai.tech/sitemap.xml")

for path in SITES:
    try:
        tree = ET.parse(path)
        root = tree.getroot()
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        changed = False
        for url in root.findall("sm:url", ns):
            lm = url.find("sm:lastmod", ns)
            if lm is not None and lm.text != NOW:
                lm.text = NOW
                changed = True
        if changed:
            tree.write(path, xml_declaration=True, encoding="utf-8")
            print(f"[{NOW}] Updated: {path}")
    except Exception as e:
        print(f"[ERROR] {path}: {e}")

# IndexNow ping for all configured domains
for domain, key in DOMAIN_KEYS.items():
    if key == "CHANGE_ME":
        continue
    body = json.dumps({
        "host": domain,
        "key": key,
        "keyLocation": f"https://{domain}/{key}.txt",
        "urlList": [f"https://{domain}/"]
    }).encode()
    req = urllib.request.Request(
        "https://www.bing.com/indexnow",
        data=body,
        headers={"Content-Type": "application/json; charset=utf-8"}
    )
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        print(f"[{NOW}] IndexNow {domain}: {resp.status}")
    except Exception as e:
        print(f"[{NOW}] IndexNow {domain} ERR: {e}")
