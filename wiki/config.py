"""Penrose Wiki configuration (MediaWiki-style).

Edit these values to customize the wiki, then rebuild with:
    py wiki/build.py

Each setting documents its purpose and default, like MediaWiki's
$wg* variables in LocalSettings.php. Setting names use the WG_
prefix to mirror MediaWiki's $wg* convention.
"""

# --- Site identity (cf. $wgSitename) ---
WG_SITENAME = "Penrose"
WG_TAGLINE = "a wiki of knowledge"
WG_TITLE_SUFFIX = "Penrose Wiki"
WG_LOGO_MAIN = "static/trifectum.png"
WG_LOGO_ICON = "static/penrose.svg"
WG_SOURCE_URL = "https://github.com/anomalyco/penrose"

# --- Navigation sections ---
# Top navigation bar links. Each is (label, url).
WG_NAV_LINKS = [
    ("Home", "index.html"),
    ("Contents", "contents.html"),
    ("All Pages", "all-pages.html"),
]

# Sidebar sections. Each is (heading, [(label, url), ...]).
WG_SIDEBAR_SECTIONS = [
    ("Main", [
        ("Home", "index.html"),
        ("Contents", "contents.html"),
        ("All Pages", "all-pages.html"),
        ("Random Page", "random.html"),
    ]),
    ("Topics", [
        ("Machines", "category-machines.html"),
        ("Resources", "category-resources.html"),
        ("Meta", "category-meta.html"),
    ]),
    ("Community", [
        ("GitHub", "https://github.com/anomalyco/penrose"),
        ("Report a Bug", "https://github.com/anomalyco/penrose/issues"),
    ]),
]

# --- Article tags (cf. MediaWiki message boxes) ---
# name -> (icon filename in static/icons/, title, body).
# Used in articles as {{name}} on its own line.
WG_TAGS = {
    "stub": (
        "w98_msg_information.png",
        "This article is a stub.",
        "You can help by expanding it.",
    ),
    "wip": (
        "w98_msg_warning.png",
        "This refers to unfinished content.",
        "This page is a work in progress.",
    ),
    "outdated": (
        "w98_msg_warning.png",
        "This article may be outdated.",
        "Some information may no longer be accurate.",
    ),
    "disputed": (
        "w98_msg_error.png",
        "The accuracy of this article is disputed.",
        "Please help verify its claims.",
    ),
}

# --- Homepage featured article ---
# Set to a page name (stem) to feature it on the homepage, or None.
WG_FEATURED_PAGE = "drill"

# --- "Did you know..." facts ---
# Randomly displayed on the homepage. Each is a plain-text string
# that may contain [PageName](url) style links.
WG_DID_YOU_KNOW = [
    "Drills extract resources at a rate of 1 per tick?",
    "A furnace can smelt iron ore into iron plates using coal as fuel?",
    "Research ticks unlock new technology at the research bench?",
    "Coal is the primary fuel source in the game?",
    "The wiki is built entirely in Python with zero dependencies?",
]

# --- UI defaults ---
# Theme: "light" | "dark" | "auto" (auto follows the OS setting).
WG_DEFAULT_THEME = "light"

# Zoom factor applied to the wiki window (1.0 = 100%).
WG_DEFAULT_ZOOM = 1.0
WG_ZOOM_MIN = 0.6
WG_ZOOM_MAX = 1.6
WG_ZOOM_STEP = 0.1

# --- Layout ---
# Max width of the wiki window (any valid CSS width).
WG_WINDOW_MAX_WIDTH = "min(1600px, calc(100vw - 100px))"

# --- Voronoi desktop background ---
# Light theme: classic Win95 teal with a slightly lighter cell.
WG_VORONOI_LIGHT_BASE = [0, 128, 128]
WG_VORONOI_LIGHT_CELL = [16, 146, 146]
# Dark theme: near-black teal with a subtle lighter cell.
WG_VORONOI_DARK_BASE = [4, 15, 15]
WG_VORONOI_DARK_CELL = [8, 26, 26]
