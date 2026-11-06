"""HTML шаблоните на сайта. Целият изглед е тук и в assets/site.css."""
import html
import json
import re
from datetime import date
from urllib.parse import quote

import markdown_lite as MD

LANGS = ['bg', 'en']

UI = {
    'bg': {
        'nav_about': 'За дружеството', 'nav_services': 'Области на практика', 'nav_articles': 'Статии',
        'nav_contact': 'Контакти', 'menu': 'Меню', 'other_lang': 'English', 'skip': 'Към съдържанието',
        'address': 'Адрес', 'hours': 'Работно време', 'phone': 'Телефон', 'email': 'Имейл',
        'map': 'Отворете в Google Maps', 'map_hero': 'Намерете ни в Google Maps', 'contact_us': 'Изпратете запитване',
        'form_name': 'Име', 'form_email': 'Имейл', 'form_message': 'Вашият въпрос',
        'form_consent': 'Запознах се с', 'form_consent_link': 'политиката за лични данни',
        'form_send': 'Изпратете запитването', 'form_sending': 'Изпращане…',
        'form_ok': 'Запитването е изпратено. Ще Ви отговорим по имейл.',
        'form_err': 'Запитването не беше изпратено. Опитайте отново или ни пишете на {email}.',
        'latest': 'Последни статии', 'all_articles': 'Всички статии', 'read': 'Прочетете статията',
        'by': 'Автор:', 'back': 'Всички статии', 'more_about': 'Повече за дружеството',
        'not_found': 'Тази страница не съществува', 'not_found_text': 'Адресът може да е променен. Върнете се към началната страница.',
        'home': 'Към началната страница', 'privacy': 'Политика за лични данни', 'notice': 'Правна информация', 'faq': 'Често задавани въпроси',
        'months': ['януари', 'февруари', 'март', 'април', 'май', 'юни', 'юли', 'август', 'септември',
                   'октомври', 'ноември', 'декември'],
    },
    'en': {
        'nav_about': 'About the firm', 'nav_services': 'Practice areas', 'nav_articles': 'Articles',
        'nav_contact': 'Contact', 'menu': 'Menu', 'other_lang': 'Български', 'skip': 'Skip to content',
        'address': 'Address', 'hours': 'Office hours', 'phone': 'Phone', 'email': 'Email',
        'map': 'Open in Google Maps', 'map_hero': 'Find us on Google Maps', 'contact_us': 'Send an enquiry',
        'form_name': 'Name', 'form_email': 'Email', 'form_message': 'Your question',
        'form_consent': 'I have read the', 'form_consent_link': 'privacy policy',
        'form_send': 'Send the enquiry', 'form_sending': 'Sending…',
        'form_ok': 'Your enquiry has been sent. We will reply by email.',
        'form_err': 'Your enquiry was not sent. Please try again or write to {email}.',
        'latest': 'Latest articles', 'all_articles': 'All articles', 'read': 'Read the article',
        'by': 'By', 'back': 'All articles', 'more_about': 'More about the firm',
        'not_found': 'This page does not exist', 'not_found_text': 'The address may have changed. Return to the home page.',
        'home': 'Go to the home page', 'privacy': 'Privacy policy', 'notice': 'Legal notice', 'faq': 'Frequently asked questions',
        'months': ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September',
                   'October', 'November', 'December'],
    },
}

esc = lambda s: html.escape(str(s or ''), quote=True)


class Ctx:
    def __init__(self, site, articles, lang):
        self.site, self.lang, self.ui = site, lang, UI[lang]
        self.all_articles = articles
        self.live = [a for a in articles
                     if a.get('published') and a.get('title', {}).get(lang, '').strip()]

    def t(self, node):
        """Текстът на текущия език. Ако липсва превод, се ползва другият език."""
        if isinstance(node, dict):
            other = 'en' if self.lang == 'bg' else 'bg'
            return node.get(self.lang) or node.get(other) or ''
        return node or ''


def rel_path(lang, slug):
    prefix = '' if lang == 'bg' else 'en'
    return '/'.join(p for p in (prefix, slug) if p)


