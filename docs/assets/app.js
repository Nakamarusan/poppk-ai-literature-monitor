const state = {
  articles: [],
  filtered: [],
};

const elements = {
  list: document.querySelector("#articles"),
  empty: document.querySelector("#emptyState"),
  error: document.querySelector("#errorState"),
  count: document.querySelector("#resultCount"),
  search: document.querySelector("#searchInput"),
  type: document.querySelector("#typeFilter"),
  year: document.querySelector("#yearFilter"),
  sort: document.querySelector("#sortOrder"),
  clear: document.querySelector("#clearFilters"),
  statTotal: document.querySelector("#statTotal"),
  statNew: document.querySelector("#statNew"),
  statHistorical: document.querySelector("#statHistorical"),
  statScan: document.querySelector("#statScan"),
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
    .toLocaleLowerCase("ja")
    .replace(/\s+/g, " ")
    .trim();

const parseDateValue = (value) => {
  const time = Date.parse(value || "");
  return Number.isFinite(time) ? time : 0;
};

const displayDate = (value) => {
  const time = parseDateValue(value);
  if (!time) return value || "日付不明";
  return new Intl.DateTimeFormat("ja-JP", {
    year: "numeric",
    month: "short",
    day: "numeric",
  }).format(new Date(time));
};

const flattenTerms = (article) => [
  ...(article.terms?.pk || []),
  ...(article.terms?.ai || []),
  ...(article.terms?.method || []),
];

const searchText = (article) =>
  normalize([
    article.title,
    article.authors,
    article.venue,
    article.doi,
    article.abstract,
    article.insights?.prior_limitation,
    article.insights?.contribution,
    article.insights?.new_capability,
    article.insights?.significance,
    ...flattenTerms(article),
  ].join(" "));

const articleYear = (article) => {
  const match = String(article.publication_date || "").match(/^\d{4}/);
  return match ? match[0] : "";
};

const badgeForType = (type) =>
  type === "historical"
    ? '<span class="badge badge-historical">2020+ archive</span>'
    : '<span class="badge badge-new">New</span>';

const badgeForPriority = (priority) => {
  if (!priority) return "";
  const className = priority.toLowerCase() === "high"
    ? "badge-high"
    : "badge-medium";
  return `<span class="badge ${className}">${escapeHtml(priority)}</span>`;
};

const renderTags = (values) => {
  const tags = [...new Set(values.filter(Boolean))].slice(0, 14);
  if (!tags.length) return "<p>抽出語はありません。</p>";
  return `<div class="tag-list">${tags
    .map((tag) => `<span class="tag">${escapeHtml(tag)}</span>`)
    .join("")}</div>`;
};

const insightBlock = (number, title, value) => `
  <section class="insight">
    <span class="insight-number">${number}</span>
    <h3>${escapeHtml(title)}</h3>
    <p>${escapeHtml(value || "抄録では明示されていません。")}</p>
  </section>
`;

const articleCard = (article) => {
  const sourceUrl = safeUrl(article.url);
  const doi = article.doi
    ? `<span class="doi">DOI: ${escapeHtml(article.doi)}</span>`
    : "";
  const scoreText = Number.isFinite(Number(article.score))
    ? ` / score ${Number(article.score)}`
    : "";
  const typeLabel = article.selection_type === "historical"
    ? "2020年以降の過去論文"
    : "新着論文";
  const reportLabel = article.reported_at || article.report_date || "";
  const tags = flattenTerms(article);
  const id = escapeHtml(article.id || article.title);

  return `
    <article class="paper-card" id="${id}">
      <div class="paper-main">
        <div class="paper-topline">
          ${badgeForType(article.selection_type)}
          ${badgeForPriority(article.priority)}
          <span class="reported-date">${escapeHtml(typeLabel)} · 紹介 ${escapeHtml(reportLabel)}</span>
        </div>

        <h2 class="paper-title">
          <a href="${escapeHtml(sourceUrl)}" target="_blank" rel="noopener noreferrer">
            ${escapeHtml(article.title)}
          </a>
        </h2>

        <p class="metadata">
          <span>${escapeHtml(article.authors || "著者情報なし")}</span>
          <span>${escapeHtml(article.venue || article.source || "掲載元不明")}</span>
          <span>公開 ${escapeHtml(displayDate(article.publication_date))}</span>
        </p>

        <div class="paper-actions">
          <a class="primary-link" href="${escapeHtml(sourceUrl)}"
             target="_blank" rel="noopener noreferrer">原論文を開く</a>
          ${doi}
        </div>

        <div class="insight-grid">
          ${insightBlock("01", "従来の課題", article.insights?.prior_limitation)}
          ${insightBlock("02", "方法・新規性", article.insights?.contribution)}
          ${insightBlock("03", "新たに可能になったこと", article.insights?.new_capability)}
          ${insightBlock("04", "研究上の意義", article.insights?.significance)}
        </div>
      </div>

      <details class="paper-details">
        <summary>抄録・抽出語・判定情報</summary>
        <div class="details-content">
          <h3>抄録抜粋</h3>
          <p>${escapeHtml(article.abstract || "抄録は取得されていません。")}</p>
          <h3>抽出語</h3>
          ${renderTags(tags)}
          <h3>自動判定</h3>
          <p>
            ${escapeHtml(article.priority || "Priority not assigned")}${escapeHtml(scoreText)}
            · ${escapeHtml(article.insights?.source || "要約方法不明")}
          </p>
        </div>
      </details>
    </article>
  `;
};

const populateYears = (years) => {
  const values = Array.isArray(years)
    ? years
    : [...new Set(state.articles.map(articleYear).filter(Boolean))].sort().reverse();
  for (const year of values) {
    const option = document.createElement("option");
    option.value = year;
    option.textContent = year;
    elements.year.append(option);
  }
};

const updateStats = (payload) => {
  elements.statTotal.textContent = String(payload.article_count ?? state.articles.length);
  elements.statNew.textContent = String(
    payload.new_count ?? state.articles.filter((item) => item.selection_type === "new").length
  );
  elements.statHistorical.textContent = String(
    payload.historical_count
      ?? state.articles.filter((item) => item.selection_type === "historical").length
  );
  elements.statScan.textContent = payload.last_scan_at || "—";
};

const sortArticles = (articles, order) => [...articles].sort((a, b) => {
  if (order === "published-desc") {
    return parseDateValue(b.publication_date) - parseDateValue(a.publication_date);
  }
  if (order === "score-desc") {
    return (Number(b.score) || 0) - (Number(a.score) || 0)
      || parseDateValue(b.publication_date) - parseDateValue(a.publication_date);
  }
  return parseDateValue(
    String(b.reported_at || "").replace(" JST", "+09:00").replace(" ", "T")
  ) - parseDateValue(
    String(a.reported_at || "").replace(" JST", "+09:00").replace(" ", "T")
  );
});

const applyFilters = () => {
  const query = normalize(elements.search.value);
  const type = elements.type.value;
  const year = elements.year.value;

  let filtered = state.articles.filter((article) => {
    const queryMatch = !query || searchText(article).includes(query);
    const typeMatch = type === "all" || article.selection_type === type;
    const yearMatch = year === "all" || articleYear(article) === year;
    return queryMatch && typeMatch && yearMatch;
  });

  filtered = sortArticles(filtered, elements.sort.value);
  state.filtered = filtered;
  elements.list.innerHTML = filtered.map(articleCard).join("");
  elements.empty.hidden = filtered.length !== 0;
  elements.list.hidden = filtered.length === 0;
  elements.count.textContent = `${filtered.length}件を表示`;
};

const clearFilters = () => {
  elements.search.value = "";
  elements.type.value = "all";
  elements.year.value = "all";
  elements.sort.value = "reported-desc";
  applyFilters();
  elements.search.focus();
};

const bindEvents = () => {
  elements.search.addEventListener("input", applyFilters);
  elements.type.addEventListener("change", applyFilters);
  elements.year.addEventListener("change", applyFilters);
  elements.sort.addEventListener("change", applyFilters);
  elements.clear.addEventListener("click", clearFilters);
};

const load = async () => {
  try {
    const response = await fetch("./articles.json", { cache: "no-store" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const payload = await response.json();
    state.articles = Array.isArray(payload.articles) ? payload.articles : [];
    populateYears(payload.years);
    updateStats(payload);
    bindEvents();
    applyFilters();
  } catch (error) {
    console.error("Unable to load articles.json", error);
    elements.count.textContent = "読み込みに失敗しました。";
    elements.error.hidden = false;
    elements.list.hidden = true;
  }
};

load();
