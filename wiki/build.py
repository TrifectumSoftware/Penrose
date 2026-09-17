"""Static wiki builder with MediaWiki-style features.

Reads .md files from content/, converts to HTML, outputs to dist/.
Supports categories, infoboxes, charts, nav bars, and more.
No external dependencies. To add a page, create a .md file in content/.
"""

import json
import math
import random
import re
import shutil
from datetime import datetime
from pathlib import Path

import config

CONTENT_DIR = Path(__file__).parent / "content"
DIST_DIR = Path(__file__).parent / "dist"
STATIC_DIR = Path(__file__).parent / "static"

SEARCH_FORM = f"""<form class="searchbox" action="search.html" method="get" role="search">
  <img class="searchbox__icon" src="static/icons/w98_magnifying_glass.png" alt="">
  <input class="searchbox__input" type="text" name="q" placeholder="Search the wiki" autocomplete="off">
  <button class="searchbox__btn" type="submit">Search</button>
</form>"""

HERO = f"""<div class="hero">
  <img class="hero__logo" src="{config.WG_LOGO_MAIN}" alt="{config.WG_SITENAME}">
  <div class="hero__title">{config.WG_SITENAME}</div>
  <div class="hero__subtitle">{config.WG_TAGLINE}</div>
</div>"""

RANDOM_BUTTON = """<div class="hero-actions">
  <button id="random-page" class="random-btn" type="button">
    <img src="static/icons/w98_gears.png" alt=""> Random page
  </button>
</div>"""

# Article tags: {{name}} renders a banner. (icon, title, body)
TAGS = config.WG_TAGS


# ── Helpers ───────────────────────────────────────────────────────

def wiki_config_json():
    return json.dumps({
        "defaultTheme": config.WG_DEFAULT_THEME,
        "defaultZoom": config.WG_DEFAULT_ZOOM,
        "zoomMin": config.WG_ZOOM_MIN,
        "zoomMax": config.WG_ZOOM_MAX,
        "zoomStep": config.WG_ZOOM_STEP,
        "voronoiLightBase": config.WG_VORONOI_LIGHT_BASE,
        "voronoiLightCell": config.WG_VORONOI_LIGHT_CELL,
        "voronoiDarkBase": config.WG_VORONOI_DARK_BASE,
        "voronoiDarkCell": config.WG_VORONOI_DARK_CELL,
    })


def render_tag(key):
    icon, title, body = TAGS[key]
    return f"""<div class="tag tag--{key}">
  <img class="tag__icon" src="static/icons/{icon}" alt="">
  <div class="tag__text"><strong>{title}</strong> {body}</div>
</div>"""


def parse_frontmatter(md):
    meta = {}
    body = md
    if md.startswith("---"):
        lines = md.split("\n")
        for idx in range(1, len(lines)):
            if lines[idx].strip() == "---":
                body = "\n".join(lines[idx + 1:])
                break
            if ":" in lines[idx]:
                k, v = lines[idx].split(":", 1)
                key = k.strip().lower()
                val = v.strip()
                if key == "categories":
                    meta["categories"] = [c.strip() for c in val.split(",")]
                else:
                    meta[key] = val
    return meta, body


# -- Navigation --------------------------------------------------------

def build_nav_bar(current_name):
    links = []
    for label, url in config.WG_NAV_LINKS:
        cls = " nav-bar__link--active" if url == current_name + ".html" else ""
        links.append(f'<a class="nav-bar__link{cls}" href="{url}">{label}</a>')
    nav_left = "\n".join(links)
    nav_right = (
        '<span class="nav-bar__history">'
        '<button class="nav-bar__btn" onclick="history.back()" title="Back">&#9665;</button>'
        '<button class="nav-bar__btn" onclick="history.forward()" title="Forward">&#9655;</button>'
        '</span>'
    )
    return f'<nav class="nav-bar">\n{nav_left}\n{nav_right}\n</nav>'


def build_breadcrumbs(page):
    crumbs = [('<a href="index.html">Home</a>',)]
    topic = page.get("topic")
    if topic:
        topic_slug = topic.lower().replace(" ", "-")
        crumbs.append((f'<a href="category-{topic_slug}.html">{topic}</a>',))
    crumbs.append((f'<span>{page["title"]}</span>',))
    parts = []
    for crumb in crumbs:
        parts.append(f'<span class="breadcrumb">{crumb[0]}</span>')
    return '<nav class="breadcrumbs" aria-label="Breadcrumb">\n' + " &rsaquo; ".join(parts) + "\n</nav>"


def build_sidebar_html(current_name):
    sections = []
    for heading, links in config.WG_SIDEBAR_SECTIONS:
        items = []
        for label, url in links:
            cls = " active" if url == current_name + ".html" else ""
            if url.startswith("http"):
                items.append(f'<li><a href="{url}" target="_blank" rel="noopener">{label}</a></li>')
            else:
                items.append(f'<li><a class="{cls.strip()}" href="{url}">{label}</a></li>')
        sections.append(f'<div class="sidebar-section"><h3>{heading}</h3><ul>{"".join(items)}</ul></div>')
    return "\n".join(sections)


# ── Homepage sections ─────────────────────────────────────────────

