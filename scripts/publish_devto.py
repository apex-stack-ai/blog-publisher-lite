#!/usr/bin/env python3
"""
Publish a markdown article to Dev.to via their REST API.

Usage:
  python publish_devto.py <markdown_file> --api-key <key> [--publish] [--tags tag1,tag2]

The script parses the markdown file to extract:
- Title (from first # heading)
- Tags (from *Tags: ...* line)
- Body (everything after the --- separator)

Blog Publisher Lite by Apex Stack â https://apexstack.gumroad.com
"""

import argparse
import json
import sys
import urllib.request
import urllib.error


def parse_article(filepath: str) -> dict:
    """Parse a markdown file into title, tags, and body."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.split("\n")
    title = ""
    tags = []
    body_lines = []
    found_separator = False
    metadata_zone = True

    for line in lines:
        if line.startswith("# ") and not title:
            title = line[2:].strip()
            continue

        if line.startswith("*Tags:") and metadata_zone:
            tag_str = line.replace("*Tags:", "").replace("*", "").strip()
            tags = [t.strip().lower().replace(" ", "") for t in tag_str.split(",")]
            continue

        if metadata_zone and (line.startswith("*Read time:") or line.startswith("*CTA:")):
            continue

        if line.strip() == "---" and metadata_zone:
            found_separator = True
            metadata_zone = False
            continue

        if not metadata_zone:
            body_lines.append(line)

    if not found_separator:
        body_lines = []
        past_title = False
        for line in lines:
            if line.startswith("# ") and not past_title:
                past_title = True
                continue
            if past_title:
                body_lines.append(line)

    body = "\n".join(body_lines).strip()
    return {"title": title, "tags": tags[:4], "body": body}


def publish(article: dict, api_key: str, published: bool = False) -> dict:
    """Publish article to Dev.to API."""
    payload = {
        "article": {
            "title": article["title"],
            "published": published,
            "body_markdown": article["body"],
            "tags": article["tags"],
        }
    }

    data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        "https://dev.to/api/articles",
        data=data,
        headers={
            "api-key": api_key,
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode("utf-8"))
            return {
                "success": True,
                "url": result.get("url", ""),
                "id": result.get("id", ""),
                "title": result.get("title", ""),
                "published": result.get("published", False),
            }
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        return {
            "success": False,
            "status": e.code,
            "error": error_body,
        }


def main():
    parser = argparse.ArgumentParser(description="Publish markdown article to Dev.to")
    parser.add_argument("file", help="Path to markdown file")
    parser.add_argument("--api-key", required=True, help="Dev.to API key")
    parser.add_argument("--publish", action="store_true", help="Publish immediately (default: draft)")
    parser.add_argument("--tags", help="Comma-separated tags (overrides file tags)")

    args = parser.parse_args()

    article = parse_article(args.file)

    if args.tags:
        article["tags"] = [t.strip().lower() for t in args.tags.split(",")][:4]

    print(f"Title: {article['title']}")
    print(f"Tags: {article['tags']}")
    print(f"Body length: {len(article['body'])} chars")
    print(f"Publishing: {'immediately' if args.publish else 'as draft'}")
    print()

    result = publish(article, args.api_key, published=args.publish)

    if result["success"]:
        print(f"Published successfully!")
        print(f"URL: {result['url']}")
        print(f"ID: {result['id']}")
        print(f"Status: {'Published' if result['published'] else 'Draft'}")
    else:
        print(f"Failed to publish!")
        print(f"Status: {result.get('status')}")
        print(f"Error: {result.get('error')}")
        sys.exit(1)

    print(f"\n--- JSON ---")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
