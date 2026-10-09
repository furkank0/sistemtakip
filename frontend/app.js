const API_BASE = window.location.port === "5173" ? "http://127.0.0.1:8000" : "";
const labels = { domain: "Domain", hosting: "Hosting", vds: "VDS", license: "Lisans" };
const statusLabels = { active: "Aktif", expired: "Süresi geçti", cancelled: "İptal" };
const auditActionLabels = { create: "Oluşturuldu", update: "Güncellendi", delete: "Silindi" };
const auditEntityLabels = { asset: "Varlık", vendor: "Sağlayıcı", notification: "Bildirim" };
const auditFieldLabels = {
  type: "tür", name: "ad", vendor: "sağlayıcı", vendor_id: "sağlayıcı", owner: "sorumlu",
  cost: "maliyet", currency: "para birimi", cost_period: "maliyet periyodu",
  starts_at: "başlangıç tarihi", expires_at: "bitiş tarihi", auto_renew: "otomatik yenileme",
  reminder_days: "hatırlatma günleri", snoozed_until: "erteleme bitişi",
  support_email: "destek e-postası", panel_url: "panel adresi",
  status: "durum", tag_ids: "etiketler", contact_ids: "irtibat kişileri",
  notes: "not içeriği (değer saklanmaz)",
};
const $ = (selector) => document.querySelector(selector);
let editingAssetId = null;
let editingVendorId = null;
let availableTags = [];
let availableVendors = [];
let availableContacts = [];
let assetPage = 0;
let searchTimer = null;
const pageMeta = {
  dashboard: ["VARLIK YÖNETİMİ", "Genel bakış"],
  assets: ["ENVANTER", "Varlıklar"],
  checks: ["SİSTEM İZLEME", "Kontroller"],
  settings: ["YAPILANDIRMA", "Ayarlar"],
};

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>'"]/g, (character) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" })[character]);
}

function showError(message) { const banner = $("#error-banner"); banner.textContent = message; banner.classList.remove("hidden"); }
function clearError() { $("#error-banner").classList.add("hidden"); }

function navigateTo(section) {
  const selected = pageMeta[section] ? section : "dashboard";
  document.querySelectorAll("[data-page-section]").forEach((panel) => {
    panel.hidden = panel.dataset.pageSection !== selected;
  });
  document.querySelectorAll(".nav-link").forEach((link) => {
    link.classList.toggle("active", link.dataset.section === selected);
  });
  $("#page-eyebrow").textContent = pageMeta[selected][0];
  $("#page-title").textContent = pageMeta[selected][1];
  $("#open-create").hidden = !["dashboard", "assets"].includes(selected);
  if (window.location.hash !== `#${selected}`) history.replaceState(null, "", `#${selected}`);
}

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, { headers: { "Content-Type": "application/json" }, ...options });
  if (!response.ok) throw new Error(`API hatası (${response.status})`);
  return response.status === 204 ? null : response.json();
}

function renderAssets(items, total, offset) {
  $("#record-count").textContent = `${total} kayıt`;
  $("#page-summary").textContent = total
    ? `${offset + 1}–${offset + items.length} / ${total}`
    : "0 kayıt";
  $("#previous-page").disabled = offset === 0;
  $("#next-page").disabled = offset + items.length >= total;
  $("#asset-rows").innerHTML = items.length ? items.map((asset) => `
    <tr><td><span class="asset-name">${escapeHtml(asset.name)}</span><span class="asset-sub">${escapeHtml(asset.owner || "Sorumlu belirtilmedi")}</span>${asset.tags?.length ? `<span class="asset-tags">${asset.tags.map((tag) => escapeHtml(tag.name)).join(" · ")}</span>` : ""}</td>
    <td>${escapeHtml(labels[asset.type] || asset.type)}</td><td>${escapeHtml(asset.vendor || "—")}</td><td>${escapeHtml(asset.expires_at || "—")}</td>
    <td><span class="badge ${escapeHtml(asset.status)}">${escapeHtml(statusLabels[asset.status] || asset.status)}</span></td><td><div class="table-actions"><button class="table-action" data-edit="${asset.id}" type="button">Düzenle</button><button class="table-action delete" data-delete="${asset.id}" type="button">Sil</button></div></td></tr>`).join("")
    : '<tr><td class="empty-state" colspan="6">Filtrelere uyan varlık bulunamadı.</td></tr>';
}