def build_featured_html(pages):
    if not config.WG_FEATURED_PAGE:
        return ""
    featured = next((p for p in pages if p["name"] == config.WG_FEATURED_PAGE), None)
    if not featured:
        return ""
    icon = featured.get("icon", "w98_file_lines.png")
    if not icon.startswith("static/"):
        icon = "static/icons/" + icon
    excerpt = md_to_text(featured["md"])[:200] + "..."
    return f"""<div class="featured">
  <h2>Featured Article</h2>
  <div class="featured__card">
    <img class="featured__icon" src="{icon}" alt="">
    <div class="featured__body">
      <a class="featured__title" href="{featured["name"]}.html">{featured["title"]}</a>
      <p class="featured__excerpt">{excerpt}</p>
      <a class="featured__link" href="{featured["name"]}.html">Read more &rarr;</a>
    </div>
  </div>
</div>"""


def build_quick_nav(pages):
    groups = {}
    for p in pages:
        if p["name"] in ("index", "search"):
            continue
        topic = p.get("topic") or "Uncategorized"
        if topic not in groups:
            groups[topic] = []
        groups[topic].append(p)

    items = []
    for topic in sorted(groups):
        members = groups[topic]
        icon = next((p["icon"] for p in members if p.get("icon")), "w98_file_lines.png")
        if not icon.startswith("static/"):
            icon = "static/icons/" + icon
        topic_slug = topic.lower().replace(" ", "-")
        items.append(
            f'<a class="quick-nav__item" href="category-{topic_slug}.html">'
            f'<img class="quick-nav__icon" src="{icon}" alt="">'
            f'<span class="quick-nav__label">{topic}</span></a>'
        )
    return '<div class="quick-nav">\n' + "\n".join(items) + "\n</div>"


def build_did_you_know():
    facts = config.WG_DID_YOU_KNOW
    if not facts:
        return ""
    items = []
    for fact in facts:
        items.append(f"<li>{inline(fact)}</li>")
    return f"""<div class="dyk">
  <h2>Did you know&hellip;</h2>
  <ul class="dyk__list">
    {"".join(items)}
  </ul>
</div>"""


# ── Category system ───────────────────────────────────────────────

def build_category_index(pages):
    cats = {}
    for p in pages:
        for cat in p.get("categories", []):
            if cat not in cats:
                cats[cat] = []
            cats[cat].append(p)
    return cats


def build_category_page_html(cat_name, cat_pages, all_pages):
    items = []
    for p in sorted(cat_pages, key=lambda x: x["title"].lower()):
        icon = p.get("icon", "w98_file_lines.png")
        if not icon.startswith("static/"):
            icon = "static/icons/" + icon
        items.append(
            f'<li class="cat-page">'
            f'<img class="cat-page__icon" src="{icon}" alt="">'
            f'<a href="{p["name"]}.html">{p["title"]}</a>'
            f'</li>'
        )
    body = f'<h1 id="category-{cat_name.lower()}">Category: {cat_name}</h1>\n'
    body += f'<p class="cat-count">{len(cat_pages)} page{"s" if len(cat_pages) != 1 else ""} in this category.</p>\n'
    body += '<ul class="cat-list">\n' + "\n".join(items) + "\n</ul>"
    return build_page(
        {"name": f"category-{cat_name.lower().replace(' ', '-')}", "title": f"Category: {cat_name}", "categories": []},
        all_pages, body, ""
    )


def build_all_pages_html(pages):
    items = []
    for p in sorted(pages, key=lambda x: x["title"].lower()):
        if p["name"] in ("index", "search"):
            continue
        cats = ", ".join(p.get("categories", []))
        cat_str = f' <span class="all-pages__cats">({cats})</span>' if cats else ""
        items.append(f'<li><a href="{p["name"]}.html">{p["title"]}</a>{cat_str}</li>')
    body = '<h1 id="all-pages">All Pages</h1>\n'
    body += f'<p>{len(pages)} pages in the wiki.</p>\n'
    body += '<ul class="all-pages__list">\n' + "\n".join(items) + "\n</ul>"
    return build_page({"name": "all-pages", "title": "All Pages", "categories": []}, pages, body, "")


# ── Related articles ──────────────────────────────────────────────

def build_related_articles(page, pages):
    page_cats = set(page.get("categories", []))
    page_topic = page.get("topic")
    related = []
    for p in pages:
        if p["name"] == page["name"] or p["name"] in ("index", "search"):
            continue
        score = 0
        if p.get("topic") == page_topic:
            score += 2
        if set(p.get("categories", [])) & page_cats:
            score += 1
        if score > 0:
            related.append((score, p))
    related.sort(key=lambda x: -x[0])
    related = related[:5]
    if not related:
        return ""
    items = []
    for _, p in related:
        items.append(f'<li><a href="{p["name"]}.html">{p["title"]}</a></li>')
    return f'<div class="related"><h3>Related articles</h3><ul>{"".join(items)}</ul></div>'


# ── Page metadata ─────────────────────────────────────────────────

def build_page_metadata(page):
    cats = page.get("categories", [])
    cat_links = []
    for c in cats:
        slug = c.lower().replace(" ", "-")
        cat_links.append(f'<a href="category-{slug}.html">{c}</a>')
    if not cat_links:
        return ""
    return '<div class="page-meta">Categories: ' + ", ".join(cat_links) + "</div>"


# ── Site stats ────────────────────────────────────────────────────

def build_site_stats(pages):
    n_pages = len([p for p in pages if p["name"] not in ("index", "search")])
    cats = build_category_index(pages)
    n_cats = len(cats)
    n_articles = sum(1 for p in pages if p["name"] not in ("index", "search", "contents", "this-wiki"))
    return f'<div class="site-stats">{n_pages} pages &middot; {n_cats} categories &middot; {n_articles} articles</div>'


