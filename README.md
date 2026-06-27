# SingX Hermes 技能包

为 [Hermes Agent](https://hermes-agent.nousresearch.com) 打造的两个实战技能——在马来西亚真实商家网站上淬炼出来的安全加固与 SEO 方案。

## 技能

### 1. singx-security-hardening（安全加固）
静态站点 Nginx 一键安全加固：
- 6 项安全头（CSP、HSTS、X-Frame、X-Content、Referrer、Permissions）
- 15 类路径拦截（`.env`、`wp-admin`、`xmlrpc`、Spring Boot actuator 等）
- 已知恶意 IP 封禁清单
- www → 非www 301 重定向
- SEO 友好缓存策略 `Cache-Control: public, max-age=3600`
- `server_tokens off` 隐藏版本号
- 自动化验证清单

附带 `harden-site.py` 一键脚本：SCP 到 VPS 直接跑，自动备份 → nginx 测试 → 重载 → 验证。

### 2. singx-seo-specialist（SEO 专家）
静态单页站点 SEO 标签全量注入：
- Title、Description、Keywords（中英巫三语）
- Open Graph + Twitter Card
- JSON-LD 结构化数据（LocalBusiness / Organization / FAQPage）
- Canonical URL
- Sitemap.xml 生成 + VPS crontab 每日自动更新
- IndexNow 秒推 Bing
- robots.txt 含正确 Disallow 规则
- Google Search Console / Bing Webmaster 验证

## 安装

看 [INSTALL.md](INSTALL.md)。

## 许可

MIT
