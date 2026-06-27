# FAQ Schema Deployment

Deploying FAQPage JSON-LD schema for a page that already has FAQ content.

## When to Use

- Page has `<details>` or accordion-style FAQ section
- Site owner wants rich results in Google search (expanded Q&A)
- Part of SEO automation after site build

## Prerequisite

FAQ content must already exist on the page. Extract the Q&A pairs from the HTML:

```bash
# Find FAQ questions and answers in the page
grep -A1 'faq-item\|faq_q\|faq_a' index.html | grep -oP '(?<=>)[^<]+(?=</summary>|</p>)'
```

## Template

Insert in `<head>` before `</head>`, after the existing Organization/LocalBusiness JSON-LD:

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "QUESTION_TEXT",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "ANSWER_TEXT"
      }
    }
  ]
}
</script>
```

## Deployment Script

```python
#!/usr/bin/env python3
"""Insert FAQPage schema before </head> in index.html"""
faq_json = '''<script type="application/ld+json">
{...FAQPage JSON...}
</script>
'''

with open('/var/www/PATH/index.html', 'r') as f:
    content = f.read()

content = content.replace('</head>', faq_json + '\n</head>')

with open('/var/www/PATH/index.html', 'w') as f:
    f.write(content)
```

Upload via SCP and run:

```bash
scp insert_faq.py root@VPS:/tmp/
ssh root@VPS "cp /var/www/PATH/index.html /var/www/PATH/index.html.bak-faq && python3 /tmp/insert_faq.py"
```

## Validation

```bash
# Check FAQPage appears exactly once
grep -c 'FAQPage' /var/www/PATH/index.html  # Expected: 1

# Validate with Schema.org
curl -sI https://DOMAIN/  # Should be 200

# Then open: https://validator.schema.org/#url=https://DOMAIN/
# Check: FAQPage - 0 errors, 0 warnings
```

## Caveats

- Q&A text must match visible page content exactly — mismatch triggers Google "misleading" penalty
- Use the page's canonical language (x-default)
- 3-8 Q&A pairs optimal; too many dilutes weight
- Do NOT include `</script>` inside answer text — it will break the HTML

## Real Example (singxai.tech, 2026-06-23)

5 Q&A pairs extracted from the Chinese FAQ section, rendered in English (canonical language):

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {"@type": "Question", "name": "Can you really build a website in 3 days?", "acceptedAnswer": {"@type": "Answer", "text": "Yes. Standard sites delivered in 3 working days. Complex features like AI chatbot and membership system take 5-7 days for Pro/Custom plans."}},
    {"@type": "Question", "name": "What if I'm not satisfied?", "acceptedAnswer": {"@type": "Answer", "text": "Full refund. Pay 50% upfront, the rest after you're happy. We revise until you say OK with no extra charges."}},
    {"@type": "Question", "name": "What's included in the monthly fee?", "acceptedAnswer": {"@type": "Answer", "text": "Hosting, SSL certificate, domain assistance, regular maintenance, and AI chatbot quota."}},
    {"@type": "Question", "name": "I don't have a domain name. What do I do?", "acceptedAnswer": {"@type": "Answer", "text": "We help you register one. .com and .tech are recommended. Domain fees cost approximately RM50-80 per year, paid directly to the registrar."}},
    {"@type": "Question", "name": "What can the AI chatbot do?", "acceptedAnswer": {"@type": "Answer", "text": "Answer customer questions, auto-quote, guide orders, and collect customer information. 24/7 online, trained specifically on your business."}}
  ]
}
```

Validation result: Schema.org validator — 0 errors, 0 warnings for FAQPage.
