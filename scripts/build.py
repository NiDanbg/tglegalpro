#!/usr/bin/env python3
"""Генератор на статичния сайт. Чете content/ и пише готовите страници в dist/.
Употреба: python scripts/build.py"""
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import discovery as D
import render as R

BASE = Path(__file__).resolve().parent.parent
DIST = BASE / 'dist'


def load():
    site = json.loads((BASE / 'content' / 'site.json').read_text(encoding='utf-8'))
    articles = []
    for path in sorted((BASE / 'content' / 'articles').glob('*.json')):
        art = json.loads(path.read_text(encoding='utf-8'))
        art['id'] = path.stem
        articles.append(art)
    articles.sort(key=lambda a: a.get('date', ''), reverse=True)
    return site, articles


def write(rel, html):
    target = DIST / rel / 'index.html' if rel else DIST / 'index.html'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(html, encoding='utf-8')


def clean_dist():
    """Изчиства съдържанието, без да трие самата папка: панелът може да я сервира в момента."""
    DIST.mkdir(exist_ok=True)
    for item in DIST.iterdir():
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()


def build():
    site, articles = load()
    clean_dist()
    shutil.copytree(BASE / 'assets', DIST / 'assets')
    shutil.copytree(BASE / 'images', DIST / 'images')

    entries = []
    for lang in R.LANGS:
        ctx = R.Ctx(site, articles, lang)
        pages = {
            '': R.page_home,
            'about': R.page_about,
            'services': R.page_services,
            'contact': R.page_contact,
            'privacy': R.page_privacy,
            'legal-notice': R.page_notice,
        }
        for slug, fn in pages.items():
            write(R.rel_path(lang, slug), fn(ctx))
            entries.append((lang, slug, None))
        if ctx.live:
            write(R.rel_path(lang, 'articles'), R.page_articles(ctx))
            entries.append((lang, 'articles', ctx.live[0].get('date')))
            for art in ctx.live:
                slug = 'articles/' + art['id']
                write(R.rel_path(lang, slug), R.page_article(ctx, art))
                entries.append((lang, slug, art.get('updated') or art.get('date')))

    (DIST / '404.html').write_text(R.page_404(R.Ctx(site, articles, 'bg')), encoding='utf-8')
    (DIST / 'CNAME').write_text(site['domain'] + '\n', encoding='utf-8')
    (DIST / '.nojekyll').write_text('', encoding='utf-8')
    (DIST / 'robots.txt').write_text(D.robots(site), encoding='utf-8')
    (DIST / 'sitemap.xml').write_text(D.sitemap(site, entries), encoding='utf-8')
    (DIST / 'llms.txt').write_text(D.llms(site, articles), encoding='utf-8')
    (DIST / 'llms-full.txt').write_text(D.llms_full(site, articles), encoding='utf-8')
    for lang in R.LANGS:
        ctx = R.Ctx(site, articles, lang)
        if ctx.live:
            target = DIST / R.rel_path(lang, 'feed.xml')
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(D.rss(ctx), encoding='utf-8')
    print(f'Готово: {len(entries)} страници в dist/')
    return len(entries)


if __name__ == '__main__':
    build()
