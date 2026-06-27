---
name: singx-security-hardening
description: SingX 客户站安全加固一站式技能 — 安全头、路径拦截、恶意IP封禁、www重定向、缓存策略、源站保护。新建客户站或安全审计时加载。
version: 1.0.0
---

# SingX 安全加固

SingX 客户站建站后的安全加固流程。覆盖所有从 johormaid.com、singxai.tech 实战中积累的安全经验。

## 何时加载

- 新建客户站部署完成后
- 安全审计 / 爬虫检查后发现问题
- 用户问"网站安全吗""需要加固吗"

## 加固清单（9 项）

| # | 项目 | 重要性 | 说明 |
|:--:|------|:--:|------|
| 1 | 安全头五件套 | 🔴 | CSP + HSTS + X-Frame + X-Content-Type + Referrer-Policy |
| 2 | 路径拦截 | 🔴 | 15 类漏洞扫描路径返回 403 |
| 3 | www → 非www 301 | 🟡 | 防重复内容，SEO 必备 |
| 4 | IP 封禁 | 🟡 | 已知恶意 IP 加 deny |
| 5 | Cache-Control | 🟡 | 静态站用 public, max-age=3600 |
| 6 | server_tokens off | 🟢 | 隐藏 Nginx 版本号 |
| 7 | 源站 IP 保护 | 🟢 | CF-only 白名单 |
| 8 | /admin/ 路径 | 🔴 | 客户站必须拦截裸 /admin/ |
| 9 | 验证 | 🔴 | 逐项 curl 验证 |

---

## 1. 安全头五件套

在 Nginx `location /` 块中添加：

```nginx
add_header X-Content-Type-Options nosniff always;
add_header X-Frame-Options SAMEORIGIN always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy strict-origin-when-cross-origin always;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
add_header Permissions-Policy "camera=(), microphone=(), geolocation=()" always;
```

CSP 按站点实际情况定制。通用静态站模板：

```nginx
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.tailwindcss.com https://cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com https://fonts.googleapis.com; font-src 'self' https://cdnjs.cloudflare.com https://fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self'; frame-src 'self'; object-src 'none'; base-uri 'self'; form-action 'self'" always;
```

⚠️ CSP 中的域名按站点实际引用的 CDN 调整。如果站点用了其他 CDN（jsdelivr、unpkg 等），必须加上，否则资源被浏览器拦截。

**部署方式**：用 Python 脚本插入到 Nginx `location /` 块中（不要用 sed/heredoc）：

```python
# 在 location / { 之后插入安全头
with open('/etc/nginx/sites-enabled/SITE', 'r') as f:
    content = f.read()

headers = '''        add_header X-Content-Type-Options nosniff always;
        add_header X-Frame-Options SAMEORIGIN always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy strict-origin-when-cross-origin always;
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
        add_header Permissions-Policy "camera=(), microphone=(), geolocation=()" always;
'''

content = content.replace('    location / {\n', '    location / {\n' + headers)

with open('/etc/nginx/sites-enabled/SITE', 'w') as f:
    f.write(content)
```

---

## 2. 路径拦截（15 类）

在 `server` 块中、`root` 之前添加：

```nginx
# Block common vulnerability scan paths
location ~* ^/(\.env|\.git|wp-admin|wp-login|xmlrpc\.php|actuator|configprops|heapdump|threaddump|trace|env|logfile|firebase|credentials|key\.json|appsettings|account\.json|local-config|admin) {
    return 403;
}
```

**⚠️ 关键坑：`admin` 必须显式加入正则！**

