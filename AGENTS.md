# AGENTS.md — Çok-AI Çalışma ve Devir Protokolü

> Bu dosya projede çalışan **tüm AI ajanları** (Claude, ChatGPT, Gemini, Copilot vb.) için bağlayıcıdır.
> Çalışmaya başlamadan önce sırasıyla bu dosyayı ve `docs/STATE.md` dosyasını oku.
> Gerçek durumun tek kaynağı **GitHub reposudur**; sohbet geçmişi kaynak değildir.

## 1. Proje Amacı

Kurum içi kullanım için bir web platformu geliştirmek:

- **Varlık/lisans takibi:** domain, hosting, VDS sunucular ve lisanslı ürünlerin (başlangıç/bitiş tarihi, yenileme, maliyet, sorumlu, sağlayıcı) merkezi takibi.
- **Yenileme uyarıları:** bitişe kalan gün eşiklerinde (örn. 60/30/14/7/1) bildirim.
- **Günlük rutin kontrollerin standardizasyonu:** tekrar eden checklist şablonları, tamamlanma kaydı, geçmiş raporu.
- **Aktif sistem takibi:** otomatik kontroller (domain RDAP/WHOIS expiry, TLS sertifika expiry, DNS çözümleme, HTTP/TCP/ICMP erişilebilirlik).
- **Denetlenebilirlik:** her değişiklik audit log'a yazılır.

## 2. Kullanıcı ve Ortam Bağlamı

- Kullanıcı: kurum içi IT / sistem yöneticisi. İletişim dili **Türkçe**.
- Hedef ortam: Ubuntu Linux sunucu, Docker Compose ile dağıtım; altyapıda vSphere/ESXi ve firewall (Sophos/WatchGuard vb.) bulunur.
- Kimlik doğrulama hedefi (sonraki aşama): LDAP/AD entegrasyonu.
- Kullanıcı tercihi: adım adım, doğrudan, teknik derinliği yüksek, gereksiz dolgu olmayan yanıtlar; kritik işlemlerde **önce onay**.

## 3. Teknoloji Yığını

> **Seçildi:** M0 ve ilk sürüm için aşağıdaki yığın kullanılacak. Karar `docs/STATE.md`'ye kaydedildi.

- Backend: Python FastAPI + SQLAlchemy + Alembic
- Veritabanı: PostgreSQL
- Zamanlayıcı: APScheduler (başlangıç), gerekirse Celery beat
- Frontend: HTMX + Jinja2 — Next.js'e göre daha küçük bakım yüzeyi
- Dağıtım: Docker Compose, reverse proxy arkasında (TLS)
- Bildirim: SMTP e-posta (v1); Teams webhook / Telegram sonraki aşama

## 4. Veri Modeli Taslağı (v0)

| Tablo | Ana alanlar |
|---|---|
| `assets` | id, type (`domain`\|`hosting`\|`vds`\|`license`), name, vendor, owner, cost, currency, starts_at, expires_at, auto_renew, status, notes |
| `asset_endpoints` | asset_id, kind (`fqdn`\|`ip`\|`url`), value, check_profile |
| `credential_refs` | asset_id, vault_ref (parola yöneticisi referansı — **düz metin sır tutulmaz**) |
| `check_templates` | id, name, frequency (`daily`\|`weekly`…), items[] |
| `check_runs` | id, template_id, run_date, performed_by, status |
| `check_results` | run_id, item_id, result (`ok`\|`warn`\|`fail`\|`na`), note |
| `auto_checks` | id, asset_id, type (`rdap`\|`tls`\|`dns`\|`http`\|`tcp`\|`icmp`), schedule, last_result |
| `notifications` | id, asset_id, rule, channel, sent_at |
| `audit_log` | id, actor, action, entity, entity_id, diff, at |

## 5. Çalışma Kuralları (Tüm Ajanlar İçin)

**Oturum başı**
1. `git pull` ile son durumu al.
2. `AGENTS.md` ve `docs/STATE.md` oku; "Sıradaki adım" ve "Yarım kalanlar"dan devam et.
3. Çelişki veya belirsizlik varsa tahmin yürütme; kullanıcıya sor ve cevabı Karar Kayıtları'na yaz.

**Git**
- Dal adı: `ai/<ajan>/<kısa-konu>` (örn. `ai/gemini/asset-crud`). `main`'e doğrudan push yok; PR veya kullanıcı onaylı merge.
- Küçük, atomik commit. Conventional Commits: `feat:`, `fix:`, `docs:`, `refactor:`, `chore:`, `test:`.
- Commit mesajı sonuna ajan imzası: `Agent: claude | chatgpt | gemini | other`.
- Başka ajanın yarım bıraktığı dalı ezme; devam edeceksen yeni commit ekle.

**Güvenlik**
- Repoya **asla** girmeyecekler: parola, API anahtarı, token, lisans anahtarı, private key, `.env`, gerçek müşteri/sunucu verisi. Yalnızca `.env.example` commit edilir.
- Lisans anahtarı/kimlik bilgisi saklanacaksa: alan düzeyinde şifreleme (AES-GCM / libsodium), anahtar ortam değişkeninden; loglara asla yazılmaz. v1'de tercih: sadece `vault_ref`.
- Üretim sistemlerine bağlanan her kod varsayılan olarak **read-only** olur; yazma/silme işlemleri kullanıcı onayı ister.
- Bağımlılık eklerken sürüm sabitle ve gerekçesini `docs/STATE.md`'ye yaz.

**Kalite**
- Her özellik için en az bir test; migration'lar geri alınabilir olmalı.
- Hata mesajları ve audit log'da hassas veri sızdırma.
- Kod, identifier ve commit mesajları İngilizce; kullanıcıyla iletişim ve `docs/` içeriği Türkçe.

## 6. Oturum Sonu / Kesinti Protokolü (ZORUNLU)

Kredi, token veya bağlam sınırı yaklaştığında (ya da kullanıcı "devir al" dediğinde) **hemen**:

1. Çalışan her şeyi commit et (yarımsa `wip:` önekiyle) ve push et.
2. `docs/STATE.md` dosyasını güncelle: yapılanlar, yarım kalanlar, sıradaki somut adım, açık kararlar, bilinen hatalar.
3. Kullanıcıya şu formatta **DEVİR ÖZETİ** ver:
   - Son commit hash / dal
   - Tamamlananlar (madde madde)
   - Yarım kalan iş + tam olarak nerede kaldığı
   - Sıradaki 3 adım
   - Kullanıcıdan beklenen onay/bilgi

Not: Ajanlar kendi kalan kredisini her zaman göremez. Bu yüzden `docs/STATE.md` her anlamlı adımdan sonra güncel tutulur; kesinti anında devir hazır olmalıdır.

## 7. Yol Haritası

> Ayrıntılı görevler, bitti tanımları ve mimari için `docs/PLAN.md` dosyasına bak.

- [ ] **M0** — Repo iskeleti, Docker Compose, CI (lint + test), `.env.example`
- [ ] **M1** — Varlık CRUD (domain/hosting/VDS/lisans) + bitiş tarihine göre pano
- [ ] **M2** — Yenileme uyarı motoru (eşikler, e-posta)
- [ ] **M3** — Günlük checklist şablonları ve çalıştırma kaydı
- [ ] **M4** — Otomatik kontroller (RDAP, TLS expiry, DNS, HTTP/TCP/ICMP)
- [ ] **M5** — Kimlik doğrulama (yerel + LDAP/AD), rol modeli, audit log
- [ ] **M6** — Raporlama, CSV/PDF dışa aktarım, sağlayıcı API entegrasyonları
