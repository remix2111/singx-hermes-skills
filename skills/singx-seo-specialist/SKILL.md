---
name: singx-seo-specialist
description: SingX SEO 自动化 Agent — 客户站一键补全所有 SEO 标签，含 sitemap/robots/canonical/OG/hreflang/JSON-LD/GSC。
category: seo
tags: [singx, seo, automation, gsc, structured-data]
---

# SingX SEO Specialist

> 客户站 SEO 一键自动化。建站完成后自动补全所有 SEO 元素 + 提交 GSC。

## 触发条件

- DevOps 部署完成后自动调用
- 用户说"做 SEO"、"优化 SEO"、"检查 SEO"

## 所需参数

| 参数 | 示例 | 说明 |
|------|------|------|
| 域名 | johormaid.com | 正式域名 |
| 站点路径 | /var/www/singxai.tech/demo/johormaid | VPS 绝对路径 |
| 行业 | cleaning | 用于关键词生成 |
| 城市 | Johor Bahru | 本地 SEO |
| 三语关键词 | EN/BM/ZH | 各语言核心词 |

## SEO 执行流程

### 步骤 1：创建 sitemap.xml

```bash
cat > sitemap.xml << EOF
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://域名.com/</loc>
    <lastmod>$(date +%Y-%m-%d)</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>
EOF
```

上传到站点根目录。

### 步骤 2：创建 robots.txt

```
User-agent: *
Allow: /
Sitemap: https://域名.com/sitemap.xml
```

### 步骤 3：检查并补全 HTML Head 标签

检查现有标签，补全缺失项：

```bash
# 检查现有标签
grep -c 'canonical' index.html    # 目标: 1
grep -c 'hreflang' index.html     # 目标: 4
grep -c 'og:title' index.html     # 目标: ≥1
grep -c 'twitter:card' index.html # 目标: ≥1
grep -c 'ld+json' index.html      # 目标: 1
grep -c '<h1' index.html          # 目标: 1（SPA 单页）
```

**补全模板（在 </title> 后插入）：**

```html
<meta name="description" content="[三语关键词描述，120字以内]">
<meta name="keywords" content="[EN keywords], [BM keywords], [ZH keywords]">
<meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large">
<link rel="canonical" href="https://域名.com/">
<link rel="alternate" hreflang="en" href="https://域名.com/">
<link rel="alternate" hreflang="ms" href="https://域名.com/?lang=bm">
<link rel="alternate" hreflang="zh" href="https://域名.com/?lang=zh">
<link rel="alternate" hreflang="x-default" href="https://域名.com/">
<meta property="og:title" content="[品牌名] • [行业标语]">
<meta property="og:description" content="[简短描述]">
<meta property="og:url" content="https://域名.com/">
<meta property="og:type" content="website">
<meta property="og:locale" content="en_US">
<meta property="og:image" content="https://域名.com/assets/logo.svg">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="[品牌名] • [行业标语]">
```

⚠️ `og:image` 必须有——分享到 WhatsApp/Facebook 没有预览图是致命伤。如站点无 logo，先用 SVG 顶（`assets/logo.svg`），后续替换 PNG。

### 马来西亚市场关键词策略 🔴

**三语必须，优先级 BM ≥ EN > ZH**：马来市场最大群体是马来人（用马来文/英文搜索），华人次之。

```
EN: website builder [city], AI website, [industry] [city], small business website
BM: bina laman web [city], laman web perniagaan, [industry] [city], website murah
ZH: [城市][行业], [城市]建站, [服务名]
```

BM 关键词要包含 `murah`（便宜）、`perniagaan`（生意）这类高搜索量词。

### 步骤 4：添加 JSON-LD 结构化数据

根据页面内容选择合适的 schema 类型：

| 页面特征 | Schema 类型 | 适用 |
|---------|------------|------|
| 有地址/电话/营业时间 | `LocalBusiness` | 所有实体店客户 |
| 公司/组织（无实体地址） | `Organization` | singxai.tech 自身 |
| 页面底部有 FAQ/常见问题 | `FAQPage` | 有 FAQ 区块的站 |

#### 4a. LocalBusiness（默认，实体店客户）