`wp-admin` 不匹配裸 `/admin/`。客户站（如 johormaid.com）的 `/admin/` 是商家后台入口，必须拦截 — 所有管理都走主站 singxai.tech/admin。**只有 singxai.tech 主站本身才允许 /admin/**。

### 路径拦截覆盖的攻击类型

| 路径模式 | 拦截的攻击 |
|----------|-----------|
| `\.env`, `\.git` | 配置文件泄露扫描 |
| `wp-admin`, `wp-login`, `xmlrpc\.php` | WordPress 漏洞扫描 |
| `actuator`, `configprops`, `heapdump`, `threaddump` | Spring Boot Actuator 信息泄露 |
| `trace`, `dump` | 调试端点探测 |
| `firebase`, `credentials`, `key\.json`, `appsettings` | 云服务凭证扫描 |
| `logfile` | 日志文件探测 |
| `admin` | 后台入口暴露（客户站专用） |

### 部署方式

```python
block = '''    # Block common vulnerability scan paths
    location ~* ^/(\\.env|\\.git|wp-admin|wp-login|xmlrpc\\.php|actuator|configprops|heapdump|threaddump|trace|env|logfile|firebase|credentials|key\\.json|appsettings|account\\.json|local-config|admin) {
        return 403;
    }

'''

with open('/etc/nginx/sites-enabled/SITE', 'r') as f:
    content = f.read()

content = content.replace(
    '    root /var/www/...;\n    index index.html;',
    block + '    root /var/www/...;\n    index index.html;'
)
```

---

## 3. www → 非www 301

防重复内容。www 和裸域必须只有一个返回 200，另一个 301。

```nginx
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name www.EXAMPLE.COM;
    ssl_certificate /root/.acme.sh/EXAMPLE.COM_ecc/fullchain.cer;
    ssl_certificate_key /root/.acme.sh/EXAMPLE.COM_ecc/EXAMPLE.COM.key;
    return 301 https://EXAMPLE.COM$request_uri;
}
```

⚠️ johormaid 正确（有独立 redirect block），singxai 曾经缺失 www redirect（两个 server_name 写在一起），6月25日修复。

---

## 4. 已知恶意 IP 封禁

在 `server` 块中添加 `deny` 指令：

```nginx
# Block known malicious IPs
deny 20.63.8.12;       # Azure Toronto — WP vuln scanner, 52 req burst
deny 13.70.31.127;     # Azure HK — PHP webshell scanner, 30 req/2s
```

**已知恶意 IP 清单**（持续更新）：

| IP | 来源 | 行为 | 发现日期 |
|----|------|------|----------|
| `20.63.8.12` | Azure Toronto | WP漏洞扫描，52路径/次 | 2026-06-23 |
| `13.70.31.127` | Azure HK | PHP webshell扫描，30次/2秒 | 2026-06-25 |
| `45.45.237.206` | 不明 | 多UA伪造，凭证扫描 | 2026-05-28 |
| `35.247.253.44` | GCP | Spring Boot actuator扫描 | 2026-05-29 |
| `34.154.237.45` | GCP | TLS探测+多UA | 2026-05-29 |
| `34.176.252.5` | GCP | Docker-compose扫描 | 2026-05-29 |
| `35.228.51.74` | GCP | PHP配置扫描 | 2026-05-30 |
| `34.162.65.109` | GCP | .env变种扫描 | 2026-05-30 |
| `151.243.143.47` | BreezeHost SG | 伪造Baidu爬虫 | 2026-05-30 |
| `162.243.184.211` | DigitalOcean | WP指纹扫描 | 2026-05-31 |
| `3.0.52.182` | AWS SG | .env暴力扫描，170+次 | 2026-06-17 |

⚠️ 路径拦截 403 已覆盖这些扫描，IP deny 是额外防护层，两者不冲突。

---

## 5. Cache-Control

**静态营销站**用 `public, max-age=3600`（1小时浏览器缓存）。严禁 `no-cache, no-store` — 会阻止搜索引擎缓存页面。

```nginx
add_header Cache-Control "public, max-age=3600" always;
```

⚠️ johormaid 曾误设 `no-cache, no-store, must-revalidate` + `Pragma no-cache` + `Expires 0`，6月25日修复。

**客户端渲染的 SPA/PWA**（如商家后台）可以用默认值或短缓存。

---

## 6. server_tokens off

在 `/etc/nginx/nginx.conf` 的 `http` 块中：

```nginx
http {
    server_tokens off;
    ...
}
```

效果：响应头 `server: nginx` 不显示版本号。注意 `server_tokens off` 只缩短不删除 — 完全删除需要 `nginx-extras` 的 `more_clear_headers Server;`，但不推荐（增加依赖）。

---

## 7. 源站 IP 保护（CF-only 白名单）

如果站点套了 Cloudflare CDN，防止攻击者绕过 CF 直连源站：

参考 `nginx-access-log-analysis` 技能的 `references/cloudflare-nginx-whitelist.conf`。

核心配置：

```nginx
# 恢复真实访问者 IP
real_ip_header CF-Connecting-IP;
# set_real_ip_from 列出所有 CF IP 范围...

# 用 geo 检查连接是否来自 CF
geo $realip_remote_addr $is_cf {
    default 0;
    # 列出所有 CF IP...
}

# 每个 server 块中
if ($is_cf != 1) { return 403; }
```

⚠️ 未套 CF 的站点不需要此配置。

---

## 8. /admin/ 路径处理

**客户站**（如 johormaid.com）：
- `/admin/` → **必须 403**（路径拦截正则已包含 `admin`）
- 所有管理都走主站 `singxai.tech/admin`

**主站**（singxai.tech）：
- `/admin/` → **允许访问**（是合法的商家/管理员登录入口）
- 用 Nginx alias 指向 merchant 目录
- 路径拦截正则中**不加** `admin`

⚠️ 这是曾经踩过的坑：路径拦截的 `wp-admin` 不匹配裸 `/admin/`，导致 singxai 主站的管理后台被误报（实际是合法入口）、客户站的管理入口被遗漏。

---

## 9. 验证清单

加固完成后逐项 curl 验证：

```bash
# 安全头
curl -skI https://SITE/ | grep -iE 'x-content-type|x-frame|x-xss|referrer-policy|strict-transport|permissions-policy|csp|cache-control'

# 路径拦截（全部应返回 403）
for path in /.env /.git/config /wp-admin/install.php /xmlrpc.php /actuator/env /admin/; do
  code=$(curl -sk -o /dev/null -w "%{http_code}" "https://SITE$path")
  echo "$path → HTTP $code"
done

# www 重定向
curl -sk -o /dev/null -w "HTTP %{http_code} → %{redirect_url}" "https://www.SITE/"

# server_tokens
curl -skI https://SITE/ | grep -i 'server:'

# 首页正常
curl -sk -o /dev/null -w "HTTP %{http_code}" "https://SITE/"
```

---

## 部署步骤总结

1. **SCP 上传 Python 加固脚本到 VPS**
2. **执行**：`python3 /tmp/harden-SITE.py`
3. **nginx -t** → **systemctl reload nginx**
4. **逐项 curl 验证**

## 坑

- **sed/heredoc 不要在远程 Nginx 配置上用** — 嵌套引号必然损坏。永远用 Python 脚本 SCP 上传。
- **`location /plan` 是前缀匹配** — 会误伤 `/plan.html`。封目录用 `location = /plan` 或 `location /plan/`。
- **`wp-admin` 正则不匹配裸 `/admin/`** — 必须显式加 `admin|`。
- **`location /admin` 显式块覆盖正则拦截** — Nginx 的 `location /admin { ... }` 优先级高于 `location ~* ^/(...|admin|...) { return 403; }`。如果客户站有显式 `/admin` 块（如指向 merchant 登录页），正则中的 `admin` 不会生效，`/admin/` 仍返回 200。要拦截必须在显式块内加 `return 403;`，或删除显式块。singxai 主站除外（合法入口）。
- **Cache-Control: no-store 是 SEO 毒药** — 静态营销站禁止使用。
- **安全头必须在 `location /` 块内** — 放在 server 块可能不被继承。
- **路径拦截必须放在 `root` 指令之前** — 否则可能被 try_files 覆盖。
