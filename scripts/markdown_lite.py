"""Малък Markdown -> HTML: заглавия, параграфи, списъци, цитати, линии,
удебелен, курсив, връзки и изображения. Текстът се екранира, преди да се обработи."""
import html as _html
import re

_BOLD = re.compile(r'\*\*(.+?)\*\*')
_ITALIC = re.compile(r'(?<![\*\w])\*(?!\s)(.+?)(?<!\s)\*(?![\*\w])')
_IMAGE = re.compile(r'!\[([^\]]*)\]\(([^)\s]+)\)')
_LINK = re.compile(r'\[([^\]]+)\]\(([^)\s]+)\)')
_SAFE_URL = re.compile(r'^(https?://|mailto:|/|#)|^[\w./-]+$')


def _url(raw):
    url = raw.strip()
    if not _SAFE_URL.match(url):
        return '#'
    if url.startswith('images/'):
        return '/' + url
    return url


def inline(text):
    text = _html.escape(text, quote=True)
    text = _IMAGE.sub(lambda m: f'<img src="{_url(m.group(2))}" alt="{m.group(1)}" loading="lazy">', text)
    text = _LINK.sub(lambda m: f'<a href="{_url(m.group(2))}">{m.group(1)}</a>', text)
    text = _BOLD.sub(r'<strong>\1</strong>', text)
    text = _ITALIC.sub(r'<em>\1</em>', text)
    return text


def to_html(text):
    """Абзаците се делят с празен ред. Заглавията в текста започват от h2."""
    if not text:
        return ''
    out, para, items = [], [], []
    kind = None

    def flush():
        nonlocal kind
        if para:
            joined = ' '.join(para).strip()
            m = _IMAGE.fullmatch(joined)
            if m:
                alt = m.group(1)
                cap = f'<figcaption>{_html.escape(alt)}</figcaption>' if alt else ''
                out.append(f'<figure>{inline(joined)}{cap}</figure>')
            else:
                out.append(f'<p>{inline(joined)}</p>')
            para.clear()
        if items:
            if kind == 'blockquote':
                out.append('<blockquote><p>' + ' '.join(inline(i) for i in items) + '</p></blockquote>')
            else:
                out.append(f'<{kind}>' + ''.join(f'<li>{inline(i)}</li>' for i in items) + f'</{kind}>')
            items.clear()
        kind = None

    for raw in text.replace('\r\n', '\n').split('\n'):
        line = raw.strip()
        if not line:
            flush()
            continue
        if re.fullmatch(r'-{3,}', line):
            flush()
            out.append('<hr>')
            continue
        h = re.match(r'^(#{1,3})\s+(.*)$', line)
        if h:
            flush()
            level = max(len(h.group(1)), 2)
            out.append(f'<h{level}>{inline(h.group(2))}</h{level}>')
            continue
        for pattern, tag in ((r'^[-*]\s+(.*)$', 'ul'), (r'^\d+[.)]\s+(.*)$', 'ol'), (r'^>\s?(.*)$', 'blockquote')):
            m = re.match(pattern, line)
            if m:
                if kind != tag or para:
                    flush()
                kind = tag
                items.append(m.group(1))
                break
        else:
            if items:
                flush()
            para.append(line)
    flush()
    return '\n'.join(out)
