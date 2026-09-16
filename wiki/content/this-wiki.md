---
topic: Meta
categories: Meta
icon: w98_help_book_big.png
---

# This Wiki

How this wiki works, and how to contribute to it.

## Format

Every page is a single markdown file in the `wiki/content/` directory. The filename becomes the URL. A file named `quantum-computing.md` becomes `quantum-computing.html`.

The build script (`wiki/build.py`) reads all `.md` files, converts them to HTML, and writes the output to `wiki/dist/`.

## Adding a Page

1. Create a new `.md` file in `wiki/content/`
2. Optionally add front-matter (see below)
3. Start the file with a heading: `# Your Page Title`
4. Write the content in markdown
5. Run `py wiki/build.py` to regenerate the site
6. Commit the new file and the updated `dist/` output

## Page Metadata

An optional front-matter block at the top of the file sets page properties:

```
---
title: My Page
topic: Machines
categories: Machines, Extraction
icon: w98_gears.png
---

# My Page
```

- `title` — page title shown in the title bar and breadcrumbs
- `topic` — groups the page on the homepage quick-nav grid and generates category pages
- `categories` — comma-separated list of categories; generates `category-*.html` pages
- `icon` — icon shown beside the page in listings (any file in `static/icons/`)

## Categories

Pages tagged with `categories` are automatically grouped into category pages. Each unique category gets its own `category-name.html` page listing all member pages. The sidebar shows category links under the "Topics" section.

## Navigation

The wiki includes several navigation elements:

- **Top nav bar** — horizontal tabs below the titlebar for major sections (Home, Contents, All Pages)
- **Sidebar sections** — grouped navigation links (Main, Topics, Community)
- **Breadcrumbs** — `Home > Topic > Page` trail on every article
- **Related articles** — automatically suggested at the bottom of each page based on shared categories/topic
- **Random page** — button on the homepage redirects to a random page

All navigation is configured in `wiki/config.py` via `WG_NAV_LINKS` and `WG_SIDEBAR_SECTIONS`.

## Homepage Features

The homepage supports special template directives:

- `{{hero}}` — logo and tagline block
- `{{randompage}}` — random page button
- `{{dyk}}` — "Did you know..." facts (configured in `WG_DID_YOU_KNOW`)
- `{{featured}}` — featured article card (configured in `WG_FEATURED_PAGE`)
- `{{topics}}` — quick navigation icon grid

## Article Tags

Banners like "This article is a stub" are added with a tag directive on its own line:

- `{{stub}}` — "This article is a stub."
- `{{wip}}` — "This refers to unfinished content."
- `{{outdated}}` — "This article may be outdated."
- `{{disputed}}` — "The accuracy of this article is disputed."

New tags are defined in the `TAGS` dictionary in `wiki/build.py`.

## Markdown Syntax

The build script supports basic markdown:

- Headings: `# Heading` through `#### Heading`
- Bold: `**bold text**`
- Italic: `*italic text*`
- Inline code: use single backticks for `code`
- Links: `[link text](url)` for internal and external links
- Images and icons: `![alt text](static/icons/w98_gears.png)`
- Thumbnails: `![[caption]](url)` for a right-floated image with a caption
- Lists: `- item` for unordered lists, `1. item` for ordered lists
- Code blocks: triple backticks for fenced code

## Tables

Write tables with pipes. The first row is the header. The separator row (`| --- | --- |`) is optional:

```
| Page | Description |
| Welcome | The home page |
| This Wiki | Documentation |
```

## Colored Tables

Add `<!-- rowclass:colorname -->` before a table row to color it. Available colors: blue, red, green, yellow, orange, purple, cyan, grey.

```
<!-- rowclass:green -->
| Item | Value |
| ---- | ----- |
| Good | 100 |
```

## Infoboxes

A right-floated summary box, the classic Wikimedia element:

```
::: infobox
title = Page Name
image = static/icons/w98_gears.png
caption = Optional caption
Type = Static wiki
Built with = Python
:::
```

The `title` and `image` keys are special; every other `Key = Value` line becomes a label/value row.

## Charts

Charts are rendered as inline SVG via `::: block` syntax. All charts respond to the active theme.

### Pie Chart

