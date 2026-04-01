#!/usr/bin/env python3
"""Extrahiert Text-Content aus den alten HTML-Seiten und erzeugt Markdown-Dateien für 11ty."""

import re
import os
from pathlib import Path
from html import unescape

# Pfade
BASE = Path(__file__).parent
OLD_PAGES = BASE  # Alte HTML-Dateien liegen im Repo-Root
SRC_PAGES = BASE / "src" / "pages"
SRC_PAGES.mkdir(parents=True, exist_ok=True)

# Bereits manuell erstellte Seiten — nicht überschreiben
SKIP = {"hotel", "impressum", "kontakt", "gasthaus", "brauerei", "datenschutz"}

# Header-Bilder (manuell zugeordnet)
HEADER_IMAGES = {
    "brauerei": "/img/bier-header_1.jpg",
    "gasthaus": "/img/header_01.jpg",
    "erlebnishotel": "/img/header_01.jpg",
    "seminar": "/img/bienenstock_header.jpg",
    "feiern-geniessen": "/img/hochzeiten-slider-4.jpg",
    "hochzeiten": "/img/hochzeiten-slider-4.jpg",
    "veranstaltungssaele": "/img/braustube_header.jpg",
    "zimmer-preise": "/img/header_01.jpg",
}

# Zimmer-Header-Bilder
ZIMMER_HEADERS = {
    "bauernzimmer": "/img/bauernzimmer-header-1.jpg",
    "heustadlzimmer": "/img/heustadlzimmer_header.jpg",
    "erotikzimmer": "/img/erotikzimmer_header.jpg",
    "bienenstock": "/img/bienenstock_header.jpg",
    "braustube": "/img/braustube_header.jpg",
    "hochzeitszimmer": "/img/hochzeiten-slider-4.jpg",
    "bierbad-fuer-zwei": "/img/bierbad-header_01.jpg",
    "candle-light-dinner": "/img/candle-light-header_01.jpg",
}


def strip_tags(html):
    """Entferne HTML-Tags, behalte Text."""
    # Inline-Styles und Scripts entfernen
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    # Kommentare entfernen
    html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)
    # <br> → Zeilenumbruch
    html = re.sub(r'<br\s*/?>', '\n', html)
    # </p>, </div>, </h*> → doppelter Umbruch
    html = re.sub(r'</(?:p|div|h[1-6]|li|tr|section|article)>', '\n\n', html)
    # <h1>...<h6> → Markdown-Heading
    for i in range(1, 7):
        html = re.sub(rf'<h{i}[^>]*>', f'\n\n{"#" * i} ', html)
    # <li> → Bullet
    html = re.sub(r'<li[^>]*>', '- ', html)
    # <a href="...">text</a> → [text](href)
    html = re.sub(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>',
                  lambda m: f'[{strip_tags(m.group(2))}]({m.group(1)})', html)
    # <strong>/<b> → **text**
    html = re.sub(r'<(?:strong|b)[^>]*>(.*?)</(?:strong|b)>',
                  lambda m: f'**{m.group(1)}**', html, flags=re.DOTALL)
    # <em>/<i> → *text*
    html = re.sub(r'<(?:em|i)[^>]*>(.*?)</(?:em|i)>',
                  lambda m: f'*{m.group(1)}*', html, flags=re.DOTALL)
    # Restliche Tags entfernen
    html = re.sub(r'<[^>]+>', '', html)
    # HTML entities
    html = unescape(html)
    # Mehrere Leerzeilen → max 2
    html = re.sub(r'\n{3,}', '\n\n', html)
    # Whitespace am Zeilenanfang/Ende bereinigen
    lines = [line.strip() for line in html.split('\n')]
    html = '\n'.join(lines)
    # Nochmal mehrere Leerzeilen
    html = re.sub(r'\n{3,}', '\n\n', html)
    return html.strip()


def extract_title(html):
    """Extrahiere Seitentitel."""
    m = re.search(r'<title[^>]*>(.*?)</title>', html, re.DOTALL)
    if m:
        title = m.group(1).strip()
        # "Hotel — Steirisch Ursprung" → "Hotel"
        title = re.sub(r'\s*[–—|]\s*Steirisch.*$', '', title).strip()
        title = re.sub(r'\s*[–—|]\s*$', '', title).strip()
        return title if title else None
    return None


def extract_content(html):
    """Extrahiere den Hauptinhalt."""
    # Suche nach <main>...</main>
    m = re.search(r'<main[^>]*>(.*?)</main>', html, re.DOTALL)
    if m:
        content = m.group(1)
        # Container-Wrapper entfernen
        content = re.sub(r'<div class="container">\s*', '', content)
        return strip_tags(content)

    # Fallback: Content nach Navbar, vor Footer
    m = re.search(r'</nav>(.*?)<footer', html, re.DOTALL)
    if m:
        return strip_tags(m.group(1))

    return ""