def build_footer(pages):
    return f"""<footer class="wiki-footer">
  <div class="wiki-footer__links">
    <a href="index.html">Home</a>
    <a href="contents.html">Contents</a>
    <a href="all-pages.html">All Pages</a>
    <a href="search.html">Search</a>
    <a href="this-wiki.html">About</a>
    <a href="{config.WG_SOURCE_URL}" target="_blank" rel="noopener">Source</a>
  </div>
  <div class="wiki-footer__copy">
    Content is available under CC0 1.0 Universal.
  </div>
</footer>"""


# ── Collapsible TOC ───────────────────────────────────────────────

def build_toc(lines):
    items = []
    for line in lines:
        m = re.match(r"^(#{1,4})\s+(.+)", line)
        if m:
            level = len(m.group(1))
            text = m.group(2)
            anchor = text.lower().strip()
            anchor = re.sub(r"[^a-z0-9]+", "-", anchor)
            cls = "toc__item" if level == 1 else "toc__item toc__item--sub"
            items.append(f'<li class="{cls}"><a href="#{anchor}">{inline(text)}</a></li>')
    if not items:
        return ""
    return (
        '<nav class="toc-nav" aria-label="Table of contents">'
        '<div class="toc"><div class="toc__header" role="button" tabindex="0">'
        '<h2 class="toc__title">Contents</h2>'
        '<span class="toc__toggle">&#9660;</span></div>'
        '<ul class="toc__list">\n' + "\n".join(items) + "\n</ul></div></nav>"
    )


# ── Table parsing ─────────────────────────────────────────────────

def split_table_row(line):
    r = line.strip()
    if r.startswith("|"):
        r = r[1:]
    if r.endswith("|"):
        r = r[:-1]
    return [c.strip() for c in r.split("|")]


def is_separator_row(cells):
    return all(re.match(r"^:?-{1,}:?$", c) for c in cells)


def parse_table(raw_lines, shadow=False):
    row_classes = []
    table_lines = []
    for line in raw_lines:
        m = re.match(r"^<!--\s*rowclass:(\w+)\s*-->$", line.strip())
        if m:
            row_classes.append(m.group(1))
        else:
            table_lines.append(line)

    rows = [split_table_row(line) for line in table_lines]
    if not rows:
        return ""

    if len(rows) > 1 and is_separator_row(rows[1]):
        header = rows[0]
        body = rows[2:]
    else:
        header = rows[0]
        body = rows[1:]

    cls = ' class="shadow"' if shadow else ""
    out = [f"<table{cls}>"]
    out.append("<thead><tr>" + "".join(f"<th>{inline(c)}</th>" for c in header) + "</tr></thead>")
    if body:
        out.append("<tbody>")
        for ri, row in enumerate(body):
            rcls = f' class="row-{row_classes[ri]}"' if ri < len(row_classes) else ""
            out.append(f"<tr{rcls}>" + "".join(f"<td>{inline(c)}</td>" for c in row) + "</tr>")
        out.append("</tbody>")
    out.append("</table>")
    return "\n".join(out)


# ── Infobox ───────────────────────────────────────────────────────

def parse_infobox(lines):
    title = None
    image = None
    caption = None
    rows = []

    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        if "=" in line:
            key, val = line.split("=", 1)
            key = key.strip()
            val = val.strip()
            kl = key.lower()
            if kl == "title":
                title = val
            elif kl == "image":
                image = val
            elif kl == "caption":
                caption = val
            else:
                rows.append((key, val))
        else:
            rows.append((line, ""))

    out = ['<aside class="infobox"><table>']
    if title:
        out.append(f'<tr class="infobox__title"><th colspan="2">{inline(title)}</th></tr>')
    if image:
        img = f'<img src="{image}" alt="{title or "infobox"}">'
        cap = f'<div class="infobox__caption">{inline(caption)}</div>' if caption else ""
        out.append(f'<tr class="infobox__image"><td colspan="2">{img}{cap}</td></tr>')
    for key, val in rows:
        out.append(f"<tr><th>{inline(key)}</th><td>{inline(val)}</td></tr>")
    out.append("</table></aside>")
    return "\n".join(out)


# ── Charts ────────────────────────────────────────────────────────

PIE_COLORS = [
    "#3366cc", "#dc3912", "#ff9900", "#109618",
    "#990099", "#0099c6", "#dd4477", "#66aa00",
    "#b82e2e", "#316395", "#994499", "#22aa99",
]

BAR_COLORS = [
    "#3366cc", "#dc3912", "#ff9900", "#109618",
    "#990099", "#0099c6", "#dd4477", "#66aa00",
]


def _parse_kv(lines):
    title = None
    items = []
    for raw in lines:
        line = raw.strip()
        if not line or "=" not in line:
            continue
        key, val = line.split("=", 1)
        key = key.strip()
        val = val.strip()
        if key.lower() == "title":
            title = val
        else:
            items.append((key, val))
    return title, items


