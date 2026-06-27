# WordPress → Static Site 迁移：旧 URL 301 重定向

接手旧域名时（原站跑过 WordPress），搜索引擎索引里残留大量旧 URL。用户搜索点击后全是 404，伤 SEO 且伤用户体验。

## 症状

Google/Bing 爬虫持续访问不存在的路径（来自旧 WP 结构）：
```
/about/  /services/  /faq-2/  /contact/  /blog/
/office-cleaning/  /carpet-cleaning/  /sofa-cleaning/
/cn/  /zh/  /privacy/  /privacy-policy/
/wp-content/uploads/2024/12/client_4-768x384.png
/wp-content/plugins/elementor/assets/js/...
```

## 修复：Nginx 301 批量重定向到首页

在 HTTPS server block 的 `location /` 之前插入：

```nginx
# Redirect old WordPress URLs to homepage
location ~* ^/(about|services|faq-2|contact|blog|privacy|privacy-policy|cn|zh)/?$ {
    return 301 /;
}
location ~* ^/(office-cleaning|sofa-cleaning|carpet-cleaning|mattress-cleaning|general-cleaning|post-renovation-cleaning)(-cn)?/?$ {
    return 301 /;
}
location ~* ^/wp-content/ {
    return 301 /;
}
```

## 部署方式

```bash
# 用 Python 插入（避免 shell heredoc 引号地狱）
python3 << 'PYEOF'
with open("/etc/nginx/sites-available/域名.com") as f:
    conf = f.read()

redirects = """    # Redirect old WordPress URLs to homepage
    location ~* ^/(about|services|faq-2|contact|blog|privacy|privacy-policy|cn|zh)/?$ {
        return 301 /;
    }
    location ~* ^/(office-cleaning|sofa-cleaning|carpet-cleaning|mattress-cleaning|general-cleaning|post-renovation-cleaning)(-cn)?/?$ {
        return 301 /;
    }
    location ~* ^/wp-content/ {
        return 301 /;
    }

"""

marker = "    root /var/www/singxai.tech/demo/站点目录;"
conf = conf.replace(marker, redirects + marker)

with open("/etc/nginx/sites-available/域名.com", "w") as f:
    f.write(conf)
PYEOF

nginx -t && systemctl reload nginx
```

## 验证

```bash
for path in "/about/" "/services/" "/office-cleaning/" "/wp-content/uploads/x.jpg"; do
  code=$(curl -sI -o /dev/null -w "%{http_code}" https://域名$path)
  echo "$path → $code"  # 期望全部 301
done
```

## 为什么不用 404

- 301 保留外链权重（旧 URL 可能有其他网站引用）
- Google 看到 301 会更新索引，比 404 快
- 用户体验：点旧链接直接到首页，而不是死胡同