def url(lang, slug=''):
    rel = rel_path(lang, slug)
    return '/' + rel + '/' if rel else '/'


def abs_url(site, lang, slug=''):
    return f"https://{site['domain']}{url(lang, slug)}"


def nl_html(text):
    return ''.join(f'<p>{esc(c.strip())}</p>' for c in re.split(r'\n\s*\n', text or '') if c.strip())


def fmt_date(iso, lang):
    try:
        d = date.fromisoformat(iso)
    except (TypeError, ValueError):
        return ''
    month = UI[lang]['months'][d.month - 1]
    return f'{d.day} {month} {d.year} г.' if lang == 'bg' else f'{month} {d.day}, {d.year}'


def initials(name):
    parts = (name or '').split()
    if not parts:
        return ''
    return (parts[0][0] + parts[-1][0]).upper() if len(parts) > 1 else parts[0][0].upper()


def org_ld(ctx):
    """Описанието на дружеството, което търсачките и ИИ системите четат от всяка страница."""
    site, c, lang = ctx.site, ctx.site['contact'], ctx.lang
    base = f"https://{site['domain']}"
    data = {
        '@type': ['LegalService', 'LocalBusiness'], '@id': f'{base}/#firm',
        'name': ctx.t(site['firm']['name']),
        'alternateName': [site['firm']['name']['bg'], site['firm']['name']['en']],
        'description': ctx.t(site['seo']['home']),
        'url': abs_url(site, lang), 'email': c.get('email', ''),
        'image': f"{base}/{site['home']['hero_image']}",
        'address': {'@type': 'PostalAddress', 'streetAddress': ctx.t(c.get('street')),
                    'addressLocality': ctx.t(c.get('city')), 'addressCountry': 'BG'},
        'areaServed': {'@type': 'Country', 'name': 'България' if lang == 'bg' else 'Bulgaria'},
        'memberOf': {'@type': 'Organization', 'name': ctx.t(site['firm']['bar'])},
        'openingHoursSpecification': [{
            '@type': 'OpeningHoursSpecification',
            'dayOfWeek': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
            'opens': c.get('opens', ''), 'closes': c.get('closes', '')}],
        'employee': [{'@id': f"{base}/#{p['id']}"} for p in site['team']],
        'knowsAbout': [ctx.t(a['title']) for a in site['services']],
        'hasOfferCatalog': {'@type': 'OfferCatalog', 'name': ctx.t(site['services_page']['title']), 'itemListElement': [
            {'@type': 'Offer', 'itemOffered': {'@type': 'Service', 'name': ctx.t(a['title']), 'description': ctx.t(a['summary']),
                                               'url': abs_url(site, lang, 'services') + '#' + a['id']}}
            for a in site['services']]},
    }
    if c.get('phone'):
        data['telephone'] = c['phone']
    links = [u.strip() for u in (site.get('same_as') or '').split('\n') if u.strip()]
    if links:
        data['sameAs'] = links
    people = [{'@type': 'Person', '@id': f"{base}/#{p['id']}", 'name': ctx.t(p['name']), 'jobTitle': ctx.t(p.get('role')),
               'worksFor': {'@id': f'{base}/#firm'}, 'url': abs_url(site, lang, 'about') + '#' + p['id'],
               **({'image': f"{base}/{p['photo']}"} if p.get('photo') else {}),
               **({'description': ctx.t(p['bio'])} if ctx.t(p.get('bio')) else {})}
              for p in site['team']]
    website = {'@type': 'WebSite', '@id': f'{base}/#site', 'url': f'{base}/', 'name': ctx.t(site['firm']['name']),
               'inLanguage': LANGS, 'publisher': {'@id': f'{base}/#firm'}}
    return [data, website] + people


def crumbs_ld(ctx, trail):
    """trail: [(име, slug), ...] без началната страница."""
    items = [(ctx.t(ctx.site['firm']['name']), '')] + trail
    return {'@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': abs_url(ctx.site, ctx.lang, sl)}
        for i, (n, sl) in enumerate(items)]}