def parse_pie(lines):
    title, items = _parse_kv(lines)
    slices = []
    for k, v in items:
        try:
            slices.append((k, float(v)))
        except ValueError:
            continue
    total = sum(v for _, v in slices)
    if total == 0:
        return ""

    size = 200
    cx, cy, r = size // 2, size // 2, 80
    legend_items = []
    paths = []
    angle = -math.pi / 2
    for i, (label, value) in enumerate(slices):
        sweep = 2 * math.pi * (value / total)
        x1 = cx + r * math.cos(angle)
        y1 = cy + r * math.sin(angle)
        x2 = cx + r * math.cos(angle + sweep)
        y2 = cy + r * math.sin(angle + sweep)
        large = 1 if sweep > math.pi else 0
        color = PIE_COLORS[i % len(PIE_COLORS)]
        d = f"M{cx},{cy} L{x1:.1f},{y1:.1f} A{r},{r} 0 {large},1 {x2:.1f},{y2:.1f} Z"
        pct = value / total * 100
        paths.append(f'<path d="{d}" fill="{color}" stroke="var(--win-white)" stroke-width="1"/>')
        legend_items.append(f'<span class="pie-legend__item"><span class="pie-legend__swatch" style="background:{color}"></span>{label} ({pct:.0f}%)</span>')
        angle += sweep

    svg = f'<svg viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg">\n' + "\n".join(paths) + "\n</svg>"
    title_html = f'<div class="chart__title">{inline(title)}</div>' if title else ""
    legend_html = '<div class="pie-legend">' + "".join(legend_items) + "</div>"
    return f'<div class="chart">{title_html}{svg}{legend_html}</div>'


def parse_donut(lines):
    title, items = _parse_kv(lines)
    slices = []
    for k, v in items:
        try:
            slices.append((k, float(v)))
        except ValueError:
            continue
    total = sum(v for _, v in slices)
    if total == 0:
        return ""

    size = 200
    cx, cy = size // 2, size // 2
    r_outer, r_inner = 85, 50
    legend_items = []
    paths = []
    angle = -math.pi / 2
    for i, (label, value) in enumerate(slices):
        sweep = 2 * math.pi * (value / total)
        ox1 = cx + r_outer * math.cos(angle)
        oy1 = cy + r_outer * math.sin(angle)
        ox2 = cx + r_outer * math.cos(angle + sweep)
        oy2 = cy + r_outer * math.sin(angle + sweep)
        ix1 = cx + r_inner * math.cos(angle + sweep)
        iy1 = cy + r_inner * math.sin(angle + sweep)
        ix2 = cx + r_inner * math.cos(angle)
        iy2 = cy + r_inner * math.sin(angle)
        large = 1 if sweep > math.pi else 0
        color = PIE_COLORS[i % len(PIE_COLORS)]
        d = f"M{ox1:.1f},{oy1:.1f} A{r_outer},{r_outer} 0 {large},1 {ox2:.1f},{oy2:.1f} L{ix1:.1f},{iy1:.1f} A{r_inner},{r_inner} 0 {large},0 {ix2:.1f},{iy2:.1f} Z"
        pct = value / total * 100
        paths.append(f'<path d="{d}" fill="{color}" stroke="var(--win-white)" stroke-width="1"/>')
        legend_items.append(f'<span class="pie-legend__item"><span class="pie-legend__swatch" style="background:{color}"></span>{label} ({pct:.0f}%)</span>')
        angle += sweep

    svg = f'<svg viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg">\n' + "\n".join(paths) + "\n</svg>"
    title_html = f'<div class="chart__title">{inline(title)}</div>' if title else ""
    legend_html = '<div class="pie-legend">' + "".join(legend_items) + "</div>"
    return f'<div class="chart">{title_html}{svg}{legend_html}</div>'


def parse_barchart(lines):
    title, items_raw = _parse_kv(lines)
    items = []
    for k, v in items_raw:
        try:
            items.append((k, float(v)))
        except ValueError:
            continue
    if not items:
        return ""
    max_val = max(v for _, v in items)
    if max_val == 0:
        return ""

    bar_h, gap, label_w, chart_w = 24, 6, 80, 300
    total_h = len(items) * (bar_h + gap) + 10
    svg_w = label_w + chart_w + 40

    bars = []
    for i, (label, value) in enumerate(items):
        y = i * (bar_h + gap) + 5
        bw = chart_w * (value / max_val)
        color = BAR_COLORS[i % len(BAR_COLORS)]
        bars.append(f'<text x="{label_w - 6}" y="{y + bar_h // 2 + 4}" text-anchor="end" class="barchart-label">{inline(label)}</text>')
        bars.append(f'<rect x="{label_w}" y="{y}" width="{bw:.1f}" height="{bar_h}" fill="{color}" rx="0"/>')
        bars.append(f'<text x="{label_w + bw + 4}" y="{y + bar_h // 2 + 4}" class="barchart-value">{value:g}</text>')

    svg = f'<svg viewBox="0 0 {svg_w} {total_h}" xmlns="http://www.w3.org/2000/svg">\n' + "\n".join(bars) + "\n</svg>"
    title_html = f'<div class="chart__title">{inline(title)}</div>' if title else ""
    return f'<div class="chart">{title_html}{svg}</div>'


