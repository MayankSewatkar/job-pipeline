const TIERS = [
  { id: 1, label: "TIER 1 · STRONG MATCH" },
  { id: 2, label: "TIER 2 · WORTH A LOOK" },
  { id: 3, label: "TIER 3 · LOW MATCH" },
];

const STATUS_CYCLE = ["pending_review", "applied", "rejected"];
const STATUS_LABEL = {
  pending_review: "Pending approval",
  applied: "Applied",
  rejected: "Rejected",
};

const LOCAL_OVERRIDES_KEY = "job-pipeline-status-overrides";

let allJobs = [];

function loadOverrides() {
  try {
    return JSON.parse(localStorage.getItem(LOCAL_OVERRIDES_KEY) || "{}");
  } catch {
    return {};
  }
}

function saveOverride(jobId, status) {
  const overrides = loadOverrides();
  overrides[jobId] = status;
  localStorage.setItem(LOCAL_OVERRIDES_KEY, JSON.stringify(overrides));
}

function ringColor(score) {
  if (score >= 85) return "#1e8e5a";
  if (score >= 65) return "#d97706";
  return "#9aa0ab";
}

function timeAgo(iso) {
  if (!iso) return null;
  const diffMs = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diffMs / 60000);
  if (mins < 60) return `${Math.max(mins, 0)}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

function matchesFilters(job, query, statusFilter) {
  const q = query.trim().toLowerCase();
  const textMatch =
    !q ||
    job.title.toLowerCase().includes(q) ||
    job.company.toLowerCase().includes(q);
  const statusMatch = statusFilter === "all" || job.status === statusFilter;
  return textMatch && statusMatch;
}

function buildCard(job, template) {
  const node = template.content.cloneNode(true);
  const card = node.querySelector(".card");

  node.querySelector(".card-title").textContent = job.title;
  node.querySelector(".card-sub").textContent = [job.company, job.location]
    .filter(Boolean)
    .join(" · ");

  const badge = node.querySelector(".status-badge");
  badge.dataset.status = job.status;
  badge.textContent = STATUS_LABEL[job.status] || job.status;
  badge.title = "Click to change status";
  badge.addEventListener("click", () => {
    const next = STATUS_CYCLE[(STATUS_CYCLE.indexOf(job.status) + 1) % STATUS_CYCLE.length];
    job.status = next;
    saveOverride(job.id, next);
    render();
  });

  const postedAgo = timeAgo(job.posted_at);
  const scrapedAgo = timeAgo(job.scraped_at);
  const metaParts = [];
  if (postedAgo) metaParts.push(`Posted ${postedAgo}`);
  if (scrapedAgo) metaParts.push(`Scraped ${scrapedAgo}`);
  node.querySelector(".meta").textContent = metaParts.join(" · ");

  const scoreValue = node.querySelector(".score-value");
  const ringFill = node.querySelector(".ring-fill");
  const color = ringColor(job.score);
  scoreValue.textContent = job.score ?? "–";
  ringFill.style.stroke = color;
  const pct = Math.max(0, Math.min(100, job.score || 0)) / 100;
  const circumference = 176;
  ringFill.style.strokeDasharray = `${circumference}`;
  ringFill.style.strokeDashoffset = `${circumference * (1 - pct)}`;

  if (job.url) {
    card.style.cursor = "pointer";
    card.addEventListener("click", (e) => {
      if (e.target.closest(".status-badge")) return;
      window.open(job.url, "_blank", "noopener");
    });
  }

  return node;
}

function render() {
  const board = document.getElementById("board");
  const template = document.getElementById("job-card-template");
  const query = document.getElementById("search").value;
  const statusFilter = document.getElementById("status-filter").value;

  board.innerHTML = "";

  TIERS.forEach((tier) => {
    const jobsInTier = allJobs
      .filter((j) => j.tier === tier.id)
      .filter((j) => matchesFilters(j, query, statusFilter))
      .sort((a, b) => (b.score || 0) - (a.score || 0));

    const column = document.createElement("section");
    column.className = `column tier-${tier.id}`;

    const header = document.createElement("div");
    header.className = "column-header";
    header.innerHTML = `<span class="dot"></span><span>${tier.label}</span><span class="count">${jobsInTier.length}</span>`;
    column.appendChild(header);

    const body = document.createElement("div");
    body.className = "column-body";

    if (jobsInTier.length === 0) {
      const empty = document.createElement("div");
      empty.className = "empty-column";
      empty.textContent = "No jobs here yet.";
      body.appendChild(empty);
    } else {
      jobsInTier.forEach((job) => body.appendChild(buildCard(job, template)));
    }

    column.appendChild(body);
    board.appendChild(column);
  });
}

async function init() {
  const res = await fetch("data/jobs.json", { cache: "no-store" });
  const data = await res.json();
  const overrides = loadOverrides();

  allJobs = data.jobs.map((j) => ({
    ...j,
    status: overrides[j.id] || j.status || "pending_review",
  }));

  const lastScraped = document.getElementById("last-scraped");
  lastScraped.textContent = data.last_scraped
    ? `Last scraped: ${timeAgo(data.last_scraped)}`
    : "Last scraped: never";

  document.getElementById("search").addEventListener("input", render);
  document.getElementById("status-filter").addEventListener("change", render);

  render();
}

init().catch((err) => {
  document.getElementById("board").innerHTML =
    `<p style="padding:24px;color:#9aa0ab">Couldn't load data/jobs.json — run the scraper first, or check the file path. (${err})</p>`;
});
