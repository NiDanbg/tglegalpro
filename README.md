# Адвокатско дружество „Тенев и Гачев“: tglegalpro.com

Статичен сайт на български (`/`) и английски (`/en/`). Хостинг: GitHub Pages.

## Работа със съдържанието

Панелът работи само на компютъра на автора и не се качва в това хранилище. Сайтът се публикува от `content/`, `images/`, `assets/` и `scripts/` чрез GitHub Actions при всяко качване в `main`.

## Структура

| Път | Съдържание |
| --- | --- |
| `content/site.json` | данни за дружеството, екип, области, текстове, описания за търсачки |
| `content/articles/*.json` | статиите, по един файл; името на файла е адресът |
| `images/` | снимки, прекодирани в WebP от панела |
| `scripts/render.py` | HTML шаблоните и структурираните данни |
| `scripts/discovery.py` | robots.txt, sitemap.xml, llms.txt, llms-full.txt, RSS |
| `assets/site.css` | дизайнът |

## Контактна форма

`assets/site.js` пише в същия Google Form като другите сайтове. Съобщенията започват с `[TG Legal Pro website]` (полето `form_source` в `site.json`).

## Снимка на началната страница

`images/site/hero.webp`: снимка от Unsplash, лиценз Unsplash License:
https://unsplash.com/photos/book-lot-on-black-wooden-shelf-zeH-ljawHtg

Шрифтове: Source Serif 4 и Commissioner, лиценз SIL OFL (`assets/fonts/`).
