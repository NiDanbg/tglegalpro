"""Файловете за откриване: robots.txt, sitemap.xml, llms.txt, llms-full.txt и RSS."""
import re
from datetime import date
from email.utils import format_datetime
from datetime import datetime, timezone
from html import escape

import render as R

# Търсачки и ИИ системи, които се допускат изрично. Правилото "*" така или иначе
# разрешава всички, но изричният списък не оставя съмнение и лесно се променя.
AI_CRAWLERS = [
    'GPTBot', 'OAI-SearchBot', 'ChatGPT-User',
    'ClaudeBot', 'Claude-User', 'Claude-SearchBot',
    'PerplexityBot', 'Perplexity-User',
    'Google-Extended', 'Applebot-Extended', 'Meta-ExternalAgent', 'Amazonbot', 'DuckAssistBot', 'MistralAI-User',
]


def robots(site):
    groups = ''.join(f'User-agent: {bot}\nAllow: /\n\n' for bot in AI_CRAWLERS)
    return (f"User-agent: *\nAllow: /\n\n{groups}"
            f"Sitemap: https://{site['domain']}/sitemap.xml\n")


def sitemap(site, entries):
    """entries: (език, slug, дата или None). Всяка страница посочва и версията си на другия език."""
    known = {(lang, slug) for lang, slug, _ in entries}
    rows = []
    for lang, slug, lastmod in entries:
        alts = ''
        for other in R.LANGS:
            if (other, slug) in known:
                alts += (f'    <xhtml:link rel="alternate" hreflang="{other}" '
                         f'href="{R.abs_url(site, other, slug)}"/>\n')
        mod = f'    <lastmod>{lastmod}</lastmod>\n' if lastmod else ''
        rows.append(f'  <url>\n    <loc>{R.abs_url(site, lang, slug)}</loc>\n{mod}{alts}  </url>\n')
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
            'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + ''.join(rows) + '</urlset>\n')


def _facts(ctx):
    s, c = ctx.site, ctx.site['contact']
    lines = [f"- {ctx.ui['address']}: {ctx.t(c['address'])}",
             f"- {ctx.ui['hours']}: {ctx.t(c['hours'])}",
             f"- {ctx.ui['email']}: " + ', '.join(m for m in (c.get('email'), c.get('email2')) if m)]
    if c.get('phone'):
        lines.append(f"- {ctx.ui['phone']}: {c['phone']}")
    lines.append(f"- {ctx.t(s['firm']['bar'])}")
    return '\n'.join(lines)


def _section(ctx):
    """Един език от llms.txt: кратко описание и връзки към страниците."""
    s, ui, lang = ctx.site, ctx.ui, ctx.lang
    pages = [
        (ui['nav_about'], 'about', ctx.t(s['seo']['about'])),
        (ui['nav_services'], 'services', ctx.t(s['seo']['services'])),
        (ui['nav_contact'], 'contact', ctx.t(s['seo']['contact'])),
    ]
    out = [f"## {ctx.t(s['firm']['name'])}\n\n{ctx.t(s['seo']['home'])}\n\n{_facts(ctx)}\n"]
    out.append(f"### {ui['nav_about']}, {ui['nav_services']}, {ui['nav_contact']}\n")
    out += [f"- [{name}]({R.abs_url(s, lang, slug)}): {desc}" for name, slug, desc in pages]
    if ctx.live:
        out.append(f"\n### {ui['nav_articles']}\n")
        out += [f"- [{ctx.t(a['title'])}]({R.abs_url(s, lang, 'articles/' + a['id'])}): {ctx.t(a.get('excerpt'))}"
                for a in ctx.live]
    return '\n'.join(out)


def llms(site, articles):
    bg, en = R.Ctx(site, articles, 'bg'), R.Ctx(site, articles, 'en')
    return (f"# {bg.t(site['firm']['name'])} ({en.t(site['firm']['name'])})\n\n"
            f"> {bg.t(site['seo']['home'])}\n> {en.t(site['seo']['home'])}\n\n"
            f"{_section(bg)}\n\n{_section(en)}\n\n"
            f"## Optional\n\n- [Full text of the site](https://{site['domain']}/llms-full.txt)\n")


def _full(ctx):
    s, lang = ctx.site, ctx.lang
    out = [_section(ctx).split('\n### ')[0]]
    out.append(f"\n## {ctx.t(s['about']['title'])}\n\n{ctx.t(s['about']['text'])}")
    out.append(f"\n## {ctx.t(s['about']['team_title'])}\n")
    for p in s['team']:
        bio = ctx.t(p.get('bio'))
        out.append(f"### {ctx.t(p['name'])}\n\n{ctx.t(p.get('role'))}" + (f"\n\n{bio}" if bio else '') + '\n')
    out.append(f"## {ctx.t(s['services_page']['title'])}\n")
    for a in s['services']:
        items = '\n'.join(f'- {i.strip()}' for i in ctx.t(a.get('items')).split('\n') if i.strip())
        out.append(f"### {ctx.t(a['title'])}\n\n{ctx.t(a['summary'])}\n\n{items}\n")
    faq = [q for q in s.get('faq', []) if ctx.t(q.get('q')) and ctx.t(q.get('a'))]
    if faq:
        out.append(f"## {ctx.ui['faq']}\n")
        out += [f"### {ctx.t(q['q'])}\n\n{ctx.t(q['a'])}\n" for q in faq]
    for art in ctx.live:
        link = R.abs_url(s, lang, 'articles/' + art['id'])
        out.append(f"## {ctx.t(art['title'])}\n\n{link}, {art.get('date', '')}\n\n{ctx.t(art.get('body'))}\n")
    return '\n'.join(out)


def llms_full(site, articles):
    bg, en = R.Ctx(site, articles, 'bg'), R.Ctx(site, articles, 'en')
    return f"# {bg.t(site['firm']['name'])}\n\n{_full(bg)}\n\n---\n\n{_full(en)}\n"


def rss(ctx):
    s, lang = ctx.site, ctx.lang
    items = ''
    for art in ctx.live[:30]:
        link = R.abs_url(s, lang, 'articles/' + art['id'])
        when = ''
        if re.fullmatch(r'\d{4}-\d{2}-\d{2}', art.get('date', '')):
            d = date.fromisoformat(art['date'])
            stamp = datetime(d.year, d.month, d.day, tzinfo=timezone.utc)
            when = f'<pubDate>{format_datetime(stamp)}</pubDate>'
        items += (f'<item><title>{escape(ctx.t(art["title"]))}</title><link>{link}</link>'
                  f'<guid>{link}</guid>{when}<description>{escape(ctx.t(art.get("excerpt")))}</description></item>\n')
    home = R.abs_url(s, lang)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel>'
            f'<title>{escape(ctx.t(s["firm"]["name"]))}</title><link>{home}</link>'
            f'<description>{escape(ctx.t(s["seo"]["articles"]))}</description><language>{lang}</language>\n'
            f'{items}</channel></rss>\n')
