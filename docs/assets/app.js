const catalog = { articles: [] };
let cardObserver = null;

const $ = (selector) => document.querySelector(selector);
const ui = {
  list: $("#articles"),
  empty: $("#emptyState"),
  error: $("#errorState"),
  count: $("#resultCount"),
  search: $("#searchInput"),
  type: $("#typeFilter"),
  year: $("#yearFilter"),
  sort: $("#sortOrder"),
  clear: $("#clearFilters"),
  total: $("#statTotal"),
  newCount: $("#statNew"),
  archiveCount: $("#statHistorical"),
  scan: $("#statScan"),
};

const escapeHtml = (value) =>
  String(value ?? "").replace(/[&<>"']/g, (character) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#039;",
  })[character]);

const safeUrl = (value) =>
  /^https?:\/\//i.test(String(value ?? "")) ? String(value) : "#";

const normalize = (value) =>
  String(value ?? "")
    .normalize("NFKC")
    .toLocaleLowerCase("en")
    .replace(/\s+/g, " ")
    .trim();

const dateValue = (value) => {
  const time = Date.parse(value || "");
  return Number.isFinite(time) ? time : 0;
};

const displayDate = (value) => {
  const time = dateValue(value);
  if (!time) return value || "Date unavailable";
  return new Intl.DateTimeFormat("en", {
    year: "numeric",
    month: "short",
    day: "numeric",
  }).format(new Date(time));
};

const authors = (article) => {
  if (Array.isArray(article.authors)) return article.authors.join(", ");
  return article.authors || "Authors unavailable";
};

const score = (article) => {
  const raw = article.score;
  if (typeof raw === "number") {
    return { total: raw, priority: "", components: {} };
  }
  return {
    total: Number(raw?.total) || 0,
    priority: raw?.priority || "",
    components: raw?.components || {},
  };
};

const terms = (article) => {
  const groups = article.evidence?.terms || article.terms || {};
  return ["pk", "ai", "method"].flatMap((group) => groups[group] || []);
};

const summary = (article) => article.summary || article.insights || {};

const searchableText = (article) =>
  normalize([
    article.title,
    authors(article),
    article.venue,
    article.doi,
    article.abstract,
    ...Object.values(summary(article)),
    ...terms(article),
  ].join(" "));

const articleYear = (article) => {
  const match = String(article.publication_date || "").match(/^\d{4}/);
  return match ? match[0] : "";
};

const typeBadge = (type) =>
  type === "historical"
    ? '<span class="badge badge-historical"><i></i>Archive selection</span>'
    : '<span class="badge badge-new"><i></i>New article</span>';

const priorityBadge = (value) => {
  if (!value) return "";
  return `<span class="badge badge-${escapeHtml(value.toLowerCase())}">
    ${escapeHtml(value)} relevance
  </span>`;
};

const tagList = (values) => {
  const unique = [...new Set(values.filter(Boolean))].slice(0, 18);
  if (!unique.length) return "<p>No matched terms.</p>";
  return `<div class="tag-list">${unique
    .map((value) => `<span class="tag">${escapeHtml(value)}</span>`)
    .join("")}</div>`;
};

const insight = (number, title, value) => `
  <section class="insight">
    <span class="insight-number">${number}</span>
    <div>
      <h3>${escapeHtml(title)}</h3>
      <p>${escapeHtml(value || "Not stated in the available abstract.")}</p>
    </div>
  </section>
`;

const scoreBreakdown = (components) => {
  const labels = [
    ["PK", components.pk],
    ["AI", components.ai],
    ["Method", components.method],
    ["Intersection", components.intersection],
  ];
  return `<div class="score-breakdown">${labels
    .map(([label, value]) => `
      <span><small>${escapeHtml(label)}</small><strong>${Number(value) || 0}</strong></span>
    `)
    .join("")}</div>`;
};

