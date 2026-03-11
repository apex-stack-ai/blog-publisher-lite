---
name: blog-publisher-lite
description: "Publish markdown articles to Dev.to via their REST API. Use this skill whenever the user wants to publish a blog post or article to Dev.to. Triggers include: posting to Dev.to, publishing articles, 'publish my article', 'post this on dev.to', or any mention of publishing written content to Dev.to. Also trigger when user has markdown content they want published on a developer blogging platform."
---

# Blog Publisher Lite

Publish markdown articles to **Dev.to** â the largest developer blogging platform â directly from a markdown file using their REST API.

> **Want cross-posting to Medium and Hashnode too?** Upgrade to [Blog Cross-Publisher (Full)](https://apexstack.gumroad.com) for canonical URL management, Hashnode GraphQL integration, Medium browser automation, and platform-specific tag mapping.

## What You Need

A Dev.to API key. Get one in 30 seconds:
1. Go to https://dev.to/settings/extensions
2. Scroll to "DEV Community API Keys"
3. Enter a description, click "Generate API Key"
4. Copy the key

## Article Format

Write your article in standard markdown with optional metadata at the top:

```markdown
# Your Article Title

*Tags: javascript, webdev, programming, ai*
*Read time: ~5 min*

---

Your article body starts here. Standard markdown works: **bold**, *italic*,
[links](https://example.com), code blocks, images, and headings.

## A Section Heading

More content...
```

The skill extracts the title from the first `# heading`, tags from the `*Tags:*` line, and everything after `---` becomes the body.

## Publishing

Use the bundled script:

```bash
python scripts/publish_devto.py article.md \
  --api-key YOUR_API_KEY \
  --publish
```

| Flag | What It Does |
|------|-------------|
| `--publish` | Publish immediately (omit for draft) |
| `--tags "seo,webdev"` | Override tags from the file |

The script outputs the published URL and article ID as JSON.

## API Details

```
POST https://dev.to/api/articles
Header: api-key: <key>
Header: Content-Type: application/json
```

Payload:
```json
{
  "article": {
    "title": "Article Title",
    "published": true,
    "body_markdown": "Full markdown body",
    "tags": ["seo", "webdev", "programming", "ai"]
  }
}
```

**Constraints:** Max 4 tags, lowercase, no spaces (use hyphens). Dev.to auto-generates a slug from the title.

## Updating an Existing Article

```
PUT https://dev.to/api/articles/{id}
```

Same payload structure. Use the article `id` from the original publish response.

## Network Restrictions

If `curl` or `urllib` fails with connection errors in sandboxed environments, use browser JavaScript `fetch()` as a workaround:

```javascript
fetch('https://dev.to/api/articles', {
  method: 'POST',
  headers: {
    'api-key': 'YOUR_KEY',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    article: {
      title: 'Your Title',
      published: false,
      body_markdown: 'Your content...',
      tags: ['seo', 'webdev']
    }
  })
}).then(r => r.json()).then(console.log)
```

## Troubleshooting

### 401 Unauthorized
API key invalid or expired. Generate a new one at https://dev.to/settings/extensions

### 422 Unprocessable Entity
Check: title is present, tags â¤ 4, body_markdown is valid, no duplicate draft with same title.

### 429 Too Many Requests
Rate limited. Wait 30 seconds and retry.

---

*Built by [Apex Stack](https://apexstack.gumroad.com) â tools for developers who ship.*
