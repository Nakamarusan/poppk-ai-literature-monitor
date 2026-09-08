/* An isolated renderer keeps an unavailable spotlight from breaking the library. */
(async () => {
  const status = document.querySelector("#spotlightStatus");
  const view = document.querySelector("#spotlightArticle");
  const picker = document.querySelector("#spotlightHistory");
  if (!status || !view || !picker) return;

  // Source metadata and generated text are untrusted, including link labels.
  const escape = (value) => String(value ?? "").replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;",
  })[c]);
  const safeUrl = (value) => {
    try {
      const url = new URL(value);
      return ["https:", "http:"].includes(url.protocol) ? url.href : "#";
    } catch { return "#"; }
  };
  const fields = [
    ["prior_limitation", "Prior limitation"], ["contribution", "Contribution"],
    ["new_capability", "What becomes possible"], ["significance", "Significance"],
  ];

  try {
    const response = await fetch("./flagship.json", { cache: "no-store" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const payload = await response.json();
    const articles = (Array.isArray(payload.articles) ? payload.articles : [])
      .filter((item) => ["Science", "Cell", "Nature"].includes(item.journal))
      .sort((a, b) => String(b.reported_at).localeCompare(String(a.reported_at)));
    if (!articles.length) {
      status.textContent = payload.status === "source unavailable"
        ? "The source is temporarily unavailable. The main literature library is unaffected."
        : "No spotlight selected yet. The daily search favors recent papers and falls back to the 2020+ archive.";
      return;
    }
    status.textContent = `${articles.length} additional paper${articles.length === 1 ? "" : "s"} · Last checked ${payload.last_checked_at || "not recorded"}`;
    if (payload.status === "source unavailable") status.textContent += " · Source temporarily unavailable; showing saved selections.";
    for (const [index, article] of articles.entries()) {
      const option = document.createElement("option");
      option.value = index;
      option.textContent = `${article.reported_at.slice(0, 10)} · ${article.journal} · ${article.title}`;
      picker.append(option);
    }
    picker.closest("label").hidden = false;
    const render = () => {
      const item = articles[Number(picker.value) || 0];
      const connections = Array.isArray(item.connections) ? item.connections : [];
      view.innerHTML = `
        <article class="paper-card spotlight-card">
          <div class="paper-topline">
            <span class="badge badge-new">${escape(item.journal)} · Research spotlight</span>
            <span class="reported-date">Selected ${escape(item.reported_at)}</span>
          </div>
          <p class="paper-kicker">Published ${escape(item.publication_date)} · ${escape(item.selection_type)} selection</p>
          <h3 class="paper-title"><a href="${escape(safeUrl(item.url))}" target="_blank" rel="noopener noreferrer">${escape(item.title)}</a></h3>
          <p class="metadata">${escape((item.authors || []).join(", ") || "Authors unavailable")}</p>
          <div class="insight-grid">${fields.map(([key, label], index) => `
            <section class="insight"><span class="insight-number">0${index + 1}</span><div>
              <h4>${label}</h4><p>${escape(item.summary?.[key] || "Not stated in the available abstract.")}</p>
            </div></section>`).join("")}</div>
          <section class="spotlight-connections" aria-label="Proposed research connections">
            <h4>Connections to your research</h4>
            <p class="detail-note">Proposed uses, not findings established by this paper.</p>
            ${connections.slice(0, 2).map((link) => `<div class="spotlight-connection">
              <strong>${escape(link.topic)}</strong>
              <p>${escape(link.potential_use)}</p>
              <small>Matched in the abstract: ${escape((link.matched_terms || []).join(", "))}</small>
            </div>`).join("")}
          </section>
          <details class="paper-details">
            <summary>Available abstract and selection basis</summary>
            <div class="spotlight-abstract">
              <p>${escape(item.abstract)}</p>
              <p class="detail-note">${escape(item.summary?.source)}. No full text was fetched.</p>
              <p class="detail-note">Selected by the research profile, not the main library's 0–100 relevance score.
                <a href="./method.html#flagship">Read the selection policy.</a></p>
              <a class="source-link" href="${escape(safeUrl(item.url))}" target="_blank" rel="noopener noreferrer">Open source record ↗</a>
            </div>
          </details>
        </article>`;
    };
    picker.addEventListener("change", render);
    render();
  } catch (error) {
    console.error("Flagship spotlight could not be loaded", error);
    status.textContent = "The research spotlight is temporarily unavailable. The main library remains available below.";
  }
})();