def parse_histogram(lines):
    title, items_raw = _parse_kv(lines)
    items = []
    for k, v in items_raw:
        try:
            items.append((k, float(v)))
        except ValueError:
            continue
    if not items:
        return ""
    max_val = max(v for _, v in items)
    if max_val == 0:
        return ""

    chart_w, chart_h = 400, 200
    margin_l, margin_r, margin_t, margin_b = 50, 20, 10, 40
    inner_w = chart_w - margin_l - margin_r
    inner_h = chart_h - margin_t - margin_b
    n = len(items)
    bar_w = inner_w / n
    gap = max(1, bar_w * 0.1)

    bars = []
    for i, (label, value) in enumerate(items):
        bh = inner_h * (value / max_val)
        x = margin_l + i * bar_w + gap / 2
        y = margin_t + inner_h - bh
        w = bar_w - gap
        color = BAR_COLORS[i % len(BAR_COLORS)]
        bars.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{bh:.1f}" fill="{color}"/>')
        lx = margin_l + i * bar_w + bar_w / 2
        bars.append(f'<text x="{lx:.1f}" y="{chart_h - margin_b + 14}" text-anchor="middle" class="barchart-label">{inline(label)}</text>')
        bars.append(f'<text x="{lx:.1f}" y="{y - 3}" text-anchor="middle" class="barchart-value">{value:g}</text>')
    bars.append(f'<line x1="{margin_l}" y1="{margin_t}" x2="{margin_l}" y2="{margin_t + inner_h}" stroke="var(--win-dark-grey)" stroke-width="1"/>')
    bars.append(f'<line x1="{margin_l}" y1="{margin_t + inner_h}" x2="{margin_l + inner_w}" y2="{margin_t + inner_h}" stroke="var(--win-dark-grey)" stroke-width="1"/>')

    svg = f'<svg viewBox="0 0 {chart_w} {chart_h}" xmlns="http://www.w3.org/2000/svg">\n' + "\n".join(bars) + "\n</svg>"
    title_html = f'<div class="chart__title">{inline(title)}</div>' if title else ""
    return f'<div class="chart">{title_html}{svg}</div>'


def parse_linechart(lines):
    title, items_raw = _parse_kv(lines)
    series = []
    for k, v in items_raw:
        try:
            points = [float(x) for x in v.split()]
            if points:
                series.append((k, points))
        except ValueError:
            continue
    if not series:
        return ""

    all_vals = [v for _, pts in series for v in pts]
    min_val, max_val = min(all_vals), max(all_vals)
    if max_val == min_val:
        max_val = min_val + 1
    max_len = max(len(pts) for _, pts in series)

    chart_w, chart_h = 400, 220
    margin_l, margin_t, margin_b = 50, 20, 40
    inner_w = chart_w - margin_l - 20
    inner_h = chart_h - margin_t - margin_b

    elements = []
    # Axes first (render behind lines)
    elements.append(f'<line x1="{margin_l}" y1="{margin_t}" x2="{margin_l}" y2="{margin_t + inner_h}" stroke="var(--win-dark-grey)" stroke-width="1"/>')
    elements.append(f'<line x1="{margin_l}" y1="{margin_t + inner_h}" x2="{margin_l + inner_w}" y2="{margin_t + inner_h}" stroke="var(--win-dark-grey)" stroke-width="1"/>')
    for i in range(max_len):
        x = margin_l + (i / max(max_len - 1, 1)) * inner_w
        elements.append(f'<text x="{x:.1f}" y="{chart_h - margin_b + 14}" text-anchor="middle" class="barchart-label">{i + 1}</text>')
    for step in range(5):
        v = min_val + (max_val - min_val) * step / 4
        y = margin_t + inner_h - (step / 4) * inner_h
        elements.append(f'<text x="{margin_l - 6}" y="{y + 4}" text-anchor="end" class="barchart-value">{v:g}</text>')
    # Then data lines and points on top
    for i, (name, points) in enumerate(series):
        color = BAR_COLORS[i % len(BAR_COLORS)]
        coords = []
        for j, v in enumerate(points):
            x = margin_l + (j / max(max_len - 1, 1)) * inner_w
            y = margin_t + inner_h - ((v - min_val) / (max_val - min_val)) * inner_h
            coords.append((x, y))
            elements.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="{color}"/>')
        if len(coords) > 1:
            path_d = " ".join(f"{'M' if k == 0 else 'L'}{x:.1f},{y:.1f}" for k, (x, y) in enumerate(coords))
            elements.append(f'<path d="{path_d}" fill="none" stroke="{color}" stroke-width="2"/>')

    legend_items = []
    for i, (name, _) in enumerate(series):
        color = BAR_COLORS[i % len(BAR_COLORS)]
        legend_items.append(f'<span class="pie-legend__item"><span class="pie-legend__swatch" style="background:{color}"></span>{name}</span>')

    svg = f'<svg viewBox="0 0 {chart_w} {chart_h}" xmlns="http://www.w3.org/2000/svg">\n' + "\n".join(elements) + "\n</svg>"
    title_html = f'<div class="chart__title">{inline(title)}</div>' if title else ""
    legend_html = '<div class="pie-legend">' + "".join(legend_items) + "</div>" if legend_items else ""
    return f'<div class="chart">{title_html}{svg}{legend_html}</div>'


