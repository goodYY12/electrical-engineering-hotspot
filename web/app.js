const $ = (selector) => document.querySelector(selector);
const eventList = $("#eventList");
const form = $("#queryForm");
let snapshot = { events: [], metrics: {}, attempts: [] };
let activeFilter = "全部";

const escapeHtml = (value = "") => String(value).replace(/[&<>'"]/g, (char) => ({
  "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;",
}[char]));

function formatTime(value) {
  if (!value) return "时间未知";
  return new Intl.DateTimeFormat("zh-CN", {
    month: "numeric", day: "numeric", hour: "2-digit", minute: "2-digit", hour12: false,
  }).format(new Date(value));
}

function renderEvents() {
  const events = (snapshot.events || []).filter((event) => activeFilter === "全部" || event.category === activeFilter);
  if (!events.length) {
    eventList.innerHTML = `<div class="empty-state"><div class="empty-orbit"><span></span></div><h3>${snapshot.generated_at ? "当前筛选暂无结果" : "还没有观察记录"}</h3><p>${snapshot.generated_at ? "换一个分类，或调整目标后重新采集。" : "填写目标院校并开始采集。页面只展示实际返回的数据。"}</p></div>`;
    return;
  }
  eventList.innerHTML = events.map((event, index) => {
    const lead = event.items?.[0] || {};
    const evidence = event.evidence_tier === "search_snippet" ? "搜索代理证据" : "官网可见观察";
    const trend = event.trend === "new" ? "● 新出现" : event.trend === "up" ? "↑ 上升" : "— 持平";
    return `<article class="event-card" style="animation-delay:${index * 45}ms">
      <div class="rank">${String(index + 1).padStart(2, "0")}</div>
      <div>
        <div class="event-meta"><span class="tag">${escapeHtml(event.category)}</span><span class="tag ${event.evidence_tier === "search_snippet" ? "proxy" : ""}">${evidence}</span><span class="trend">${trend}</span></div>
        <h3><a href="${escapeHtml(lead.url || "#")}" target="_blank" rel="noopener noreferrer">${escapeHtml(event.title)}</a></h3>
        <p class="event-summary">${escapeHtml(event.summary || "该线索暂未提供摘要，请打开原页核验。")}</p>
        <div class="event-foot"><span class="platforms">${escapeHtml((event.platforms || []).join(" · "))}</span><span>${event.source_count} 个独立来源</span><span>线索指数 ${event.signal_score}</span><span>${formatTime(event.latest_at)}</span></div>
      </div>
    </article>`;
  }).join("");
}

function renderAttempts() {
  const list = $("#attemptList");
  const attempts = snapshot.attempts || [];
  if (!attempts.length) {
    list.innerHTML = '<p class="muted">运行一次采集后显示。</p>';
    return;
  }
  list.innerHTML = attempts.map((attempt) => `<div class="attempt-row ${attempt.outcome === "error" ? "error" : ""}">
    <i></i><span>${escapeHtml(attempt.method.replace("public_search:", ""))}</span><b>${attempt.outcome === "error" ? "失败" : `${attempt.exact_matches} 条`}</b>
  </div>`).join("");
}

function renderSnapshot() {
  renderEvents();
  renderAttempts();
  const metrics = snapshot.metrics || {};
  $("#metricEvents").textContent = metrics.events || 0;
  $("#metricItems").textContent = metrics.exact_items || 0;
  $("#metricPlatforms").textContent = metrics.platforms || 0;
  $("#metricFailures").textContent = metrics.failures || 0;
  $("#updatedAt").textContent = snapshot.generated_at ? `更新于 ${formatTime(snapshot.generated_at)}` : "尚未更新";
  const pill = $("#statusPill");
  const warning = ["indexing_gap", "collection_incomplete", "access_limited"].includes(snapshot.status);
  pill.className = `status-pill ${snapshot.generated_at ? (warning ? "warn" : "ready") : ""}`;
  pill.querySelector("b").textContent = snapshot.status_label || "等待首次采集";
  const limitations = snapshot.limitations || [];
  $("#limitations").hidden = !limitations.length;
  $("#limitationList").innerHTML = limitations.map((text, index) => `<article><b>0${index + 1}</b><br>${escapeHtml(text)}</article>`).join("");
}

async function loadState() {
  try {
    const response = await fetch("/api/state", { cache: "no-store" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    snapshot = await response.json();
    renderSnapshot();
  } catch (error) {
    $("#formError").textContent = `无法读取本地服务：${error.message}`;
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const data = new FormData(form);
  const seedUrls = String(data.get("seed_urls") || "").split(/\r?\n/).map((value) => value.trim()).filter(Boolean);
  const payload = {
    school: data.get("school"), college: data.get("college"), major_code: data.get("major_code"),
    admission_year: Number(data.get("admission_year")), seed_urls: seedUrls,
  };
  $("#formError").textContent = "";
  $("#progress").hidden = false;
  $("#refreshButton").disabled = true;
  try {
    const response = await fetch("/api/refresh", {
      method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload),
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.detail || "采集失败");
    snapshot = result;
    activeFilter = "全部";
    $("#filters .selected")?.classList.remove("selected");
    $('#filters [data-filter="全部"]').classList.add("selected");
    renderSnapshot();
    $("#hot").scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (error) {
    $("#formError").textContent = error.message;
  } finally {
    $("#progress").hidden = true;
    $("#refreshButton").disabled = false;
  }
});

$("#filters").addEventListener("click", (event) => {
  const button = event.target.closest("button[data-filter]");
  if (!button) return;
  activeFilter = button.dataset.filter;
  $("#filters .selected")?.classList.remove("selected");
  button.classList.add("selected");
  renderEvents();
});

$("#themeButton").addEventListener("click", () => {
  const dark = document.documentElement.dataset.theme === "dark";
  document.documentElement.dataset.theme = dark ? "" : "dark";
  localStorage.setItem("hotspot-theme", dark ? "light" : "dark");
});

if (localStorage.getItem("hotspot-theme") === "dark") document.documentElement.dataset.theme = "dark";
loadState();
