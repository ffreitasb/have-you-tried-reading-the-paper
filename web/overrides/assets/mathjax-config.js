/* Local MathJax 3, initialized once after the complete static document exists. */
window.MathJax = {
  tex: { inlineMath: [["\\(", "\\)"]], displayMath: [["\\[", "\\]"]],
    processEscapes: true, packages: { "[+]": ["ams"] } },
  options: { ignoreHtmlClass: ".*|", processHtmlClass: "arithmatex" },
  chtml: { displayAlign: "left", displayIndent: "0" }
};
