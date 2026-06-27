# Install

## Option 1: Direct Copy

```bash
git clone https://github.com/remix2111/singx-hermes-skills.git
cp -r singx-hermes-skills/skills/* ~/.hermes/skills/
```

Then load in Hermes session: `/skill singx-security-hardening` or `/skill singx-seo-specialist`

## Option 2: Hermes Skills Hub (coming soon)

```bash
hermes skills install singx-security-hardening
hermes skills install singx-seo-specialist
```

## Option 3: Symlink (dev mode)

```bash
ln -s $(pwd)/singx-hermes-skills/skills/singx-security-hardening ~/.hermes/skills/web-development/singx-security-hardening
ln -s $(pwd)/singx-hermes-skills/skills/singx-seo-specialist ~/.hermes/skills/seo/singx-seo-specialist
```
