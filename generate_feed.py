#!/usr/bin/env python3
"""Generates feed.xml from all .md files in articles/"""
import os
import subprocess
import re
from datetime import datetime, timezone
from email.utils import format_datetime

FEED_TITLE = "Leseliste"
FEED_DESCRIPTION = "Artikel aus der persönlichen Leseliste"
GITHUB_USER = "konstantinhorn"
REPO_NAME = "rss-reader-feed"
FEED_LINK = f"https://{GITHUB_USER}.github.io/{REPO_NAME}/"
FEED_URL = f"https://{GITHUB_USER}.github.io/{REPO_NAME}/feed.xml"
ARTICLES_DIR = "articles"


def get_first_commit_date(filepath):
    """Get date when file was first committed (added) to the repo."""
    result = subprocess.run(
        ["git", "log", "--follow", "--diff-filter=A", "--format=%aI", "--", filepath],
        capture_output=True, text=True
    )
    lines = [l.strip() for l in result.stdout.strip().split('\n') if l.strip()]
    if lines:
        try:
            return datetime.fromisoformat(lines[-1])
        except Exception:
            pass
    return datetime.now(timezone.utc)


def extract_title(content, filename):
    """Extract first H1 heading or use filename as title."""
    for line in content.split('\n'):
        line = line.strip()
        if line.startswith('# '):
            return line[2:].strip()
    return os.path.splitext(os.path.basename(filename))[0]


def xml_escape(text):
    return (text
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;'))


def md_to_html(content):
    """Convert markdown to basic HTML for RSS readers."""
    lines = content.split('\n')
    html = []
    in_code = False

    for line in lines:
        if line.startswith('```'):
            if in_code:
                html.append('</code></pre>')
            else:
                lang = line[3:].strip()
                html.append(f'<pre><code class="language-{xml_escape(lang)}">' if lang else '<pre><code>')
            in_code = not in_code
            continue

        if in_code:
            html.append(xml_escape(line))
            continue

        if line.startswith('### '):
            html.append(f'<h3>{xml_escape(line[4:])}</h3>')
        elif line.startswith('## '):
            html.append(f'<h2>{xml_escape(line[3:])}</h2>')
        elif line.startswith('# '):
            html.append(f'<h1>{xml_escape(line[2:])}</h1>')
        elif line.startswith('> '):
            html.append(f'<blockquote><p>{xml_escape(line[2:])}</p></blockquote>')
        elif line.startswith('- ') or line.startswith('* '):
            html.append(f'<li>{xml_escape(line[2:])}</li>')
        elif line.strip() == '':
            html.append('')
        else:
            text = xml_escape(line)
            text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
            text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
            text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
            text = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', text)
            html.append(f'<p>{text}</p>')

    return '\n'.join(html)


def generate():
    if not os.path.exists(ARTICLES_DIR):
        print("No articles directory found.")
        return

    items = []
    for filename in sorted(os.listdir(ARTICLES_DIR)):
        if not filename.endswith('.md'):
            continue
        filepath = os.path.join(ARTICLES_DIR, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        date = get_first_commit_date(filepath)
        title = extract_title(content, filename)
        html_content = md_to_html(content)

        items.append((date, title, html_content, filename))

    # Newest first
    items.sort(key=lambda x: x[0], reverse=True)

    now_str = format_datetime(datetime.now(timezone.utc))

    xml_items = []
    for date, title, html_content, filename in items:
        pub_date = format_datetime(date)
        # Use CDATA to avoid escaping issues; replace any ]]> in content
        safe_html = html_content.replace(']]>', ']]&gt;')
        xml_items.append(f"""  <item>
    <title>{xml_escape(title)}</title>
    <link>{FEED_LINK}</link>
    <guid isPermaLink="false">{xml_escape(filename)}</guid>
    <pubDate>{pub_date}</pubDate>
    <description><![CDATA[{safe_html}]]></description>
    <content:encoded><![CDATA[{safe_html}]]></content:encoded>
  </item>""")

    items_xml = '\n'.join(xml_items)
    feed_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"
  xmlns:content="http://purl.org/rss/1.0/modules/content/"
  xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>{FEED_TITLE}</title>
    <link>{FEED_LINK}</link>
    <description>{FEED_DESCRIPTION}</description>
    <language>de</language>
    <lastBuildDate>{now_str}</lastBuildDate>
    <atom:link href="{FEED_URL}" rel="self" type="application/rss+xml"/>
{items_xml}
  </channel>
</rss>"""

    with open('feed.xml', 'w', encoding='utf-8') as f:
        f.write(feed_xml)

    print(f"Generated feed.xml with {len(items)} article(s)")


if __name__ == '__main__':
    generate()