def find_pages():
    """Finde alle alten Seiten."""
    pages = []

    # Top-level Seiten
    for d in sorted(OLD_PAGES.iterdir()):
        if d.is_dir() and (d / "index.html").exists():
            name = d.name
            if name.startswith(('_', '.', 'src', 'node_modules', 'assets')):
                continue
            if name in SKIP:
                continue
            pages.append((name, d / "index.html", f"/{name}/"))

    # Zimmer-und-Angebote Unterseiten
    zua = OLD_PAGES / "zimmer-und-angebote"
    if zua.is_dir():
        for d in sorted(zua.iterdir()):
            if d.is_dir() and (d / "index.html").exists():
                name = d.name
                pages.append((f"zimmer-und-angebote/{name}",
                             d / "index.html",
                             f"/zimmer-und-angebote/{name}/"))

    return pages


def main():
    pages = find_pages()
    created = 0

    for slug, html_path, permalink in pages:
        html = html_path.read_text(encoding="utf-8", errors="replace")
        title = extract_title(html) or slug.split("/")[-1].replace("-", " ").title()
        content = extract_content(html)

        if not content or len(content) < 20:
            print(f"  SKIP (kein Content): {slug}")
            continue

        # Content bereinigen
        # 1. Führende H1 entfernen wenn sie dem Titel entspricht
        title_clean = re.sub(r'[^\w\s]', '', title.lower().strip())
        lines = content.split('\n')
        cleaned_lines = []
        title_removed = False
        for line in lines:
            # Erste H1/H2 die dem Titel ähnelt → entfernen
            if not title_removed and re.match(r'^#{1,2}\s+', line):
                heading_text = re.sub(r'^#{1,2}\s+', '', line).strip()
                heading_clean = re.sub(r'[^\w\s]', '', heading_text.lower().strip())
                if heading_clean == title_clean or heading_clean in title_clean or title_clean in heading_clean:
                    title_removed = True
                    continue
            cleaned_lines.append(line)
        content = '\n'.join(cleaned_lines)

        # 2. Leere Listen entfernen
        content = re.sub(r'-\s*\n', '', content)
        content = re.sub(r'\n{3,}', '\n\n', content)

        # 3. Kaputte Markdown-Artefakte bereinigen
        content = re.sub(r'\*\[?\*\*\]?\([^)]*\)', '', content)  # *[**](/url)
        content = re.sub(r'^\*\*$', '', content, flags=re.MULTILINE)  # alleinstehende **
        content = re.sub(r'^\*$', '', content, flags=re.MULTILINE)  # alleinstehende *
        content = re.sub(r'\n{3,}', '\n\n', content)

        # 4. HTML-Entities im Content dekodieren
        content = unescape(content)

        # 5. Unicode-Normalisierung (Soft-Hyphens, fancy Apostrophe)
        content = content.replace('\u00ad', '')  # Soft-Hyphen entfernen
        content = content.replace('\u2019', "'")  # Right Single Quotation → normaler Apostroph
        content = content.replace('\u2018', "'")  # Left Single Quotation
        content = content.replace('\u201c', '"')  # Left Double Quotation
        content = content.replace('\u201d', '"')  # Right Double Quotation

        content = content.strip()
        if not content or len(content) < 10:
            print(f"  SKIP (nach Bereinigung leer): {slug}")
            continue

        # Titel: Entities dekodieren
        title = unescape(title)
        # Anführungszeichen escapen für YAML
        title_yaml = title.replace('"', '\\"')

        # Frontmatter
        frontmatter = f'---\ntitle: "{title_yaml}"\npermalink: {permalink}\n'

        # Header-Bild zuordnen
        short = slug.split("/")[-1]
        if short in HEADER_IMAGES:
            frontmatter += f'headerImage: {HEADER_IMAGES[short]}\n'
        elif short in ZIMMER_HEADERS:
            frontmatter += f'headerImage: {ZIMMER_HEADERS[short]}\n'

        frontmatter += '---\n\n'

        # Markdown-Datei schreiben
        md_name = slug.replace("/", "--") + ".md"
        md_path = SRC_PAGES / md_name
        md_path.write_text(frontmatter + content, encoding="utf-8")
        created += 1
        print(f"  OK: {slug} → {md_name} ({len(content)} chars)")

    print(f"\n  {created} Markdown-Dateien erstellt in {SRC_PAGES}")


if __name__ == "__main__":
    main()
