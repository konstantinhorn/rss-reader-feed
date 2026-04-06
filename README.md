# RSS Leseliste

Persönlicher RSS-Feed für Artikel aus der Leseliste.

**Feed-URL:** `https://konstantinhorn.github.io/rss-reader-feed/feed.xml`

## Wie es funktioniert

- Neue `.md` Dateien werden per Skript in `articles/` gepusht
- GitHub Actions generiert automatisch `feed.xml`
- Artikel die älter als 30 Tage sind, werden täglich automatisch gelöscht
- GitHub Pages hostet den Feed unter obiger URL
