/* wiki.js — Collapsible TOC and other client-side enhancements */
(function () {
  document.addEventListener("DOMContentLoaded", function () {
    // Collapsible TOC
    var toc = document.querySelector(".toc");
    if (toc) {
      var header = toc.querySelector(".toc__header");
      if (header) {
        header.addEventListener("click", function () {
          toc.classList.toggle("collapsed");
        });
        header.addEventListener("keydown", function (e) {
          if (e.key === "Enter" || e.key === " ") {
            e.preventDefault();
            toc.classList.toggle("collapsed");
          }
        });
      }
    }
  });
})();