def ld_script(ctx, extra):
    graph = org_ld(ctx) + (extra or [])
    text = json.dumps({'@context': 'https://schema.org', '@graph': graph}, ensure_ascii=False)
    return text.replace('</', '<\\/')


def wordmark(ctx, tag='a'):
    f = ctx.site['firm']
    if f.get('logo'):
        inner = f'<img src="/{esc(f["logo"])}" alt="{esc(ctx.t(f["name"]))}">'
    else:
        inner = (f'<span class="wm-name">{esc(ctx.t(f["short_first"]))} <span class="wm-amp">&amp;</span> '
                 f'{esc(ctx.t(f["short_second"]))}</span>')
    return f'<a class="wordmark" href="{url(ctx.lang)}" aria-label="{esc(ctx.t(f["name"]))}">{inner}</a>'


def layout(ctx, slug, title, description, body, other_slug=None, active='', og_image=None, og_type='website',
           extra_ld=None, noindex=False, home_title=''):
    site, ui, lang = ctx.site, ctx.ui, ctx.lang
    other = 'en' if lang == 'bg' else 'bg'
    other_slug = slug if other_slug is None else other_slug
    firm = ctx.t(site['firm']['name'])
    full_title = f'{title} | {firm}' if title else (f'{firm} | {home_title}' if home_title else firm)
    canonical = abs_url(site, lang, slug)
    hreflang = ''
    if other_slug == slug:
        hreflang = (f'<link rel="alternate" hreflang="{lang}" href="{canonical}">'
                    f'<link rel="alternate" hreflang="{other}" href="{abs_url(site, other, slug)}">'
                    f'<link rel="alternate" hreflang="x-default" href="{abs_url(site, "bg", slug)}">')
    verify = ''
    for meta, key in (('google-site-verification', 'google_verification'), ('msvalidate.01', 'bing_verification')):
        if site.get(key):
            verify += f'<meta name="{meta}" content="{esc(site[key])}">\n'
    feed_href = '/' + rel_path(lang, 'feed.xml')
    feed = f'<link rel="alternate" type="application/rss+xml" title="{esc(firm)}" href="{feed_href}">\n' if ctx.live else ''
    robots = 'noindex' if noindex else 'index, follow, max-image-preview:large, max-snippet:-1'
    image = og_image or site['home']['hero_image']

    links = [('about', ui['nav_about']), ('services', ui['nav_services'])]
    if ctx.live:
        links.append(('articles', ui['nav_articles']))
    links.append(('contact', ui['nav_contact']))
    nav = ''.join(
        f'<a href="{url(lang, s)}"{" aria-current=\"page\"" if active == s else ""}>{esc(label)}</a>'
        for s, label in links)
    lang_link = (f'<a class="lang" href="{url(other, other_slug)}" hreflang="{other}" lang="{other}">'
                 f'{esc(ui["other_lang"])}</a>')

    c = site['contact']
    phone = f'<a href="tel:{esc(re.sub(r"[^0-9+]", "", c["phone"]))}">{esc(c["phone"])}</a><br>' if c.get('phone') else ''
    email2 = f'<a href="mailto:{esc(c["email2"])}">{esc(c["email2"])}</a><br>' if c.get('email2') else ''
    reg = ctx.t(site['firm'].get('registration'))
    reg_html = f'<br>{esc(reg)}' if reg else ''

    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(full_title)}</title>
<meta name="description" content="{esc(description)}">
<meta name="robots" content="{robots}">
{verify}{feed}<link rel="canonical" href="{canonical}">
{hreflang}
<meta property="og:type" content="{og_type}">
<meta property="og:title" content="{esc(title or firm)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="https://{site['domain']}/{esc(image)}">
<meta property="og:locale" content="{'bg_BG' if lang == 'bg' else 'en_GB'}">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="preload" href="/assets/fonts/source-serif-4-{'cyrillic' if lang == 'bg' else 'latin'}-standard-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/site.css">
<script type="application/ld+json">{ld_script(ctx, extra_ld)}</script>
</head>
<body>
<a class="skip" href="#main">{esc(ui['skip'])}</a>
<header class="top">
  <div class="wrap top-in">
    {wordmark(ctx)}
    <button class="menu-btn" type="button" aria-expanded="false" aria-controls="nav">{esc(ui['menu'])}</button>
    <nav id="nav" class="nav" aria-label="{esc(ui['menu'])}">{nav}{lang_link}</nav>
  </div>