在 `</body>` 前插入：

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "[品牌名]",
  "description": "[描述]",
  "url": "https://域名.com/",
  "telephone": "[电话]",
  "email": "[邮箱]",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "[地址]",
    "addressLocality": "[城市]",
    "addressCountry": "MY"
  },
  "openingHoursSpecification": {
    "@type": "OpeningHoursSpecification",
    "dayOfWeek": ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
    "opens": "09:00",
    "closes": "17:00"
  },
  "priceRange": "[价格区间]"
}
</script>
```

⚠️ JSON-LD 必须放在 `</body>` 之前，且 script 标签内不能出现 `</script>` 字符串。

#### 4b. FAQPage（页面有 FAQ/常见问题区块）

当页面底部已有 `<details>` 或手风琴 FAQ 区块时，提取 Q&A 文本生成 FAQPage schema。**必须在 `<head>` 中而非 `</body>` 前**——FAQ Schema 是页面级标记，Google 要求在 head 中。

插入位置：在 `</head>` 之前。

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "问题文本（用页面主要语言）",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "答案文本（与页面显示的完全一致）"
      }
    }
  ]
}
</script>
```

**关键规则**：
- Q&A 文本必须与页面可见内容完全一致——不一致会被 Google 标记为误导
- 用页面的 canonical 语言（x-default 的语言），不要多语言各一套
- 3-8 个问答效果最好，过多会稀释权重
- FAQ 问答覆盖真实顾客会搜索的问题（"退款吗"、"多久做好"、"包含什么"）

**验证**：
```bash
# Schema.org validator（无需 reCAPTCHA）
curl -s "https://validator.schema.org/" # 或浏览器打开 https://validator.schema.org/#url=https://域名.com/
# 检查 FAQPage 是否 0 错误 0 警告

# Google Rich Results Test（需要 reCAPTCHA，手动）
# https://search.google.com/test/rich-results?url=https://域名.com/
```

**FAQ Schema 的 SEO 价值**：Google 搜索结果会展开 Q&A 列表，占用面积是普通结果的 3-4 倍，点击率提升 20-30%。已有 FAQ 区块的站不做 FAQ Schema 等于浪费了这个流量入口。

> 完整模板和部署脚本见 `references/faq-schema-deploy.md`

```bash
# SPA 单页应用只能有 1 个 H1
grep -c '<h1' index.html
```

如果 >1：保留 hero 的 H1，其余改为 H2（class 不变，只改标签名）。

### 步骤 6：检查图片 Alt

```bash
# 所有 img 必须有 alt
grep -oP '<img[^>]*>' index.html | grep -v 'alt=' | wc -l  # 期望 0
```

### 步骤 7：修复资源路径

```bash
# 扫描绝对路径引用
grep -n 'singxai.tech/demo/' index.html
```

全部替换为相对路径：
```bash
sed -i 's|https://singxai.tech/demo/[项目名]/assets/|assets/|g' index.html
```

### 步骤 8：浏览器语言检测

检查是否有 navigator.language 检测：

```bash
grep -c 'navigator.language' index.html  # 期望 ≥1
```

如缺失，在语言初始化逻辑中添加：
- zh* → 中文
- ms*/my*/id → 马来语
- 其他 → 英文

### 步骤 9：提交 Google Search Console

**方式 A（秒过）：HTML 文件验证**
1. 用户在 GSC 下载验证文件
2. 上传到站点根目录
3. 用户点验证 → 秒过

**方式 B：DNS TXT 验证**
1. 用户在 GSC 获取 TXT 记录值
2. 在 Hostinger DNS 中添加 TXT 记录
3. 等待 5-30 分钟传播

验证通过后：
- 提交 sitemap: `https://域名.com/sitemap.xml`
- URL Inspection → Request Indexing
- 删除前任留下的旧 sitemap 记录

### 步骤 10：设置每日 SEO cronjob + IndexNow

**不要用本地 Hermes cron**（依赖 SSH，SSH 一断全停）。把 `batch-sitemap.py` 放 VPS crontab：

```bash
# VPS crontab
0 8 * * * python3 /opt/batch-sitemap.py >> /var/log/sitemap-cron.log 2>&1
```

