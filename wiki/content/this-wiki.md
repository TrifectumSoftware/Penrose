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

An optional front-matter block at the top of the file sets the page title, topic, and icon:

```
---
title: My Page
topic: Machines
icon: w98_gears.png
---

# My Page
```

`topic` groups the page on the main page's topic grid; `icon` is the icon shown beside it (any file in `static/icons/`).

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

Or with an explicit separator (same result):

```
| Page | Description |
| ---- | ----------- |
| Welcome | The home page |
| This Wiki | Documentation |
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

## Colored Tables

Add `<!-- rowclass:colorname -->` before a table row to color it. Available colors: blue, red, green, yellow, orange, purple, cyan, grey.

```
<!-- rowclass:green -->
| Item | Value |
| ---- | ----- |
| Good | 100 |
```

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

## Design

The wiki follows these principles:

- **Content first.** Navigation exists to serve content, not the other way around.
- **Scannable structure.** Every page has a clear heading hierarchy. The table of contents in the sidebar reflects the page structure.
- **Predictable layout.** Every page uses the same template. The title bar, sidebar, content area, and scrollbars are consistent.
- **Static-first.** The only scripts are the animated desktop background and client-side search; there is no backend, no framework, and no build tool beyond Python.

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
- `WG_TAGS` — article tag registry (`{{stub}}`, `{{wip}}`, etc.)
- `WG_DEFAULT_THEME` (`light` | `dark` | `auto`), `WG_DEFAULT_ZOOM` — UI defaults
- `WG_ZOOM_MIN`, `WG_ZOOM_MAX`, `WG_ZOOM_STEP` — zoom bounds
- `WG_WINDOW_MAX_WIDTH` — window width
- `WG_VORONOI_*` — background shader colors (light and dark)

Theme and zoom choices are saved to `localStorage` (with a cookie fallback) and carried in the URL on navigation, so they stay consistent across all pages and browser restarts.

## Hosting

Since the built output is committed to the repository, any static file host can serve the wiki directly from the `dist/` directory. GitHub Pages, Netlify, and similar services can be configured to serve from the `wiki/dist/` path.