def parse_scatterplot(lines):
    title, items_raw = _parse_kv(lines)
    datasets = []
    for k, v in items_raw:
        try:
            pairs = [(float(xs), float(ys)) for pair in v.split() for xs, ys in [pair.split(",")]]
            if pairs:
                datasets.append((k, pairs))
        except (ValueError, IndexError):
            continue
    if not datasets:
        return ""

    all_x = [x for _, pts in datasets for x, _ in pts]
    all_y = [y for _, pts in datasets for _, y in pts]
    min_x, max_x = min(all_x), max(all_x)
    min_y, max_y = min(all_y), max(all_y)
    if max_x == min_x: max_x = min_x + 1
    if max_y == min_y: max_y = min_y + 1

    chart_w, chart_h = 400, 280
    margin_l, margin_t, margin_b = 50, 20, 40
    inner_w = chart_w - margin_l - 20
    inner_h = chart_h - margin_t - margin_b

    elements = []
    for i, (name, points) in enumerate(datasets):
        color = BAR_COLORS[i % len(BAR_COLORS)]
        for x, y in points:
            sx = margin_l + ((x - min_x) / (max_x - min_x)) * inner_w
            sy = margin_t + inner_h - ((y - min_y) / (max_y - min_y)) * inner_h
            elements.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="4" fill="{color}" stroke="var(--win-white)" stroke-width="1"/>')
    elements.append(f'<line x1="{margin_l}" y1="{margin_t}" x2="{margin_l}" y2="{margin_t + inner_h}" stroke="var(--win-dark-grey)" stroke-width="1"/>')
    elements.append(f'<line x1="{margin_l}" y1="{margin_t + inner_h}" x2="{margin_l + inner_w}" y2="{margin_t + inner_h}" stroke="var(--win-dark-grey)" stroke-width="1"/>')
    for step in range(5):
        vx = min_x + (max_x - min_x) * step / 4
        x = margin_l + (step / 4) * inner_w
        elements.append(f'<text x="{x:.1f}" y="{chart_h - margin_b + 14}" text-anchor="middle" class="barchart-label">{vx:g}</text>')
        vy = min_y + (max_y - min_y) * step / 4
        y = margin_t + inner_h - (step / 4) * inner_h
        elements.append(f'<text x="{margin_l - 6}" y="{y + 4}" text-anchor="end" class="barchart-value">{vy:g}</text>')

    legend_items = []
    for i, (name, _) in enumerate(datasets):
        color = BAR_COLORS[i % len(BAR_COLORS)]
        legend_items.append(f'<span class="pie-legend__item"><span class="pie-legend__swatch" style="background:{color}"></span>{name}</span>')

    svg = f'<svg viewBox="0 0 {chart_w} {chart_h}" xmlns="http://www.w3.org/2000/svg">\n' + "\n".join(elements) + "\n</svg>"
    title_html = f'<div class="chart__title">{inline(title)}</div>' if title else ""
    legend_html = '<div class="pie-legend">' + "".join(legend_items) + "</div>" if legend_items else ""
    return f'<div class="chart">{title_html}{svg}{legend_html}</div>'


def parse_gauge(lines):
    title = value = label = ""
    max_val = 100.0
    for raw in lines:
        line = raw.strip()
        if not line or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k, v = k.strip().lower(), v.strip()
        if k == "title": title = v
        elif k == "value":
            try: value = float(v)
            except ValueError: pass
        elif k == "max":
            try: max_val = float(v)
            except ValueError: pass
        elif k == "label": label = v
    if max_val == 0: max_val = 1

    size = 200
    cx, cy = size // 2, size // 2 + 10
    r = 75
    ratio = min(value / max_val, 1.0)
    needle_angle = -math.pi + math.pi * ratio

    colors = []
    n_segs = 20
    for s in range(n_segs):
        seg_start = -math.pi + (s / n_segs) * math.pi
        seg_end = -math.pi + ((s + 1) / n_segs) * math.pi
        sx1, sy1 = cx + r * math.cos(seg_start), cy + r * math.sin(seg_start)
        sx2, sy2 = cx + r * math.cos(seg_end), cy + r * math.sin(seg_end)
        ix1, iy1 = cx + (r - 12) * math.cos(seg_end), cy + (r - 12) * math.sin(seg_end)
        ix2, iy2 = cx + (r - 12) * math.cos(seg_start), cy + (r - 12) * math.sin(seg_start)
        if s / n_segs <= ratio:
            color = "#109618" if ratio < 0.6 else "#ff9900" if ratio < 0.85 else "#dc3912"
        else:
            color = "var(--win-light-grey)"
        d = f"M{sx1:.1f},{sy1:.1f} A{r},{r} 0 0,1 {sx2:.1f},{sy2:.1f} L{ix1:.1f},{iy1:.1f} A{r - 12},{r - 12} 0 0,0 {ix2:.1f},{iy2:.1f} Z"
        colors.append(f'<path d="{d}" fill="{color}" stroke="var(--win-white)" stroke-width="0.5"/>')

    nx = cx + (r - 20) * math.cos(needle_angle)
    ny = cy + (r - 20) * math.sin(needle_angle)
    needle = f'<line x1="{cx}" y1="{cy}" x2="{nx:.1f}" y2="{ny:.1f}" stroke="var(--win-black)" stroke-width="2"/>'
    needle_dot = f'<circle cx="{cx}" cy="{cy}" r="4" fill="var(--win-black)"/>'
    val_text = f'<text x="{cx}" y="{cy + 22}" text-anchor="middle" class="gauge-value">{value:g}</text>'
    if label:
        val_text += f'\n<text x="{cx}" y="{cy + 34}" text-anchor="middle" class="gauge-label">{inline(label)}</text>'

    svg = f'<svg viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg">\n' + "\n".join(colors) + f"\n{needle}\n{needle_dot}\n{val_text}\n</svg>"
    title_html = f'<div class="chart__title">{inline(title)}</div>' if title else ""
    return f'<div class="chart">{title_html}{svg}</div>'


# ── Inline / block markdown ───────────────────────────────────────

def heading(match):
    level = len(match.group(1))
    text = match.group(2)
    anchor = text.lower().strip()
    anchor = re.sub(r"[^a-z0-9]+", "-", anchor)
    return f'<h{level} id="{anchor}">{inline(text)}</h{level}>'


def paragraph(text):
    return f"<p>{inline(text)}</p>"