脚本功能：
- 遍历所有 `demo/*/sitemap.xml` + `singxai.tech/sitemap.xml`
- 更新 lastmod 到今天日期
- 自动 ping IndexNow 通知 Bing 秒收

### 步骤 11：验证 SEO Cron 正在运行 🔴

部署后或用户问"SEO 正常吗"时，执行以下验证：

```bash
# 1. 检查 VPS crontab 有每日任务
ssh root@VPS "crontab -l | grep batch-sitemap"
# 期望: 0 8 * * * python3 /opt/batch-sitemap.py ...

# 2. 检查 sitemap lastmod 是否为今天
curl -sk https://域名.com/sitemap.xml | grep -oP '(?<=<lastmod>)[^<]+'
# 期望: 今天日期

# 3. 检查 robots.txt 含 Sitemap 指向
curl -sk https://域名.com/robots.txt | grep -i sitemap
# 期望: Sitemap: https://域名.com/sitemap.xml

# 4. 检查 batch-sitemap.py 脚本存在
ssh root@VPS "head -5 /opt/batch-sitemap.py"
```

> **pitfall: cron 假运行** — Hermes cronjob `deliver: local` 时成功但不送结果，`last_status` 可能为 null。VPS crontab 比本地 cron 可靠，因为它不依赖 SSH 连接。确认方法：直接检查 sitemap.xml 的 lastmod 是不是今天。

### 步骤 11：配置 IndexNow（Bing 秒收）

**为什么**：常规 sitemap 提交后 Bing 要几小时到几天才抓。IndexNow 是即时通知协议，提交后秒收。

**流程**：
```bash
# 1. 生成 key
KEY=$(openssl rand -hex 16)

# 2. 放 key 文件到站点根目录
echo $KEY > /var/www/singxai.tech/demo/域名/${KEY}.txt
# 验证: curl -sI https://域名.com/${KEY}.txt → 200

# 3. 在 batch-sitemap.py 中配置 domain→key 映射
# 4. 每次 sitemap 更新自动 POST https://www.bing.com/indexnow
```

**验证**：成功返回 200 或 202。失败通常是 `keyLocation` 路径不对或 key 文件不可访问。

⚠️ **每个域名独立 key**——singxai.tech 和 johormaid.com 用不同的 key 文件。

> 完整实现见 `references/indexnow-setup.md`
> batch-sitemap.py 脚本见 `scripts/batch-sitemap.py`

### 步骤 12：GSC/Bing 验证后提交

GSC 验证通过后：
- 提交 sitemap: `https://域名.com/sitemap.xml`
- URL Inspection → Request Indexing

Bing 验证通过后：
- 提交 sitemap: `https://域名.com/sitemap.xml`
- **不要等**——直接用 IndexNow（步骤 11），秒收
- Bing URL Inspection 看到「Title tag missing」误报（中文 title）→ 忽略，用英文 title 可避免

## SEO 检查清单（15项）

| # | 项目 | 命令 | 目标 |
|---|------|------|:--:|
| 1 | sitemap.xml | `curl -sI https://域名/sitemap.xml` | 200 |
| 2 | robots.txt | `curl -s https://域名/robots.txt` | 含 Sitemap |
| 3 | canonical | `grep -c canonical index.html` | 1 |
| 4 | hreflang | `grep -c hreflang index.html` | 4 |
| 5 | OG tags | `grep -c 'og:' index.html` | ≥7 |
| 6 | Twitter Card | `grep -c 'twitter:' index.html` | 2 |
| 7 | JSON-LD | `grep -c 'ld+json' index.html` | 1 |
| 8 | Keywords | `grep -c 'keywords' index.html` | 1 |
| 9 | H1 count | `grep -c '<h1' index.html` | 1 |
| 10 | img alt | `grep '<img' | grep -v alt` | 0 |
| 11 | 资源路径 | `grep 'singxai.tech/demo/' index.html` | 0 |
| 12 | 浏览器语言 | `grep -c 'navigator.language' index.html` | ≥1 |
| 13 | GSC 验证 | `curl -sI https://域名/googleXXXX.html` | 200 |
| 14 | Bing 验证 | `curl -sI https://域名/BingSiteAuth.xml` | 200 |
| 15 | IndexNow | `curl -sI https://域名/KEY.txt` → `python3 /opt/batch-sitemap.py` | 200/202 |

