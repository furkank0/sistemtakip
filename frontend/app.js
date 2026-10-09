const API_BASE = window.location.port === "5173" ? "http://127.0.0.1:8000" : "";
const labels = { domain: "Domain", hosting: "Hosting", vds: "VDS", license: "Lisans" };
const statusLabels = { active: "Aktif", expired: "Süresi geçti", cancelled: "İptal" };
const $ = (selector) => document.querySelector(selector);
let editingAssetId = null;

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>'"]/g, (character) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" })[character]);
}

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
    <tr><td><span class="asset-name">${escapeHtml(asset.name)}</span><span class="asset-sub">${escapeHtml(asset.owner || "Sorumlu belirtilmedi")}</span></td>
    <td>${escapeHtml(labels[asset.type] || asset.type)}</td><td>${escapeHtml(asset.vendor || "—")}</td><td>${escapeHtml(asset.expires_at || "—")}</td>
    <td><span class="badge ${escapeHtml(asset.status)}">${escapeHtml(statusLabels[asset.status] || asset.status)}</span></td><td><div class="table-actions"><button class="table-action" data-edit="${asset.id}" type="button">Düzenle</button><button class="table-action delete" data-delete="${asset.id}" type="button">Sil</button></div></td></tr>`).join("")
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

function openCreate() {
  editingAssetId = null; $("#asset-form").reset(); $("#dialog-eyebrow").textContent = "ENVANTERE EKLE"; $("#dialog-title").textContent = "Yeni varlık"; $("#save-asset").textContent = "Kaydet"; $("#asset-dialog").showModal();
}

async function openEdit(assetId) {
  try {
    const asset = await request(`/api/assets/${assetId}`); editingAssetId = asset.id;
    const form = $("#asset-form"); Object.entries(asset).forEach(([key, value]) => { const field = form.elements.namedItem(key); if (field && value != null) field.value = value; });
    $("#dialog-eyebrow").textContent = "ENVANTERİ DÜZENLE"; $("#dialog-title").textContent = "Varlığı düzenle"; $("#save-asset").textContent = "Güncelle"; $("#asset-dialog").showModal();
  } catch (error) { showError("Varlık bilgisi alınamadı."); }
}

async function deleteAsset(assetId) {
  if (!window.confirm("Bu varlığı silmek istediğinize emin misiniz?")) return;
  try { await request(`/api/assets/${assetId}`, { method: "DELETE" }); await loadDashboard(); }
  catch (error) { showError("Varlık silinemedi."); }
}

async function saveAsset(event) {
  event.preventDefault(); const form = new FormData(event.target); const payload = Object.fromEntries(form.entries());
  if (!payload.expires_at) delete payload.expires_at; if (!payload.cost) delete payload.cost;
  try { await request(editingAssetId ? `/api/assets/${editingAssetId}` : "/api/assets", { method: editingAssetId ? "PATCH" : "POST", body: JSON.stringify(payload) }); $("#asset-dialog").close(); event.target.reset(); await loadDashboard(); }
  catch (error) { showError("Varlık kaydedilemedi. API ve veritabanı bağlantısını kontrol edin."); }
}

$("#open-create").addEventListener("click", openCreate);
$("#asset-form").addEventListener("submit", saveAsset); $("#type-filter").addEventListener("change", loadDashboard);
$("#status-filter").addEventListener("change", loadDashboard); $("#refresh-button").addEventListener("click", loadDashboard);
$("#asset-rows").addEventListener("click", (event) => { const editButton = event.target.closest("[data-edit]"); const deleteButton = event.target.closest("[data-delete]"); if (editButton) openEdit(editButton.dataset.edit); if (deleteButton) deleteAsset(deleteButton.dataset.delete); });
$("#search-input").addEventListener("input", () => { const query = $("#search-input").value.trim().toLocaleLowerCase("tr-TR"); document.querySelectorAll("#asset-rows tr").forEach((row) => { row.hidden = query && !row.textContent.toLocaleLowerCase("tr-TR").includes(query); }); });
loadDashboard();
