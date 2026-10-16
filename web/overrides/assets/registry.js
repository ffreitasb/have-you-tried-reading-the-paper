/* Progressive enhancement: no source rewriting, HTML injection or network calls. */
(() => {
  "use strict";
  const form = document.querySelector("[data-registry-filter]");
  if (!form) return;
  const article = document.querySelector(".md-content__inner");
  const input = form.querySelector("input");
  const status = form.querySelector("[data-registry-count]");
  const normalize = value => value.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLocaleLowerCase();
  // Search the original text before MathJax adds its accessible duplicates.
  const headings = [];
  const tables = [];
  article.querySelectorAll("h1,h2,h3,h4,h5,h6,table").forEach(element => {
    if (element.tagName !== "TABLE") {
      const level = Number(element.tagName.slice(1));
      headings.length = level;
      headings[level - 1] = element.textContent;
      return;
    }
    const context = headings.join(" ");
    tables.push({ table: element, rows: Array.from(element.querySelectorAll("tbody tr")).map(row => ({
      row, text: normalize(context + " " + row.textContent)
    })) });
  });
  const total = tables.reduce((sum, table) => sum + table.rows.length, 0);
  const pt = status.dataset.locale === "pt-BR";
  const update = () => {
    const terms = normalize(input.value.trim()).split(/\s+/).filter(Boolean);
    let count = 0;
    tables.forEach(({ table, rows }) => {
      let shown = 0;
      rows.forEach(({ row, text }) => {
        row.hidden = !terms.every(term => text.includes(term));
        if (!row.hidden) shown++;
      });
      table.hidden = shown === 0;
      count += shown;
    });
    status.textContent = pt ? `${count} de ${total} entradas. ${count ? "" : "Nenhuma correspondência. Tente outro termo."}` :
      `${count} of ${total} entries. ${count ? "" : "No matches. Try another term."}`;
  };
  form.addEventListener("submit", event => event.preventDefault());
  input.addEventListener("input", update);
  form.addEventListener("reset", () => { input.value = ""; update(); input.focus(); });
  if (total) { form.hidden = false; update(); }
})();
