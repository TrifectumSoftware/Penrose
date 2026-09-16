/* ============================================================
   Client-side wiki search.
   Filters the static search index (window.WIKI_INDEX, generated
   at build time) for two surfaces:

   1. The titlebar search box -> live dropdown + Enter goes to
      search.html?q=...
   2. The search results page (search.html) -> reads ?q= from the
      URL and renders full results with highlighted snippets.
   ============================================================ */
(function () {
  var index = window.WIKI_INDEX || [];

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function highlight(text, q) {
    var out = "";
    var lower = text.toLowerCase();
    var ql = q.toLowerCase();
    var i = 0;
    while (ql.length) {
      var j = lower.indexOf(ql, i);
      if (j < 0) {
        out += escapeHtml(text.slice(i));
        break;
      }
      out += escapeHtml(text.slice(i, j));
      out += "<mark>" + escapeHtml(text.slice(j, j + q.length)) + "</mark>";
      i = j + q.length;
      if (i >= text.length) break;
    }
    return out;
  }

  function snippetFor(page, q) {
    var text = page.text;
    var idx = text.toLowerCase().indexOf(q.toLowerCase());
    if (idx >= 0) {
      var start = Math.max(0, idx - 30);
      var end = Math.min(text.length, idx + q.length + 50);
      return (start > 0 ? "..." : "") + text.slice(start, end) + (end < text.length ? "..." : "");
    }
    return text.slice(0, 90) + (text.length > 90 ? "..." : "");
  }

  function search(q) {
    var ql = q.toLowerCase();
    var matches = [];
    for (var i = 0; i < index.length; i++) {
      var hay = (index[i].title + " " + index[i].text).toLowerCase();
      if (hay.indexOf(ql) >= 0) matches.push(index[i]);
    }
    return matches;
  }

  /* --- 1. Titlebar search dropdown --- */
  var input = document.getElementById("search-input");
  var results = document.getElementById("search-results");
  if (input && results) {
    input.addEventListener("input", function () {
      var q = input.value.trim();
      results.innerHTML = "";
      results.style.display = "none";
      if (!q) return;
      var matches = search(q);
      if (!matches.length) return;
      results.style.display = "block";
      for (var m = 0; m < matches.length; m++) {
        var page = matches[m];
        var a = document.createElement("a");
        a.href = page.url;
        a.className = "search-result";

        var t = document.createElement("div");
        t.className = "search-result__title";
        t.innerHTML = highlight(page.title, q);
        a.appendChild(t);

        var s = document.createElement("div");
        s.className = "search-result__snippet";
        s.innerHTML = highlight(snippetFor(page, q), q);
        a.appendChild(s);

        results.appendChild(a);
      }
    });

    input.addEventListener("keydown", function (e) {
      if (e.key === "Enter") {
        var q = input.value.trim();
        if (q) window.location.href = "search.html?q=" + encodeURIComponent(q);
      }
    });

    document.addEventListener("click", function (e) {
      if (e.target !== input) results.style.display = "none";
    });
  }

  /* --- 2. Search results page --- */
  var pageResults = document.getElementById("search-page-results");
  if (pageResults) {
    var pageInput = document.querySelector(".searchbox__input[name='q']");

    function renderPage(q) {
      pageResults.innerHTML = "";
      if (!q) return;
      var matches = search(q);
      if (!matches.length) {
        var none = document.createElement("div");
        none.className = "search-page__none";
        none.textContent = 'No pages match "' + q + '".';
        pageResults.appendChild(none);
        return;
      }
      for (var i = 0; i < matches.length; i++) {
        var page = matches[i];

        var item = document.createElement("div");
        item.className = "search-page__item";

        var a = document.createElement("a");
        a.href = page.url;
        a.className = "search-page__title";
        a.innerHTML = highlight(page.title, q);
        item.appendChild(a);

        var snip = document.createElement("div");
        snip.className = "search-page__snippet";
        snip.innerHTML = highlight(snippetFor(page, q), q);
        item.appendChild(snip);

        pageResults.appendChild(item);
      }
    }

    var params = new URLSearchParams(window.location.search);
    var q = params.get("q") || "";
    if (pageInput) pageInput.value = q;
    renderPage(q);
  }

  /* --- 3. Light / dark mode toggle --- */
  var themeBtn = document.getElementById("theme-toggle");
  if (themeBtn) {
    function isDark() {
      return document.documentElement.classList.contains("theme-dark");
    }
    function updateLabel() {
      var dark = isDark();
      themeBtn.textContent = dark ? "Light mode" : "Dark mode";
      themeBtn.setAttribute("aria-pressed", dark ? "true" : "false");
    }
    themeBtn.addEventListener("click", function () {
      var dark = !isDark();
      document.documentElement.classList.toggle("theme-dark", dark);
      saveSetting("theme", dark ? "dark" : "light");
      updateLabel();
    });
    updateLabel();
  }

  /* --- 4. Zoom control --- */
  var zoomOut = document.getElementById("zoom-out");
  var zoomIn = document.getElementById("zoom-in");
  var zoomLabel = document.getElementById("zoom-label");
  if (zoomOut && zoomIn && zoomLabel) {
    var cfg = window.WIKI_CONFIG || {};
    var ZOOM_MIN = cfg.zoomMin != null ? cfg.zoomMin : 0.6;
    var ZOOM_MAX = cfg.zoomMax != null ? cfg.zoomMax : 1.6;
    var ZOOM_STEP = cfg.zoomStep != null ? cfg.zoomStep : 0.1;

    function getZoom() {
      var v = getComputedStyle(document.documentElement).getPropertyValue("--ui-zoom").trim();
      var z = parseFloat(v);
      return isNaN(z) ? 1 : z;
    }
    function setZoom(z) {
      z = Math.round(z * 10) / 10;
      z = Math.min(ZOOM_MAX, Math.max(ZOOM_MIN, z));
      document.documentElement.style.setProperty("--ui-zoom", z);
      zoomLabel.textContent = Math.round(z * 100) + "%";
      saveSetting("zoom", String(z));
    }

    setZoom(getZoom());
    zoomOut.addEventListener("click", function () { setZoom(getZoom() - ZOOM_STEP); });
    zoomIn.addEventListener("click", function () { setZoom(getZoom() + ZOOM_STEP); });
  }

  /* --- 5. Random page button --- */
  var randomBtn = document.getElementById("random-page");
  if (randomBtn) {
    randomBtn.addEventListener("click", function () {
      var pool = index.filter(function (p) { return p.url !== "index.html"; });
      if (pool.length) {
        var r = pool[Math.floor(Math.random() * pool.length)];
        window.location.href = withSettings(r.url);
      }
    });
  }

  /* --- 6. Mobile sidebar drawer --- */
  var sidebarToggle = document.getElementById("sidebar-toggle");
  var sidebarBackdrop = document.getElementById("sidebar-backdrop");
  if (sidebarToggle) {
    function setSidebar(open) {
      document.body.classList.toggle("sidebar-open", open);
      sidebarToggle.setAttribute("aria-expanded", open ? "true" : "false");
    }
    sidebarToggle.addEventListener("click", function () {
      setSidebar(!document.body.classList.contains("sidebar-open"));
    });
    if (sidebarBackdrop) {
      sidebarBackdrop.addEventListener("click", function () { setSidebar(false); });
    }
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") setSidebar(false);
    });
    var sidebarEl = document.querySelector(".sidebar");
    if (sidebarEl) {
      sidebarEl.addEventListener("click", function (e) {
        var a = e.target && e.target.closest ? e.target.closest("a[href]") : null;
        if (a) setSidebar(false);
      });
    }
  }

  /* --- 7. Settings propagation (ONE zoom, consistent theme) --- */  function saveSetting(name, val) {
    try { localStorage.setItem(name, val); } catch (e) {}
    try { document.cookie = name + "=" + encodeURIComponent(val) + ";path=/;max-age=31536000"; } catch (e) {}
  }

  function appliedTheme() {
    return document.documentElement.classList.contains("theme-dark") ? "dark" : "light";
  }

  function appliedZoom() {
    var v = getComputedStyle(document.documentElement).getPropertyValue("--ui-zoom").trim();
    var z = parseFloat(v);
    return isNaN(z) ? 1 : z;
  }

  function withSettings(href) {
    var url;
    try { url = new URL(href, window.location.href); }
    catch (e) { return href; }
    url.searchParams.set("theme", appliedTheme());
    url.searchParams.set("zoom", String(appliedZoom()));
    return url.toString();
  }

  document.addEventListener("click", function (e) {
    if (e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    var t = e.target;
    var a = t && t.closest ? t.closest("a[href]") : null;
    if (!a) return;
    var href = a.getAttribute("href");
    if (!href || href.charAt(0) === "#" || href.indexOf("://") >= 0 || href.indexOf("mailto:") === 0) return;
    if (href.indexOf(".html") < 0) return;
    e.preventDefault();
    window.location.href = withSettings(href);
  });

  var searchForms = document.querySelectorAll("form.searchbox[action='search.html']");
  for (var f = 0; f < searchForms.length; f++) {
    (function (form) {
      form.addEventListener("submit", function () {
        var th = document.createElement("input");
        th.type = "hidden"; th.name = "theme"; th.value = appliedTheme();
        var zh = document.createElement("input");
        zh.type = "hidden"; zh.name = "zoom"; zh.value = String(appliedZoom());
        form.appendChild(th);
        form.appendChild(zh);
      });
    })(searchForms[f]);
  }
})();
