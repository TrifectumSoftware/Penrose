/* ============================================================
   Early settings resolution (loaded in <head>, runs before
   first paint to prevent theme/zoom flash).

   Resolves theme + zoom from, in order:
     1. URL query params (?theme=, ?zoom=)
     2. localStorage
     3. cookie fallback
     4. window.WIKI_CONFIG defaults (injected at build time)

   Applies them to <html> and persists back to localStorage +
   cookie so a URL-carried preference survives the next load.
   ============================================================ */
(function () {
  var cfg = window.WIKI_CONFIG || {};
  var root = document.documentElement;

  function getParam(name) {
    try {
      var m = new RegExp("[?&]" + name + "=([^&]*)").exec(window.location.search);
      return m ? decodeURIComponent(m[1]) : null;
    } catch (e) {
      return null;
    }
  }

  function getStore(name) {
    try {
      return localStorage.getItem(name);
    } catch (e) {
      return null;
    }
  }

  function setStore(name, val) {
    try {
      localStorage.setItem(name, val);
    } catch (e) {}
    try {
      document.cookie = name + "=" + encodeURIComponent(val) + ";path=/;max-age=31536000";
    } catch (e) {}
  }

  function getCookie(name) {
    try {
      var m = new RegExp("(?:^|; )" + name + "=([^;]*)").exec(document.cookie);
      return m ? decodeURIComponent(m[1]) : null;
    } catch (e) {
      return null;
    }
  }

  var zMin = cfg.zoomMin != null ? cfg.zoomMin : 0.6;
  var zMax = cfg.zoomMax != null ? cfg.zoomMax : 1.6;

  // --- Theme ---
  var t = getParam("theme") || getStore("theme") || getCookie("theme");
  if (t !== "dark" && t !== "light") t = null;
  var dark;
  if (t) {
    dark = t === "dark";
  } else if (cfg.defaultTheme === "dark") {
    dark = true;
  } else if (cfg.defaultTheme === "light" || !cfg.defaultTheme) {
    dark = false;
  } else {
    // "auto": follow the OS.
    dark = !!(window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches);
  }
  root.classList.toggle("theme-dark", dark);
  setStore("theme", dark ? "dark" : "light");

  // --- Zoom ---
  var zRaw = getParam("zoom") || getStore("zoom") || getCookie("zoom");
  var z = parseFloat(zRaw);
  if (isNaN(z)) z = cfg.defaultZoom != null ? cfg.defaultZoom : 1;
  z = Math.min(zMax, Math.max(zMin, z));
  root.style.setProperty("--ui-zoom", z);
  setStore("zoom", String(z));
})();