</header>
<main id="main">
{body}
</main>
<footer class="foot">
  <div class="wrap foot-in">
    <div>
      <p class="foot-name">{esc(firm)}</p>
      <p>{esc(ctx.t(site['firm']['bar']))}{reg_html}</p>
    </div>
    <div>
      <p>{esc(ctx.t(c['address']))}<br>{esc(ctx.t(c['hours']))}</p>
    </div>
    <div>
      <p>{phone}<a href="mailto:{esc(c['email'])}">{esc(c['email'])}</a><br>{email2}</p>
    </div>
    <div>
      <p><a href="{url(lang, 'privacy')}">{esc(ui['privacy'])}</a><br>
      <a href="{url(lang, 'legal-notice')}">{esc(ui['notice'])}</a></p>
    </div>
  </div>
</footer>
<script src="/assets/site.js" defer></script>
</body>
</html>
"""


def maps_link(ctx):
    c = ctx.site['contact']
    return 'https://www.google.com/maps/search/?api=1&query=' + quote(c.get('map_query') or ctx.t(c['address']))


def contact_facts(ctx):
    c, ui = ctx.site['contact'], ctx.ui
    map_url = maps_link(ctx)
    rows = [(ui['address'], f'{esc(ctx.t(c["address"]))}<br><a href="{map_url}" rel="noopener">{esc(ui["map"])}</a>'),
            (ui['hours'], esc(ctx.t(c['hours'])))]
    if c.get('phone'):
        tel = re.sub(r'[^0-9+]', '', c['phone'])
        rows.append((ui['phone'], f'<a href="tel:{esc(tel)}">{esc(c["phone"])}</a>'))
    mails = [m for m in (c.get('email'), c.get('email2')) if m]
    rows.append((ui['email'], '<br>'.join(f'<a href="mailto:{esc(m)}">{esc(m)}</a>' for m in mails)))
    return '<dl class="facts">' + ''.join(f'<div><dt>{esc(k)}</dt><dd>{v}</dd></div>' for k, v in rows) + '</dl>'


def person_card(ctx, p):
    name = ctx.t(p['name'])
    if p.get('photo'):
        pic = f'<img src="/{esc(p["photo"])}" alt="{esc(name)}" loading="lazy">'
    else:
        pic = f'<span class="monogram" aria-hidden="true">{esc(initials(name))}</span>'
    bio = nl_html(ctx.t(p.get('bio')))
    return (f'<article class="person" id="{esc(p["id"])}"><div class="person-pic">{pic}</div>'
            f'<div class="person-text"><h3>{esc(name)}</h3><p class="person-role">{esc(ctx.t(p.get("role")))}</p>'
            f'{bio}</div></article>')


def article_card(ctx, art):
    ui, lang = ctx.ui, ctx.lang
    link = url(lang, 'articles/' + art['id'])
    img = (f'<a class="card-img" href="{link}" tabindex="-1" aria-hidden="true">'
           f'<img src="/{esc(art["image"])}" alt="" loading="lazy"></a>') if art.get('image') else ''
    cat = ctx.t(art.get('category'))
    meta = esc(fmt_date(art.get('date'), lang)) + (f', {esc(cat)}' if cat else '')
    return (f'<article class="art-card{" has-img" if img else ""}">{img}<div><p class="art-meta">{meta}</p>'
            f'<h3><a href="{link}">{esc(ctx.t(art["title"]))}</a></h3>'
            f'<p>{esc(ctx.t(art.get("excerpt")))}</p></div></article>')


def page_home(ctx):
    s, ui, lang = ctx.site, ctx.ui, ctx.lang
    f, home, c = s['firm'], s['home'], s['contact']
    area_rows = ''.join(
        f'<a class="area" href="{url(lang, "services")}#{esc(a["id"])}"><h3>{esc(ctx.t(a["title"]))}</h3>'
        f'<p>{esc(ctx.t(a["summary"]))}</p></a>' for a in s['services'])
    steps = ''.join(
        f'<li><h3>{esc(ctx.t(p["title"]))}</h3><p>{esc(ctx.t(p["text"]))}</p></li>' for p in home['process'])
    people = ''.join(person_card(ctx, p) for p in s['team'])
    latest = ''
    if ctx.live:
        cards = ''.join(article_card(ctx, a) for a in ctx.live[:3])
        latest = (f'<section class="band"><div class="wrap split"><div class="split-head"><h2>{esc(ui["latest"])}</h2>'
                  f'<p><a href="{url(lang, "articles")}">{esc(ui["all_articles"])}</a></p></div>'
                  f'<div class="art-list">{cards}</div></div></section>')
    body = f"""