function updateAssetTypeFields(type, clearInactive = false) {
  document.querySelectorAll("[data-type-fields]").forEach((section) => {
    const active = section.dataset.typeFields === type;
    section.hidden = !active;
    if (clearInactive && !active) {
      section.querySelectorAll("input, textarea, select").forEach((field) => { field.value = ""; });
    }
  });
  $("#vendor-label").textContent = type === "domain" ? "Kayıt kuruluşu" : "Sağlayıcı";
}

function renderVendorOptions() {
  const filter = $("#vendor-filter"); const selectedFilter = filter.value;
  filter.innerHTML = '<option value="">Tüm sağlayıcılar</option>' + availableVendors.map((vendor) => `<option value="${vendor.id}">${escapeHtml(vendor.name)}</option>`).join("");
  filter.value = selectedFilter;
  const assetVendor = $("#asset-vendor"); const selectedVendor = assetVendor.value;
  assetVendor.innerHTML = '<option value="">Sağlayıcı seçin</option>' + availableVendors.map((vendor) => `<option value="${vendor.id}">${escapeHtml(vendor.name)}</option>`).join("");
  assetVendor.value = selectedVendor;
  $("#vendor-count").textContent = `${availableVendors.length} kayıt`;
  $("#vendor-list").innerHTML = availableVendors.length ? availableVendors.map((vendor) => `
    <div class="provider-row">
      <div><strong>${escapeHtml(vendor.name)}</strong><span>${escapeHtml(vendor.support_email || "Destek e-postası belirtilmedi")}</span></div>
      <div class="provider-actions">
        ${vendor.panel_url ? `<a class="text-link" href="${escapeHtml(vendor.panel_url)}" target="_blank" rel="noreferrer">Panele git →</a>` : ""}
        <button class="table-action" data-edit-vendor="${vendor.id}" type="button">Düzenle</button>
        <button class="table-action delete" data-delete-vendor="${vendor.id}" type="button">Sil</button>
      </div>
    </div>`).join("") : '<div class="empty-panel">Henüz sağlayıcı eklenmedi.</div>';
}

function resetVendorForm() {
  editingVendorId = null;
  $("#vendor-form").reset();
  $("#save-vendor").textContent = "+ Sağlayıcı ekle";
  $("#cancel-vendor-edit").hidden = true;
}

function renderAuditLog(entries) {
  $("#audit-rows").innerHTML = entries.length ? entries.map((entry) => {
    const fields = entry.action === "update"
      ? Object.keys(entry.diff)
      : Object.keys(entry.diff.created || entry.diff.deleted || {});
    const details = fields.map((field) => auditFieldLabels[field] || field).join(", ") || "Kayıt";
    return `<tr>
      <td>${escapeHtml(new Date(entry.at).toLocaleString("tr-TR"))}</td>
      <td>${escapeHtml(auditActionLabels[entry.action] || entry.action)}</td>
      <td>${escapeHtml(auditEntityLabels[entry.entity] || entry.entity)} #${entry.entity_id}</td>
      <td>${escapeHtml(details)}</td>
      <td>${escapeHtml(entry.actor)}</td>
    </tr>`;
  }).join("") : '<tr><td class="empty-state" colspan="5">Henüz değişiklik kaydı yok.</td></tr>';
}

function renderNotifications(entries) {
  $("#notification-rows").innerHTML = entries.length ? entries.map((entry) => {
    const snoozedUntil = entry.snoozed_until ? Date.parse(entry.snoozed_until) : 0;
    const statusText = entry.status !== "pending"
      ? entry.status
      : snoozedUntil > Date.now()
        ? `Ertelendi: ${new Date(snoozedUntil).toLocaleString("tr-TR")}`
        : "Gönderim bekliyor";
    const snoozeActions = entry.status === "pending"
      ? [1, 3, 7].map((days) => `<button class="table-action" data-snooze-notification="${entry.id}" data-snooze-days="${days}" type="button" aria-label="${days} gün ertele">+${days} gün</button>`).join("")
      : "—";
    return `<tr>
      <td>${escapeHtml(new Date(entry.created_at).toLocaleString("tr-TR"))}</td>
      <td>Varlık #${entry.asset_id}</td>
      <td>${entry.rule === "expired" ? "Süresi doldu" : `${escapeHtml(entry.rule.slice(5))} gün kaldı`}</td>
      <td>${escapeHtml(statusText)}</td>
      <td>${escapeHtml(entry.channel || "Kanal seçilmedi")}</td>
      <td><div class="table-actions">${snoozeActions}</div></td>
    </tr>`;
  }).join("") : '<tr><td class="empty-state" colspan="6">Henüz uyarı kuyruğu boş.</td></tr>';
}