```
::: pie
title = Breakdown
Slice A = 40
Slice B = 30
:::
```

### Donut Chart

Same as pie but with a hollow center:

```
::: donut
title = Breakdown
Slice A = 40
Slice B = 30
:::
```

### Bar Chart

Horizontal bars:

```
::: barchart
title = Output
Item A = 100
Item B = 80
:::
```

### Histogram

Vertical bars for frequency distribution:

```
::: histogram
title = Distribution
Bin 1 = 5
Bin 2 = 12
:::
```

### Line Chart

Multiple data series over a sequence (space-separated values):

```
::: linechart
title = Time Series
Series A = 10 20 30 25 40
Series B = 5 15 25 35 30
:::
```

### Scatter Plot

Correlation between two variables (x,y pairs):

```
::: scatterplot
title = Correlation
Dataset = 1,2 3,5 5,8 7,11
:::
```

### Gauge

Single value as a proportion of max:

```
::: gauge
title = Status
value = 75
max = 100
label = percent
:::
```

## Collapsible TOC

The table of contents in the sidebar is collapsible. Click the header to expand/collapse. Controlled by `static/wiki.js`.

## Icons

A library of Win95 icons ships in `static/icons/` (`.png`). Reference them from any page:

- `![Gears](static/icons/w98_gears.png)`
- `![Hardware](static/icons/w98_hardware.png)`
- `![Search](static/icons/w98_magnifying_glass.png)`

Any remote image URL also works, e.g. `![logo](https://example.com/logo.png)`.

## Search

Every page has a search box in the title bar with live suggestions; pressing Enter opens the dedicated [search results page](search.html).

Search works over page titles and body text using a static index (`static/search-index.js`) generated at build time, so no server is required.

## Links

Internal links use relative paths between HTML pages. From the home page, link to another page with `[page name](page-name.html)`.

External links work the same way: `[example](https://example.com)`.

## Footer

Every page includes a footer with site statistics (page count, category count), navigation links, and copyright information.

## Print Styles

The wiki includes print-friendly CSS that hides navigation, sidebars, and decorative elements, leaving only the article content.

## Design

The wiki follows these principles:

- **Content first.** Navigation exists to serve content, not the other way around.
- **Scannable structure.** Every page has a clear heading hierarchy. The table of contents reflects the page structure.
- **Predictable layout.** Every page uses the same template. The title bar, nav bar, sidebar, content area, and footer are consistent.
- **Static-first.** The only scripts are the animated desktop background, client-side search, and TOC toggle; there is no backend, no framework, and no build tool beyond Python.

## Building

The build script requires Python 3 and no external dependencies.

```
py wiki/build.py
```

Output is written to `wiki/dist/`. Open `dist/index.html` in a browser to preview.

## Configuration

Site-wide settings live in `wiki/config.py` (MediaWiki-style `WG_` variables):

- `WG_SITENAME`, `WG_TAGLINE`, `WG_TITLE_SUFFIX` — site identity
- `WG_LOGO_MAIN`, `WG_LOGO_ICON` — logo paths
- `WG_NAV_LINKS` — top navigation bar links
- `WG_SIDEBAR_SECTIONS` — sidebar navigation sections
- `WG_FEATURED_PAGE` — homepage featured article
- `WG_DID_YOU_KNOW` — homepage "Did you know..." facts
- `WG_TAGS` — article tag registry (`{{stub}}`, `{{wip}}`, etc.)
- `WG_DEFAULT_THEME` (`light` | `dark` | `auto`), `WG_DEFAULT_ZOOM` — UI defaults
- `WG_ZOOM_MIN`, `WG_ZOOM_MAX`, `WG_ZOOM_STEP` — zoom bounds
- `WG_WINDOW_MAX_WIDTH` — window width
- `WG_VORONOI_*` — background shader colors (light and dark)

Theme and zoom choices are saved to `localStorage` (with a cookie fallback) and carried in the URL on navigation, so they stay consistent across all pages and browser restarts.

## Hosting

Since the built output is committed to the repository, any static file host can serve the wiki directly from the `dist/` directory. GitHub Pages, Netlify, and similar services can be configured to serve from the `wiki/dist/` path.