<section class="hero">
  <div class="wrap hero-grid">
    <div class="hero-text">
      <h1>
        <span class="hero-legal">{esc(ctx.t(f['name']))}</span>
        <span class="hero-name" aria-hidden="true"><span>{esc(ctx.t(f['short_first']))}</span><span class="hero-second"><span class="hero-amp">&amp;</span> {esc(ctx.t(f['short_second']))}</span></span>
      </h1>
      <p class="hero-lead">{esc(ctx.t(home['lead']))}</p>
      <p class="hero-cta">
        <a class="btn btn-light" href="{url(lang, 'contact')}">{esc(ctx.t(home['cta_primary']))}</a>
        <span class="hero-links">
          <a class="link-light" href="{url(lang, 'services')}">{esc(ctx.t(home['cta_secondary']))}</a>
          <a class="link-light" href="{maps_link(ctx)}" rel="noopener">{esc(ui['map_hero'])}</a>
        </span>
      </p>
    </div>
    <figure class="hero-img"><img src="/{esc(home['hero_image'])}" alt="{esc(ctx.t(home['hero_alt']))}" fetchpriority="high"></figure>
  </div>
</section>
<section class="band band-areas">
  <div class="wrap split">
    <div class="split-head"><h2>{esc(ctx.t(s['services_page']['title']))}</h2></div>
    <div class="area-list">{area_rows}</div>
  </div>
</section>
<section class="band band-mist">
  <div class="wrap split">
    <div class="split-head"><h2>{esc(ctx.t(home['process_title']))}</h2></div>
    <ol class="steps">{steps}</ol>
  </div>
</section>
<section class="band">
  <div class="wrap split">
    <div class="split-head"><h2>{esc(ctx.t(s['about']['team_title']))}</h2>
    <p><a href="{url(lang, 'about')}">{esc(ui['more_about'])}</a></p></div>
    <div class="people">{people}</div>
  </div>
</section>
{latest}
<section class="band band-ink">
  <div class="wrap split">
    <div class="split-head"><h2>{esc(ctx.t(s['contact_page']['title']))}</h2>
    <p><a class="btn btn-light" href="{url(lang, 'contact')}">{esc(ui['contact_us'])}</a></p></div>
    {contact_facts(ctx)}
  </div>
</section>"""
    return layout(ctx, '', '', ctx.t(s['seo']['home']), body, home_title=ctx.t(s['seo'].get('home_title')))


def page_head(title, intro=''):
    intro_html = f'<p class="page-intro">{esc(intro)}</p>' if intro else ''
    return f'<header class="page-head"><div class="wrap"><h1>{esc(title)}</h1>{intro_html}</div></header>'


def page_about(ctx):
    s = ctx.site
    about = s['about']
    people = ''.join(person_card(ctx, p) for p in s['team'])
    body = f"""{page_head(ctx.t(about['title']))}
<section class="band">
  <div class="wrap prose-wrap"><div class="prose">{nl_html(ctx.t(about['text']))}</div></div>
</section>
<section class="band band-mist" id="team">
  <div class="wrap split">
    <div class="split-head"><h2>{esc(ctx.t(about['team_title']))}</h2></div>
    <div class="people people-full">{people}</div>
  </div>