function renderContactOptions() {
  const selected = new Set([...$("#asset-contacts").selectedOptions].map((option) => option.value));
  $("#asset-contacts").innerHTML = availableContacts.map((contact) =>
    `<option value="${contact.id}" ${selected.has(String(contact.id)) ? "selected" : ""}>${escapeHtml(contact.name)}${contact.role ? ` — ${escapeHtml(contact.role)}` : ""}</option>`
  ).join("");
  $("#contact-count").textContent = `${availableContacts.length} kayıt`;
  $("#contact-list").innerHTML = availableContacts.length ? availableContacts.map((contact) => `
    <div class="provider-row">
      <div><strong>${escapeHtml(contact.name)}</strong><span>${escapeHtml([contact.role, contact.email, contact.phone].filter(Boolean).join(" · ") || "İletişim bilgisi belirtilmedi")}</span></div>
      <button class="table-action delete" data-delete-contact="${contact.id}" type="button">Sil</button>
    </div>`).join("") : '<div class="empty-panel">Henüz irtibat kişisi eklenmedi.</div>';
}

function formatCurrency(value, currency) {
  return new Intl.NumberFormat("tr-TR", {
    style: "currency",
    currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
}

function renderCostSummary(costsByCurrency) {
  $("#cost-summary").innerHTML = costsByCurrency.length ? costsByCurrency.map((costs) => `
    <section class="cost-currency">
      <h3>${escapeHtml(costs.currency)}</h3>
      <dl>
        <div><dt>Aylık eşdeğer</dt><dd>${formatCurrency(Number(costs.monthly), costs.currency)}</dd></div>
        <div><dt>Yıllık eşdeğer</dt><dd>${formatCurrency(Number(costs.yearly), costs.currency)}</dd></div>
        <div><dt>Tek seferlik</dt><dd>${formatCurrency(Number(costs.one_time), costs.currency)}</dd></div>
        <div><dt>Periyot belirtilmemiş</dt><dd>${formatCurrency(Number(costs.unspecified), costs.currency)}</dd></div>
      </dl>
    </section>`).join("") : '<div class="empty-panel">Henüz maliyet kaydı bulunmuyor.</div>';
}

function renderOverview(items, costsByCurrency) {
  const today = new Date(); today.setHours(0, 0, 0, 0);
  const upcoming = items.filter((asset) => asset.status === "active" && asset.expires_at)
    .sort((left, right) => left.expires_at.localeCompare(right.expires_at)).slice(0, 5);
  $("#renewal-rows").innerHTML = upcoming.length ? upcoming.map((asset) => {
    const days = Math.ceil((new Date(`${asset.expires_at}T00:00:00`) - today) / 86400000);
    const remaining = days < 0 ? "Süresi geçti" : `${days} gün`;
    return `<tr><td><span class="asset-name">${escapeHtml(asset.name)}</span></td><td>${escapeHtml(labels[asset.type] || asset.type)}</td><td>${escapeHtml(asset.expires_at)}</td><td><span class="remaining ${days <= 30 ? "urgent" : ""}">${remaining}</span></td></tr>`;
  }).join("") : '<tr><td class="empty-state" colspan="4">Yaklaşan yenileme bulunmuyor.</td></tr>';

  const counts = items.reduce((result, asset) => { result[asset.type] = (result[asset.type] || 0) + 1; return result; }, {});
  const maxCount = Math.max(...Object.values(counts), 1);
  $("#type-breakdown").innerHTML = Object.entries(labels).map(([type, label]) => {
    const count = counts[type] || 0;
    return `<div class="breakdown-row"><div><span>${label}</span><strong>${count}</strong></div><div class="progress-track"><span style="width:${(count / maxCount) * 100}%"></span></div></div>`;
  }).join("");
  renderCostSummary(costsByCurrency);
}

async function loadDashboard() {
  clearError();
  const type = $("#type-filter").value; const status = $("#status-filter").value; const tagId = $("#tag-filter").value; const vendorId = $("#vendor-filter").value;
  const limit = Number($("#page-size").value);
  const params = new URLSearchParams({ offset: String(assetPage * limit), limit: String(limit), sort_by: $("#sort-by").value, sort_direction: $("#sort-direction").value });
  const search = $("#search-input").value.trim();
  if (type) params.set("type", type); if (status) params.set("status", status);
  if (tagId) params.set("tag_id", tagId); if (vendorId) params.set("vendor_id", vendorId);
  if (search) params.set("search", search);
  try {
    const [summary, data, overviewAssets, tags, vendors, contacts, auditLog, notifications] = await Promise.all([
      request("/api/assets/dashboard"),
      request(`/api/assets?${params}`),
      request("/api/assets?limit=100"),
      request("/api/tags"),
      request("/api/vendors"),
      request("/api/contacts"),
      request("/api/audit-log?limit=20"),
      request("/api/notifications?limit=20"),
    ]);
    availableTags = tags; availableVendors = vendors; availableContacts = contacts;
    renderTagOptions(); renderVendorOptions(); renderContactOptions();
    renderAuditLog(auditLog); renderNotifications(notifications);
    $("#total-count").textContent = summary.total; $("#active-count").textContent = summary.active;
    $("#expiring-count").textContent = summary.expiring_90_days; $("#expired-count").textContent = summary.expired;
    assetPage = Math.floor(data.offset / limit);
    renderAssets(data.items, data.total, data.offset);
    renderOverview(overviewAssets.items, summary.costs_by_currency);
    const health = await request("/health");
    $("#api-status").textContent = health.status === "ok" ? "Bağlı" : "Kontrol et";
  } catch (error) {
    showError("Varlık verileri yüklenemedi. API ve veritabanı bağlantısını kontrol edin.");
    $("#asset-rows").innerHTML = '<tr><td class="empty-state" colspan="6">Henüz veri alınamadı.</td></tr>';
  }
}

function openCreate() {
  editingAssetId = null; $("#asset-form").reset(); updateAssetTypeFields("domain"); setSelectedTags([]); setSelectedContacts([]); $("#dialog-eyebrow").textContent = "ENVANTERE EKLE"; $("#dialog-title").textContent = "Yeni varlık"; $("#save-asset").textContent = "Kaydet"; $("#asset-dialog").showModal();
}

async function openEdit(assetId) {
  try {
    const asset = await request(`/api/assets/${assetId}`); editingAssetId = asset.id;
    const form = $("#asset-form"); form.reset(); Object.entries(asset).forEach(([key, value]) => { const field = form.elements.namedItem(key); if (field && value != null && key !== "tags" && key !== "contacts" && key !== "vendor") field.value = key === "reminder_days" ? (value.length ? value.join(", ") : "yok") : key === "nameservers" ? value.join(", ") : value; }); updateAssetTypeFields(asset.type); setSelectedTags((asset.tags || []).map((tag) => tag.id)); setSelectedContacts((asset.contacts || []).map((contact) => contact.id));
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
  payload.tag_ids = [...event.target.elements.namedItem("tag_ids").selectedOptions].map((option) => Number(option.value));
  payload.contact_ids = [...event.target.elements.namedItem("contact_ids").selectedOptions].map((option) => Number(option.value));
  const reminderDays = payload.reminder_days.trim();
  payload.reminder_days = reminderDays.toLocaleLowerCase("tr-TR") === "yok" ? [] : reminderDays ? reminderDays.split(",").map((days) => Number(days.trim())) : null;
  const nameservers = payload.nameservers.trim();
  payload.nameservers = nameservers ? nameservers.split(",").map((server) => server.trim()).filter(Boolean) : null;
  ["hosting_plan", "management_url", "ip_address", "operating_system", "product_name"].forEach((key) => {
    payload[key] = payload[key].trim() || null;
  });
  ["vcpu_count", "memory_gb", "storage_gb", "seat_count"].forEach((key) => {
    payload[key] = payload[key] ? Number(payload[key]) : null;
  });
  payload.vendor_id = payload.vendor_id ? Number(payload.vendor_id) : null; delete payload.vendor;
  if (!payload.expires_at) delete payload.expires_at; if (!payload.cost) delete payload.cost;
  try { await request(editingAssetId ? `/api/assets/${editingAssetId}` : "/api/assets", { method: editingAssetId ? "PATCH" : "POST", body: JSON.stringify(payload) }); $("#asset-dialog").close(); event.target.reset(); await loadDashboard(); }
  catch (error) { showError("Varlık kaydedilemedi. API ve veritabanı bağlantısını kontrol edin."); }
}

function renderTagOptions() {
  const filter = $("#tag-filter"); const selectedFilter = filter.value;
  filter.innerHTML = '<option value="">Tüm etiketler</option>' + availableTags.map((tag) => `<option value="${tag.id}">${escapeHtml(tag.name)}</option>`).join("");
  filter.value = selectedFilter;
  const selected = new Set([...$("#asset-tags").selectedOptions].map((option) => option.value));
  $("#asset-tags").innerHTML = availableTags.map((tag) => `<option value="${tag.id}" ${selected.has(String(tag.id)) ? "selected" : ""}>${escapeHtml(tag.name)}</option>`).join("");
}

function setSelectedTags(tagIds) {
  const selected = new Set(tagIds.map(Number));
  [...$("#asset-tags").options].forEach((option) => { option.selected = selected.has(Number(option.value)); });
}

function setSelectedContacts(contactIds) {
  const selected = new Set(contactIds.map(Number));
  [...$("#asset-contacts").options].forEach((option) => { option.selected = selected.has(Number(option.value)); });
}

function exportAssets() {
  const params = new URLSearchParams();
  const type = $("#type-filter").value; const status = $("#status-filter").value; const tagId = $("#tag-filter").value; const vendorId = $("#vendor-filter").value;
  if (type) params.set("type", type); if (status) params.set("status", status);
  if (tagId) params.set("tag_id", tagId);
  if (vendorId) params.set("vendor_id", vendorId);
  window.location.href = `${API_BASE}/api/assets/export.csv?${params}`;
}

$("#open-create").addEventListener("click", openCreate);
document.querySelectorAll(".nav-link").forEach((link) => link.addEventListener("click", (event) => {
  event.preventDefault(); navigateTo(link.dataset.section);
}));
$("#asset-form").addEventListener("submit", saveAsset);
$("#asset-form").elements.namedItem("type").addEventListener("change", (event) => {
  updateAssetTypeFields(event.target.value, true);
});
["type-filter", "status-filter", "tag-filter", "vendor-filter", "sort-by", "sort-direction"].forEach((id) => {
  $(`#${id}`).addEventListener("change", () => { assetPage = 0; loadDashboard(); });
});
$("#page-size").addEventListener("change", () => { assetPage = 0; loadDashboard(); });
$("#previous-page").addEventListener("click", () => { assetPage = Math.max(0, assetPage - 1); loadDashboard(); });
$("#next-page").addEventListener("click", () => { assetPage += 1; loadDashboard(); });
$("#refresh-button").addEventListener("click", loadDashboard); $("#export-button").addEventListener("click", exportAssets);
$("#evaluate-notifications").addEventListener("click", async () => {
  try {
    const result = await request("/api/notifications/evaluate", { method: "POST" });
    $("#notification-result").textContent = `${result.created_count} yeni uyarı kuyruğa eklendi; e-posta gönderilmedi.`;
    await loadDashboard();
  } catch (error) { showError("Yenileme uyarıları değerlendirilemedi."); }
});
$("#notification-rows").addEventListener("click", async (event) => {
  const button = event.target.closest("[data-snooze-notification]");
  if (!button) return;
  const days = Number(button.dataset.snoozeDays);
  try {
    await request(`/api/notifications/${button.dataset.snoozeNotification}/snooze`, {
      method: "POST",
      body: JSON.stringify({ days }),
    });
    $("#notification-result").textContent = `Uyarı ${days} gün ertelendi.`;
    await loadDashboard();
  } catch (error) { showError("Yenileme uyarısı ertelenemedi."); }
});
$("#vendor-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const values = {
    name: $("#vendor-name").value.trim(),
    support_email: $("#vendor-email").value.trim() || null,
    panel_url: $("#vendor-panel").value.trim() || null,
  };
  try {
    const path = editingVendorId ? `/api/vendors/${editingVendorId}` : "/api/vendors";
    await request(path, {
      method: editingVendorId ? "PATCH" : "POST",
      body: JSON.stringify(values),
    });
    resetVendorForm();
    await loadDashboard();
  } catch (error) {
    showError(editingVendorId ? "Sağlayıcı güncellenemedi." : "Sağlayıcı eklenemedi.");
  }
});
$("#cancel-vendor-edit").addEventListener("click", resetVendorForm);
$("#vendor-list").addEventListener("click", async (event) => {
  const editButton = event.target.closest("[data-edit-vendor]");
  const deleteButton = event.target.closest("[data-delete-vendor]");
  if (editButton) {
    const vendor = availableVendors.find((item) => item.id === Number(editButton.dataset.editVendor));
    if (!vendor) return;
    editingVendorId = vendor.id;
    $("#vendor-name").value = vendor.name;
    $("#vendor-email").value = vendor.support_email || "";
    $("#vendor-panel").value = vendor.panel_url || "";
    $("#save-vendor").textContent = "Değişiklikleri kaydet";
    $("#cancel-vendor-edit").hidden = false;
    $("#vendor-name").focus();
    return;
  }
  if (!deleteButton) return;
  const vendor = availableVendors.find((item) => item.id === Number(deleteButton.dataset.deleteVendor));
  if (!vendor || !window.confirm(`"${vendor.name}" sağlayıcısını silmek istiyor musunuz? Bağlı varlıklardaki sağlayıcı kaydı kaldırılır ancak görünen sağlayıcı adı korunur.`)) return;
  try {
    await request(`/api/vendors/${vendor.id}`, { method: "DELETE" });
    if (editingVendorId === vendor.id) resetVendorForm();
    await loadDashboard();
  } catch (error) { showError("Sağlayıcı silinemedi."); }
});
$("#create-contact").addEventListener("click", async () => {
  const name = $("#contact-name").value.trim();
  if (!name) { showError("Kişi adı zorunludur."); return; }
  try {
    await request("/api/contacts", {
      method: "POST",
      body: JSON.stringify({
        name,
        email: $("#contact-email").value.trim() || null,
        phone: $("#contact-phone").value.trim() || null,
        role: $("#contact-role").value.trim() || null,
      }),
    });
    $("#contact-name").value = ""; $("#contact-email").value = "";
    $("#contact-phone").value = ""; $("#contact-role").value = "";
    await loadDashboard();
  } catch (error) { showError("Kişi eklenemedi. Bilgileri ve API bağlantısını kontrol edin."); }
});
$("#contact-list").addEventListener("click", async (event) => {
  const button = event.target.closest("[data-delete-contact]");
  if (!button || !window.confirm("Bu kişiyi tüm varlık bağlantılarından kaldırmak istediğinize emin misiniz?")) return;
  try { await request(`/api/contacts/${button.dataset.deleteContact}`, { method: "DELETE" }); await loadDashboard(); }
  catch (error) { showError("Kişi silinemedi."); }
});
$("#asset-rows").addEventListener("click", (event) => { const editButton = event.target.closest("[data-edit]"); const deleteButton = event.target.closest("[data-delete]"); if (editButton) openEdit(editButton.dataset.edit); if (deleteButton) deleteAsset(deleteButton.dataset.delete); });
$("#search-input").addEventListener("input", () => {
  window.clearTimeout(searchTimer);
  searchTimer = window.setTimeout(() => { assetPage = 0; loadDashboard(); }, 250);
});
window.addEventListener("hashchange", () => navigateTo(window.location.hash.slice(1)));
navigateTo(window.location.hash.slice(1) || "dashboard");
loadDashboard();