def inline(text):
    codes = []
    def stash(m):
        codes.append(m.group(1))
        return f"\x00{len(codes) - 1}\x00"

    text = re.sub(r"``(.+?)``", stash, text)
    text = re.sub(r"`([^`]+)`", stash, text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", text)
    text = re.sub(
        r"!\[\[([^\]]+)\]\]\(([^)]+)\)",
        r'<figure class="thumb"><img src="\2" alt="\1"><figcaption>\1</figcaption></figure>',
        text,
    )
    text = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", r'<img src="\2" alt="\1">', text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)

    for i, code in enumerate(codes):
        text = text.replace(f"\x00{i}\x00", f"<code>{code}</code>")
    return text


# ── Main parser ───────────────────────────────────────────────────

def md_to_html(md):
    lines = md.split("\n")
    html = []
    tags = []
    toc_lines = []
    in_code = False
    in_list = False
    code_block = []
    list_items = []

    def flush_list():
        nonlocal in_list, list_items
        if in_list:
            html.append("<ul>\n" + "\n".join(f"  <li>{inline(item)}</li>" for item in list_items) + "\n</ul>")
            list_items = []
            in_list = False

    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]

        if line.startswith("```"):
            if in_code:
                html.append(f'<pre><code>{chr(10).join(code_block)}</code></pre>')
                code_block = []
                in_code = False
            else:
                flush_list()
                in_code = True
            i += 1
            continue

        if in_code:
            code_block.append(line)
            i += 1
            continue

        m_block = re.match(r"^:::\s*(\w+)", line)
        if m_block and m_block.group(1) in ("infobox", "pie", "barchart", "histogram", "linechart", "scatterplot", "donut", "gauge"):
            block_type = m_block.group(1)
            flush_list()
            body = []
            i += 1
            while i < n and not (lines[i].startswith(":::") and lines[i][3:].strip() == ""):
                body.append(lines[i])
                i += 1
            i += 1
            parsers = {
                "infobox": parse_infobox,
                "pie": parse_pie,
                "barchart": parse_barchart,
                "histogram": parse_histogram,
                "linechart": parse_linechart,
                "scatterplot": parse_scatterplot,
                "donut": parse_donut,
                "gauge": parse_gauge,
            }
            html.append(parsers[block_type](body))
            continue

        if line.startswith("#"):
            flush_list()
            toc_lines.append(line)
            html.append(heading(re.match(r"^(#{1,4})\s+(.+)", line)))
            i += 1
            continue

        if re.match(r"^[-*] ", line):
            in_list = True
            list_items.append(re.sub(r"^[-*] ", "", line))
            i += 1
            continue

        if re.match(r"^\d+\. ", line):
            in_list = True
            list_items.append(re.sub(r"^\d+\. ", "", line))
            i += 1
            continue

        if line.strip().startswith("|"):
            flush_list()
            shadow = i > 0 and lines[i - 1].strip() == "<!-- shadow -->"
            table_lines = []
            while i < n:
                if lines[i].strip().startswith("|"):
                    table_lines.append(lines[i])
                    i += 1
                elif re.match(r"^<!--\s*rowclass:\w+\s*-->$", lines[i].strip()):
                    table_lines.append(lines[i])
                    i += 1
                else:
                    break
            html.append(parse_table(table_lines, shadow))
            continue

        if re.match(r"^!\[\[[^\]]+\]\]\([^)]+\)$", line.strip()) or re.match(r"^!\[[^\]]*\]\([^)]+\)$", line.strip()):
            flush_list()
            html.append(inline(line.strip()))
            i += 1
            continue

        m = re.match(r"^\{\{([\w -]+)\}\}$", line.strip())
        if m:
            flush_list()
            key = m.group(1).strip()
            if key == "search":
                html.append(SEARCH_FORM)
            elif key == "hero":
                html.append(HERO)
            elif key in TAGS:
                tags.append(render_tag(key))
            else:
                html.append(f"{{{{{key}}}}}")
            i += 1
            continue

        if line.strip() == "":
            i += 1
            continue

        flush_list()
        html.append(paragraph(line))
        i += 1

    flush_list()
    if in_code:
        html.append(f'<pre><code>{chr(10).join(code_block)}</code></pre>')

    return "\n".join(tags + html), build_toc(toc_lines)


def md_to_text(md):
    md = md.lstrip()
    md = re.sub(r"^# .*\n", "", md, count=1)
    text = re.sub(r"```.*?```", " ", md, flags=re.DOTALL)
    text = re.sub(r":::.*?:::", " ", text, flags=re.DOTALL)
    text = re.sub(r"\{\{[\w -]+\}\}", " ", text)
    text = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"[`*_>|#]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# ── Page loading ──────────────────────────────────────────────────

def load_pages():
    pages = []
    for md_file in sorted(CONTENT_DIR.glob("*.md")):
        with open(md_file, "r", encoding="utf-8") as f:
            md = f.read()
        meta, body = parse_frontmatter(md)

        title = meta.get("title")
        if not title:
            for line in body.split("\n"):
                line = line.strip()
                if line.startswith("# "):
                    title = line.lstrip("# ").strip()
                    break
        title = title or md_file.stem.replace("-", " ").title()

        pages.append({
            "name": md_file.stem,
            "title": title,
            "topic": meta.get("topic"),
            "icon": meta.get("icon"),
            "categories": meta.get("categories", []),
            "featured": meta.get("featured", "").lower() == "true",
            "md": body,
        })
    return pages


# ── Page builder ──────────────────────────────────────────────────