</section>"""
    return layout(ctx, 'about', ctx.t(about['title']), ctx.t(s['seo']['about']), body, active='about',
                  extra_ld=[crumbs_ld(ctx, [(ctx.t(about['title']), 'about')])])


def page_services(ctx):
    s = ctx.site
    blocks = ''
    for a in s['services']:
        items = [i.strip() for i in ctx.t(a.get('items')).split('\n') if i.strip()]
        lis = ''.join(f'<li>{esc(i)}</li>' for i in items)
        blocks += (f'<section class="service" id="{esc(a["id"])}"><div class="service-head"><h2>{esc(ctx.t(a["title"]))}</h2>'
                   f'<p>{esc(ctx.t(a["summary"]))}</p></div><ul class="service-items">{lis}</ul></section>')
    page = s['services_page']
    body = f"""{page_head(ctx.t(page['title']), ctx.t(page['intro']))}
<div class="wrap services">{blocks}</div>
<section class="band band-ink"><div class="wrap cta-row">
  <p class="cta-text">{esc(ctx.t(page['intro']))}</p>
  <a class="btn btn-light" href="{url(ctx.lang, 'contact')}">{esc(ctx.ui['contact_us'])}</a>
</div></section>"""
    return layout(ctx, 'services', ctx.t(page['title']), ctx.t(s['seo']['services']), body, active='services',
                  extra_ld=[crumbs_ld(ctx, [(ctx.t(page['title']), 'services')])])


def page_contact(ctx):
    s, ui, lang = ctx.site, ctx.ui, ctx.lang
    page = s['contact_page']
    err = ui['form_err'].format(email=s['contact']['email'])
    faq = [q for q in s.get('faq', []) if ctx.t(q.get('q')) and ctx.t(q.get('a'))]
    faq_html = ''
    if faq:
        rows = ''.join(f'<div><h3>{esc(ctx.t(q["q"]))}</h3><p>{esc(ctx.t(q["a"]))}</p></div>' for q in faq)
        faq_html = (f'<section class="band band-mist" id="faq"><div class="wrap split"><div class="split-head">'
                    f'<h2>{esc(ui["faq"])}</h2></div><div class="faq">{rows}</div></div></section>')
    body = f"""{page_head(ctx.t(page['title']), ctx.t(page['intro']))}
<section class="band">
  <div class="wrap contact-grid">
    {contact_facts(ctx)}
    <form id="contact-form" class="form" data-source="{esc(s['form_source'])}" data-sending="{esc(ui['form_sending'])}" data-ok="{esc(ui['form_ok'])}" data-err="{esc(err)}">
      <label for="f-name">{esc(ui['form_name'])}</label>
      <input id="f-name" name="name" type="text" autocomplete="name" required>
      <label for="f-email">{esc(ui['form_email'])}</label>
      <input id="f-email" name="email" type="email" autocomplete="email" required>
      <label for="f-message">{esc(ui['form_message'])}</label>
      <textarea id="f-message" name="message" rows="7" required></textarea>
      <p class="form-note">{esc(ctx.t(page['form_note']))}</p>
      <label class="check"><input type="checkbox" name="consent" required> <span>{esc(ui['form_consent'])} <a href="{url(lang, 'privacy')}">{esc(ui['form_consent_link'])}</a>.</span></label>
      <button class="btn" type="submit">{esc(ui['form_send'])}</button>
      <p id="form-status" role="status" aria-live="polite"></p>
    </form>
  </div>
</section>
{faq_html}"""
    extra = [crumbs_ld(ctx, [(ctx.t(page['title']), 'contact')])]
    if faq:
        extra.append({'@type': 'FAQPage', 'mainEntity': [
            {'@type': 'Question', 'name': ctx.t(q['q']),
             'acceptedAnswer': {'@type': 'Answer', 'text': ctx.t(q['a'])}} for q in faq]})
    return layout(ctx, 'contact', ctx.t(page['title']), ctx.t(s['seo']['contact']), body, active='contact', extra_ld=extra)


def page_articles(ctx):
    s = ctx.site
    page = s['articles_page']
    cards = ''.join(article_card(ctx, a) for a in ctx.live)
    body = f"""{page_head(ctx.t(page['title']), ctx.t(page['intro']))}
