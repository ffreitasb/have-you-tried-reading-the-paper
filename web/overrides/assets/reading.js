/* Expose overflowing reading surfaces to keyboard users after font/math layout. */
(() => {
  "use strict";
  const pt = document.documentElement.lang === "pt-BR";
  const label = pt ? "Conteúdo com rolagem horizontal" : "Horizontally scrollable content";
  const enhance = () => {
    document.querySelectorAll("div.arithmatex,.md-typeset__scrollwrap,table,pre>code").forEach(element => {
      if (element.scrollWidth > element.clientWidth + 1) {
        element.tabIndex = 0;
        element.setAttribute("role", "region");
        element.setAttribute("aria-label", label);
      }
    });
  };
  window.addEventListener("resize", enhance, { passive: true });
  if (document.fonts) document.fonts.ready.then(enhance);
  if (window.MathJax?.startup?.promise) window.MathJax.startup.promise.then(enhance);
  enhance();
})();