## 三语关键词模板

### 清洁服务
```
EN: professional cleaning services, [city], hourly cleaner, part-time cleaner
BM: perkhidmatan pembersihan, [city], pencuci sambilan
ZH: [城市]专业清洁服务, 钟点清洁, 住家清洁
```

### 餐饮
```
EN: [city] coffee shop, traditional food, best [cuisine] in [area]
BM: kedai kopi [city], makanan tradisional, sarapan pagi
ZH: [城市]咖啡店, 传统美食, 早餐
```

### 美容
```
EN: hair salon [city], beauty treatment, nail art [area]
BM: salon rambut [city], rawatan kecantikan
ZH: [城市]美发沙龙, 美容护理, 美甲
```

### 杂货店
```
EN: grocery store [city], mini market [area], daily necessities
BM: kedai runcit [city], pasar mini, barang keperluan harian
ZH: [城市]杂货店, 日常用品, 迷你超市
```

## 关键陷阱

- **sed 重复插入**：用 grep -c 先检查数量，避免标签叠加
- **JSON-LD 引号**：单引号 `'` 在 JSON 中不需要转义，双引号 `"` 需要 `\\\\\\\"`
- **hreflang 语言代码**：马来语用 `ms`（不是 `bm`），中文用 `zh`
- **canonical 指向**：必须指向正式域名，不是 demo 地址
- **资源路径遗漏**：除了 HTML，检查 CSS 中的 `url()` 和 JS 中的图片路径
- **旧 WordPress 域名迁移 404 陷阱** 🔴：接手旧域名（如 johormaid.com 以前跑过 WP）时，Google/Bing 索引里残留大量旧 URL（`/about/`、`/services/`、`/wp-content/...`）。用户搜到点击全是 404。必须在 Nginx 加 301 重定向，把旧 WP 路径全部指到首页，详见 `references/wp-migration-301-redirects.md`
- **`og:image` 不可省略**：马来西亚市场 WhatsApp 分享极其高频，没有 og:image 分享出去是白板。没有 logo 先用 SVG 占位
- **sitemap cron 放 VPS 不靠本地**：本地 Hermes cron 依赖 SSH，SSH 一断 sitemap 停更。用 VPS crontab 跑 `batch-sitemap.py`，见 `references/vps-sitemap-cron.md`
- **Title 用英文（Bing 不吃中文）** 🔴：Bing URL Inspection 看到中文 title 会误报「Title tag missing」——title 明明存在，但 Bing 解析不了。马来西亚市场用英文 title（含核心 EN keywords），description 可以保持三语

## 按域名追踪爬虫（Nginx 独立日志）

单一日志文件无法区分哪个站被哪些爬虫抓了多少次——SEO 优化需要按域名统计数据。

**修复**：每个客户站的 nginx server block 加入独立 access_log：

```nginx
server {
    listen 443 ssl http2;
    server_name 域名.com;
    access_log /var/log/nginx/域名-access.log;
    ...
}
```

加入后重载 nginx，之后即可按域名精确查询：

```bash
# 查看 johormaid 被 Google 抓了多少次
grep -c "Googlebot" /var/log/nginx/johormaid-access.log

# 查看 ChatGPT-User 实时抓取
grep "ChatGPT-User" /var/log/nginx/johormaid-access.log | tail -5

# 对比两个站的爬虫活跃度
for log in /var/log/nginx/*-access.log; do
  echo "$(basename $log): $(grep -ci 'bot\|crawl\|spider' $log 2>/dev/null || echo 0)"
done
```

⚠️ **`sites-enabled` symlink 陷阱**：修改 `/etc/nginx/sites-available/` 后，如果 `/etc/nginx/sites-enabled/` 里是独立文件副本而非 symlink，改动不会生效。新站部署后必须验证：`ls -la /etc/nginx/sites-enabled/域名.com` 应显示 `→` 指向 sites-available。johormaid 和 singxai 都中过这个坑。