<section class="band"><div class="wrap art-page">{cards}</div></section>"""
    return layout(ctx, 'articles', ctx.t(page['title']), ctx.t(s['seo']['articles']), body, active='articles',
                  extra_ld=[crumbs_ld(ctx, [(ctx.t(page['title']), 'articles')])])


def article_ld(ctx, art, title, slug, author):
    base = f"https://{ctx.site['domain']}"
    data = {'@type': 'Article', 'headline': title, 'description': ctx.t(art.get('excerpt')),
            'inLanguage': ctx.lang, 'datePublished': art.get('date', ''),
            'dateModified': art.get('updated') or art.get('date', ''),
            'mainEntityOfPage': abs_url(ctx.site, ctx.lang, slug),
            'publisher': {'@id': f'{base}/#firm'}}
    if art.get('image'):
        data['image'] = f"{base}/{art['image']}"
    data['author'] = {'@id': f"{base}/#{author['id']}"} if author else {'@id': f'{base}/#firm'}
    return data


def page_article(ctx, art):
    s, ui, lang = ctx.site, ctx.ui, ctx.lang
    title = ctx.t(art['title'])
    other = 'en' if lang == 'bg' else 'bg'
    slug = 'articles/' + art['id']
    has_other = art.get('title', {}).get(other, '').strip()
    other_slug = slug if has_other else ''
    author = next((p for p in s['team'] if p['id'] == art.get('author')), None)
    meta = [fmt_date(art.get('date'), lang)]
    if ctx.t(art.get('category')):
        meta.append(esc(ctx.t(art['category'])))
    author_html = ''
    if author:
        author_html = (f'<p class="art-author">{esc(ui["by"])} '
                       f'<a href="{url(lang, "about")}#{esc(author["id"])}">{esc(ctx.t(author["name"]))}</a></p>')
    image = ''
    if art.get('image'):
        alt = esc(ctx.t(art.get('image_alt')))
        image = f'<figure class="art-cover"><img src="/{esc(art["image"])}" alt="{alt}"></figure>'
    body = f"""<article class="article">
  <header class="page-head"><div class="wrap">
    <p class="art-meta art-meta-head">{', '.join(meta)}</p>
    <h1>{esc(title)}</h1>
    {author_html}
  </div></header>
  <div class="wrap prose-wrap">
    {image}
    <div class="prose">{MD.to_html(ctx.t(art.get('body')))}</div>
    <p class="disclaimer">{esc(ctx.t(s['articles_page']['disclaimer']))}</p>
    <p><a href="{url(lang, 'articles')}">{esc(ui['back'])}</a></p>
  </div>
</article>"""
    return layout(ctx, slug, title, ctx.t(art.get('excerpt')) or title, body, other_slug=other_slug,
                  active='articles', og_image=art.get('image'), og_type='article', extra_ld=[
                      crumbs_ld(ctx, [(ctx.t(s['articles_page']['title']), 'articles'), (title, slug)]),
                      article_ld(ctx, art, title, slug, author)])


def legal_page(ctx, key, slug):
    node = ctx.site['legal'][key]
    title = ctx.t(node['title'])
    body = f"""{page_head(title)}
<section class="band"><div class="wrap prose-wrap"><div class="prose">{MD.to_html(ctx.t(node['body']))}</div></div></section>"""
    plain = re.sub(r'[#*\n]+', ' ', ctx.t(node['body'])).strip()[:150]
    return layout(ctx, slug, title, plain, body)


def page_privacy(ctx):
    return legal_page(ctx, 'privacy', 'privacy')


def page_notice(ctx):
    return legal_page(ctx, 'notice', 'legal-notice')


def page_404(ctx):
    ui = ctx.ui
    body = f"""{page_head(ui['not_found'], ui['not_found_text'])}
<section class="band"><div class="wrap"><a class="btn" href="/">{esc(ui['home'])}</a></div></section>"""
    return layout(ctx, '', ui['not_found'], ui['not_found_text'], body, noindex=True)
