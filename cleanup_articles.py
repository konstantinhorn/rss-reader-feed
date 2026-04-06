#!/usr/bin/env python3
"""Deletes articles older than MAX_AGE_DAYS from the articles/ folder."""
import os
import subprocess
from datetime import datetime, timezone, timedelta

ARTICLES_DIR = "articles"
MAX_AGE_DAYS = 30


def get_first_commit_date(filepath):
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


def cleanup():
    if not os.path.exists(ARTICLES_DIR):
        print("No articles directory found.")
        return 0

    cutoff = datetime.now(timezone.utc) - timedelta(days=MAX_AGE_DAYS)
    deleted = []

    for filename in sorted(os.listdir(ARTICLES_DIR)):
        if not filename.endswith('.md'):
            continue
        filepath = os.path.join(ARTICLES_DIR, filename)
        commit_date = get_first_commit_date(filepath)

        if commit_date < cutoff:
            os.remove(filepath)
            deleted.append((filename, commit_date))
            print(f"  Deleted: {filename} (added {commit_date.strftime('%Y-%m-%d')})")

    if deleted:
        print(f"\nRemoved {len(deleted)} article(s) older than {MAX_AGE_DAYS} days.")
    else:
        print("No articles older than 30 days found.")

    return len(deleted)


if __name__ == '__main__':
    cleanup()