def build_page(page, pages, body, toc, is_home=False):
    body = body.replace("{{topics}}", build_quick_nav(pages))
    body = body.replace("{{randompage}}", RANDOM_BUTTON)
    body = body.replace("{{featured}}", build_featured_html(pages))
    body = body.replace("{{dyk}}", build_did_you_know())
    body = body.replace("{{searchbox}}", SEARCH_FORM)

    toc_nav = toc if toc else ""
    nav_bar = build_nav_bar(page["name"])
    breadcrumbs = build_breadcrumbs(page) if not is_home else ""
    sidebar = build_sidebar_html(page["name"])
    page_meta = build_page_metadata(page) if not is_home else ""
    related = build_related_articles(page, pages) if not is_home else ""
    footer = build_footer(pages)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{page["title"]} - {config.WG_TITLE_SUFFIX}</title>
  <link rel="stylesheet" href="static/style.css">
  <style>:root {{ --window-max-width: {config.WG_WINDOW_MAX_WIDTH}; }}</style>
  <script>window.WIKI_CONFIG={wiki_config_json()};</script>
  <script src="static/settings.js"></script>
</head>
<body>
  <a class="skip-link" href="#content">Skip to content</a>
  <canvas id="voronoi-bg" class="voronoi-bg" aria-hidden="true"></canvas>

  <div class="desktop">
    <div class="window" role="main">
      <div class="titlebar">
        <button id="sidebar-toggle" class="sidebar-toggle" type="button" aria-label="Toggle navigation" aria-expanded="false">&#9776;</button>
        <span class="titlebar__text">{page["title"]}</span>
        <div class="search">
          <img class="search__icon" src="static/icons/w98_magnifying_glass.png" alt="">
          <input id="search-input" class="search__input" type="text" placeholder="Search" aria-label="Search the wiki" autocomplete="off">
          <div id="search-results" class="search__results"></div>
        </div>
      </div>

      {nav_bar}

      <div class="window-body">
        <aside class="sidebar">
          <a class="sidebar-brand" href="index.html" aria-label="{config.WG_SITENAME} Wiki home">
            <img class="sidebar-brand__logo" src="static/penrose.svg" alt="{config.WG_SITENAME} Wiki">
            <span class="sidebar-brand__text">penrose.wiki</span>
          </a>
          {sidebar}
          <button id="theme-toggle" class="theme-toggle" type="button" aria-pressed="false">Dark mode</button>
          <div class="zoom-control">
            <span class="zoom-control__label">Zoom</span>
            <div class="zoom-control__row">
              <button id="zoom-out" class="zoom-btn" type="button" aria-label="Zoom out">&minus;</button>
              <span id="zoom-label" class="zoom-label">100%</span>
              <button id="zoom-in" class="zoom-btn" type="button" aria-label="Zoom in">+</button>
            </div>
          </div>
          {toc_nav}
        </aside>
        <div class="sidebar-backdrop" id="sidebar-backdrop" aria-hidden="true"></div>
        <article class="content" id="content">
          {breadcrumbs}
          {body}
          {page_meta}
          {related}
        </article>
      </div>

      {footer}
    </div>
  </div>

  <script src="static/voronoi.js"></script>
  <script src="static/search-index.js"></script>
  <script src="static/search.js"></script>
  <script src="static/wiki.js"></script>
</body>
</html>"""


# ── Build ─────────────────────────────────────────────────────────

def build():
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR, onerror=lambda f, p, e: None)
    DIST_DIR.mkdir(exist_ok=True)

    static_out = DIST_DIR / "static"
    shutil.copytree(STATIC_DIR, static_out)

    pages = load_pages()

    # Build category index
    cat_index = build_category_index(pages)

    index_entries = []
    for page in pages:
        body, toc = md_to_html(page["md"])
        is_home = page["name"] == "index"
        html = build_page(page, pages, body, toc, is_home=is_home)
        (DIST_DIR / f'{page["name"]}.html').write_text(html, encoding="utf-8")
        index_entries.append({
            "title": page["title"],
            "url": f'{page["name"]}.html',
            "text": md_to_text(page["md"]),
        })
        print(f'  {page["name"]}.html')

    # Category pages
    for cat_name, cat_pages in sorted(cat_index.items()):
        cat_html = build_category_page_html(cat_name, cat_pages, pages)
        slug = cat_name.lower().replace(" ", "-")
        (DIST_DIR / f"category-{slug}.html").write_text(cat_html, encoding="utf-8")
        print(f"  category-{slug}.html")

    # All pages
    all_pages_html = build_all_pages_html(pages)
    (DIST_DIR / "all-pages.html").write_text(all_pages_html, encoding="utf-8")
    print("  all-pages.html")

    # Random page (JS redirect, built as a simple HTML page)
    page_names = [p["name"] for p in pages if p["name"] not in ("index", "search")]
    random_js = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Random Page</title>
<script>
var pages={json.dumps(page_names)};
window.location.href=pages[Math.floor(Math.random()*pages.length)]+".html";
</script></head><body><p>Redirecting...</p></body></html>"""
    (DIST_DIR / "random.html").write_text(random_js, encoding="utf-8")
    print("  random.html")

    # Search page
    search_body = '<h1 id="search">Search</h1>\n' + SEARCH_FORM + '\n<div id="search-page-results" class="search-page__results"></div>\n'
    search_html = build_page({"name": "search", "title": "Search", "categories": []}, pages, search_body, "")
    (DIST_DIR / "search.html").write_text(search_html, encoding="utf-8")
    print("  search.html")

    # Search index
    index_js = "window.WIKI_INDEX = " + json.dumps(index_entries) + ";\n"
    (static_out / "search-index.js").write_text(index_js, encoding="utf-8")

    print(f"\nBuilt {len(pages) + len(cat_index) + 3} pages to {DIST_DIR}")


if __name__ == "__main__":
    build()
