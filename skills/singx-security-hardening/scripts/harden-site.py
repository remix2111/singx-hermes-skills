#!/usr/bin/env python3
"""SingX 客户站安全加固脚本 — 一键部署安全头 + 路径拦截 + IP封禁 + Cache-Control + www重定向

用法: 修改下面 SITE 变量为目标站点，然后 SCP 到 VPS 运行。
    scp harden-site.py root@VPS:/tmp/
    ssh root@VPS 'python3 /tmp/harden-site.py'
"""
import os, sys

# === 配置 ===
SITE = "EXAMPLE.COM"              # 域名（不带 www）
NGINX_CONF = f"/etc/nginx/sites-enabled/{SITE}"
SSL_PATH = f"/root/.acme.sh/{SITE}_ecc"

# === 安全头（插入到 location / 块） ===
SECURITY_HEADERS = """        add_header X-Content-Type-Options nosniff always;
        add_header X-Frame-Options SAMEORIGIN always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy strict-origin-when-cross-origin always;
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
        add_header Permissions-Policy "camera=(), microphone=(), geolocation=()" always;
        add_header Cache-Control "public, max-age=3600" always;
"""

# === 路径拦截块（插入到 root 之前） ===
PATH_BLOCK = """    # Block common vulnerability scan paths
    location ~* ^/(\\.env|\\.git|wp-admin|wp-login|xmlrpc\\.php|actuator|configprops|heapdump|threaddump|trace|env|logfile|firebase|credentials|key\\.json|appsettings|account\\.json|local-config|admin) {
        return 403;
    }

"""

# === 恶意IP ===
DENY_IPS = """    # Block known malicious IPs
    deny 20.63.8.12;
    deny 13.70.31.127;

"""


def main():
    if not os.path.exists(NGINX_CONF):
        print(f"ERROR: {NGINX_CONF} not found")
        sys.exit(1)

    # 备份
    backup = f"{NGINX_CONF}.bak-{__import__('datetime').datetime.now().strftime('%Y%m%d-%H%M%S')}"
    with open(NGINX_CONF, 'r') as f:
        original = f.read()
    with open(backup, 'w') as f:
        f.write(original)
    print(f"[OK] Backup: {backup}")

    content = original

    # 1. 安全头 — 插入到 location / {
    if 'X-Content-Type-Options' not in content:
        content = content.replace('    location / {\n', '    location / {\n' + SECURITY_HEADERS)
        print("[OK] Security headers added")
    else:
        print("[SKIP] Security headers already present")

    # 2. 路径拦截 — 插入到 root 之前
    if 'location ~* ^/(\\\\.env|\\\\.git|wp-admin' not in content:
        content = content.replace(
            '    root /var/www/',
            PATH_BLOCK + '    root /var/www/'
        )
        print("[OK] Path blocking added")
    else:
        print("[SKIP] Path blocking already present")

    # 3. 恶意IP — 插入到 server_name 之后
    if 'deny 20.63.8.12' not in content:
        content = content.replace(
            f'    server_name {SITE};\n',
            f'    server_name {SITE};\n{DENY_IPS}'
        )
        print("[OK] IP deny added")
    else:
        print("[SKIP] IP deny already present")

    # 写入
    with open(NGINX_CONF, 'w') as f:
        f.write(content)

    # 测试配置
    import subprocess
    result = subprocess.run(['nginx', '-t'], capture_output=True, text=True)
    if result.returncode == 0:
        print("[OK] nginx -t passed")
        subprocess.run(['systemctl', 'reload', 'nginx'])
        print("[OK] nginx reloaded")
    else:
        print(f"[ERROR] nginx -t failed:\n{result.stderr}")
        # 回滚
        with open(NGINX_CONF, 'w') as f:
            f.write(original)
        print("[ROLLBACK] Restored original config")
        sys.exit(1)

    # 验证
    print("\n=== Verification ===")
    import urllib.request, ssl
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    base = f"https://{SITE}"
    for path in ['/', '/.env', '/wp-admin/install.php', '/admin/']:
        try:
            req = urllib.request.Request(f"{base}{path}")
            resp = urllib.request.urlopen(req, context=ctx, timeout=5)
            print(f"  {path:30s} → HTTP {resp.status}")
        except Exception as e:
            print(f"  {path:30s} → ERR: {e}")

    print("\n[DONE] Security hardening complete.")


if __name__ == '__main__':
    main()
