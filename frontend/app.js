const API_BASE = window.location.hostname === "127.0.0.1" || window.location.hostname === "localhost"
  ? "http://127.0.0.1:8000" : "";
const labels = { domain: "Domain", hosting: "Hosting", vds: "VDS", license: "Lisans" };
const statusLabels = { active: "Aktif", expired: "Süresi geçti", cancelled: "İptal" };
const $ = (selector) => document.querySelector(selector);

function showError(message) { const banner = $("#error-banner"); banner.textContent = message; banner.classList.remove("hidden"); }
function clearError() { $("#error-banner").classList.add("hidden"); }

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, { headers: { "Content-Type": "application/json" }, ...options });
  if (!response.ok) throw new Error(`API hatası (${response.status})`);
  return response.status === 204 ? null : response.json();
}

function renderAssets(items) {
  const query = $("#search-input").value.trim().toLocaleLowerCase("tr-TR");
  const filtered = items.filter((asset) => !query || `${asset.name} ${asset.vendor || ""}`.toLocaleLowerCase("tr-TR").includes(query));
  $("#record-count").textContent = `${filtered.length} kayıt`;
  $("#asset-rows").innerHTML = filtered.length ? filtered.map((asset) => `
    <tr><td><span class="asset-name">${asset.name}</span><span class="asset-sub">${asset.owner || "Sorumlu belirtilmedi"}</span></td>
    <td>${labels[asset.type] || asset.type}</td><td>${asset.vendor || "—"}</td><td>${asset.expires_at || "—"}</td>
    <td><span class="badge ${asset.status}">${statusLabels[asset.status] || asset.status}</span></td><td>›</td></tr>`).join("")
    : '<tr><td class="empty-state" colspan="6">Filtrelere uyan varlık bulunamadı.</td></tr>';
}

async function loadDashboard() {
  clearError();
  const type = $("#type-filter").value; const status = $("#status-filter").value;
  try {
    const [summary, data] = await Promise.all([
      request("/api/assets/dashboard"),
      request(`/api/assets?limit=100${type ? `&type=${type}` : ""}${status ? `&status=${status}` : ""}`),
    ]);
    $("#total-count").textContent = summary.total; $("#active-count").textContent = summary.active;
    $("#expiring-count").textContent = summary.expiring_90_days; $("#expired-count").textContent = summary.expired;
    renderAssets(data.items);
  } catch (error) {
    showError("Varlık verileri yüklenemedi. API ve veritabanı bağlantısını kontrol edin.");
    $("#asset-rows").innerHTML = '<tr><td class="empty-state" colspan="6">Henüz veri alınamadı.</td></tr>';
  }
}

async function createAsset(event) {
  event.preventDefault(); const form = new FormData(event.target); const payload = Object.fromEntries(form.entries());
  if (!payload.expires_at) delete payload.expires_at; if (!payload.cost) delete payload.cost;
  try { await request("/api/assets", { method: "POST", body: JSON.stringify(payload) }); $("#asset-dialog").close(); event.target.reset(); await loadDashboard(); }
  catch (error) { showError("Varlık kaydedilemedi. API ve veritabanı bağlantısını kontrol edin."); }
}

$("#open-create").addEventListener("click", () => $("#asset-dialog").showModal());
$("#asset-form").addEventListener("submit", createAsset); $("#type-filter").addEventListener("change", loadDashboard);
$("#status-filter").addEventListener("change", loadDashboard); $("#refresh-button").addEventListener("click", loadDashboard);
$("#search-input").addEventListener("input", () => { const query = $("#search-input").value.trim().toLocaleLowerCase("tr-TR"); document.querySelectorAll("#asset-rows tr").forEach((row) => { row.hidden = query && !row.textContent.toLocaleLowerCase("tr-TR").includes(query); }); });
loadDashboard();