const articleCard = (article, index) => {
  const articleScore = score(article);
  const articleSummary = summary(article);
  const sourceUrl = safeUrl(article.url);
  const reported = article.reported_at || article.report_date || "Unknown";
  const components = articleScore.components;
  const doi = article.doi
    ? `<span class="doi">DOI&nbsp; ${escapeHtml(article.doi)}</span>`
    : "";
  const sourceLabel = article.venue
    || (Array.isArray(article.sources) ? article.sources.join(", ") : article.source)
    || "Source unavailable";
  const featured = index === 0 ? " paper-card-featured" : "";
  const scoreTotal = Math.min(Math.max(articleScore.total, 0), 100);

  return `
    <article class="paper-card${featured}" id="${escapeHtml(article.id || article.title)}"
             style="--card-order:${index}; --score:${scoreTotal}">
      <span class="folio-index">${String(index + 1).padStart(2, "0")}</span>
      <div class="paper-main">
        <div class="paper-topline">
          <div class="badge-row">
            ${typeBadge(article.selection_type)}
            ${priorityBadge(articleScore.priority)}
          </div>
          <span class="reported-date">Indexed ${escapeHtml(reported)}</span>
        </div>

        <div class="paper-heading">
          <div class="paper-heading-copy">
            <h2 class="paper-title">
              <a href="${escapeHtml(sourceUrl)}" target="_blank" rel="noopener noreferrer">
                ${escapeHtml(article.title)}
              </a>
            </h2>

            <p class="metadata">
              <span>${escapeHtml(authors(article))}</span>
              <span>${escapeHtml(sourceLabel)}</span>
              <span>${escapeHtml(displayDate(article.publication_date))}</span>
            </p>

            <div class="paper-actions">
              <a class="source-link" href="${escapeHtml(sourceUrl)}"
                 target="_blank" rel="noopener noreferrer">
                Open source record <span aria-hidden="true">↗</span>
              </a>
              ${doi}
            </div>
          </div>

          <div class="score-orbit" role="img"
               aria-label="Relevance score ${scoreTotal} out of 100">
            <div class="score-orbit-ring"></div>
            <div class="score-orbit-core">
              <strong>${scoreTotal}</strong>
              <span>/100</span>
            </div>
            <small>scope alignment</small>
          </div>
        </div>

        <div class="insight-grid">
          ${insight("01", "Prior limitation", articleSummary.prior_limitation)}
          ${insight("02", "Methodological contribution", articleSummary.contribution)}
          ${insight("03", "What becomes possible", articleSummary.new_capability)}
          ${insight("04", "Why it matters", articleSummary.significance)}
        </div>
      </div>

      <details class="paper-details">
        <summary>
          <span>Abstract, matched terms, and score construction</span>
          <i aria-hidden="true"></i>
        </summary>
        <div class="details-content">
          <section>
            <h3>Available abstract</h3>
            <p>${escapeHtml(article.abstract || "No abstract was available.")}</p>
          </section>

          <section>
            <h3>Matched terms</h3>
            ${tagList(terms(article))}
          </section>

          <section>
            <h3>Relevance score</h3>
            <p>
              This score measures scope alignment, not scientific quality.
              <a href="./method.html#score">See the scoring method.</a>
            </p>
            ${scoreBreakdown(components)}
          </section>

          <section>
            <h3>Interpretation basis</h3>
            <p>${escapeHtml(
              articleSummary.source
              || "Abstract-only deterministic summary"
            )}</p>
          </section>
        </div>
      </details>
    </article>
  `;
};

const sortArticles = (articles, order) => [...articles].sort((a, b) => {
  if (order === "published-desc") {
    return dateValue(b.publication_date) - dateValue(a.publication_date);
  }
  if (order === "score-desc") {
    return score(b).total - score(a).total
      || dateValue(b.publication_date) - dateValue(a.publication_date);
  }
  const parseReported = (value) =>
    dateValue(String(value || "").replace(" JST", "+09:00").replace(" ", "T"));
  return parseReported(b.reported_at) - parseReported(a.reported_at);
});

const revealCards = () => {
  if (cardObserver) cardObserver.disconnect();
  const cards = [...ui.list.querySelectorAll(".paper-card")];

  if (!("IntersectionObserver" in window)
      || window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    cards.forEach((card) => card.classList.add("is-visible"));
    return;
  }

  cardObserver = new IntersectionObserver((entries) => {
    for (const entry of entries) {
      if (!entry.isIntersecting) continue;
      entry.target.classList.add("is-visible");
      cardObserver.unobserve(entry.target);
    }
  }, { rootMargin: "0px 0px -8%", threshold: 0.08 });

  cards.forEach((card) => cardObserver.observe(card));
};

const render = () => {
  const query = normalize(ui.search.value);
  const selectedType = ui.type.value;
  const selectedYear = ui.year.value;

  const filtered = sortArticles(
    catalog.articles.filter((article) =>
      (!query || searchableText(article).includes(query))
      && (selectedType === "all" || article.selection_type === selectedType)
      && (selectedYear === "all" || articleYear(article) === selectedYear)),
    ui.sort.value,
  );

  ui.list.innerHTML = filtered.map(articleCard).join("");
  ui.list.hidden = filtered.length === 0;
  ui.empty.hidden = filtered.length !== 0;
  ui.count.textContent = `${filtered.length} ${filtered.length === 1 ? "study" : "studies"} in view`;
  revealCards();
};

const populateYears = (years) => {
  for (const year of years) {
    const option = document.createElement("option");
    option.value = year;
    option.textContent = year;
    ui.year.append(option);
  }
};

const bind = () => {
  for (const element of [ui.search, ui.type, ui.year, ui.sort]) {
    element.addEventListener(element === ui.search ? "input" : "change", render);
  }
  ui.clear.addEventListener("click", () => {
    ui.search.value = "";
    ui.type.value = "all";
    ui.year.value = "all";
    ui.sort.value = "reported-desc";
    render();
    ui.search.focus();
  });
};

const addGeometryMotion = () => {
  const figure = document.querySelector(".geometry-study");
  if (!figure || !window.matchMedia("(pointer: fine) and (prefers-reduced-motion: no-preference)").matches) {
    return;
  }

  figure.addEventListener("pointermove", (event) => {
    const bounds = figure.getBoundingClientRect();
    const x = (event.clientX - bounds.left) / bounds.width - 0.5;
    const y = (event.clientY - bounds.top) / bounds.height - 0.5;
    figure.style.setProperty("--tilt-x", `${(-y * 4).toFixed(2)}deg`);
    figure.style.setProperty("--tilt-y", `${(x * 5).toFixed(2)}deg`);
  });

  figure.addEventListener("pointerleave", () => {
    figure.style.setProperty("--tilt-x", "0deg");
    figure.style.setProperty("--tilt-y", "0deg");
  });
};

const load = async () => {
  try {
    const response = await fetch("./articles.json", { cache: "no-store" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const payload = await response.json();

    catalog.articles = Array.isArray(payload.articles) ? payload.articles : [];
    ui.total.textContent = payload.article_count ?? catalog.articles.length;
    ui.newCount.textContent = payload.new_count
      ?? catalog.articles.filter((item) => item.selection_type === "new").length;
    ui.archiveCount.textContent = payload.historical_count
      ?? catalog.articles.filter((item) => item.selection_type === "historical").length;
    ui.scan.textContent = payload.last_scan_at || "—";

    populateYears(payload.years || []);
    bind();
    addGeometryMotion();
    render();
  } catch (error) {
    console.error("Unable to load the article catalog", error);
    ui.count.textContent = "Catalog loading failed.";
    ui.error.hidden = false;
    ui.list.hidden = true;
  }
};

load();
