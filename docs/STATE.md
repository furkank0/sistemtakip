# docs/STATE.md — Canlı Proje Durumu

> Her ajan oturum sonunda (veya kesinti öncesi) bu dosyayı günceller. En yeni oturum **en üstte** olmalıdır.

- **Son güncelleyen:** Codex — M0 CI lint düzeltmeleri
- **Tarih:** 2026-10-08
- **Repo:** https://github.com/furkank0/sistemtakip
- **Aktif dal:** `ai/codex/m0-scaffold`
- **Son commit:** `62cd33c` (`docs: record M0 branch status`); lint düzeltmeleri henüz commit edilmedi

## Özet
Proje başlangıç aşamasında. Teknoloji yığını kullanıcı adına değerlendirildi: Python 3.12, FastAPI, SQLAlchemy, Alembic, PostgreSQL 16, APScheduler ve HTMX. M0 temel iskeleti `ai/codex/m0-scaffold` dalında GitHub'a push edildi.

## Tamamlananlar
- [x] Proje kapsamı ve çok-AI çalışma protokolü yazıldı (`AGENTS.md`)
- [x] Canlı durum dosyası oluşturuldu (`docs/STATE.md`)
- [x] Detaylı geliştirme planı yazıldı (`docs/PLAN.md`)
- [x] ChatGPT devir promptu hazırlandı (`CHATGPT_HANDOFF_PROMPT.md`)
- [x] Dört proje belgesi çalışma alanındaki hedef yollarına yerleştirildi
- [x] M0 temel iskeleti eklendi: FastAPI health/version, boş Alembic revizyonu, HTMX için frontend servisi, Caddy proxy ve PostgreSQL Compose tanımı
- [x] `.env.example`, `.gitignore`, README, Ruff/mypy CI ve pre-commit yapılandırması eklendi

## Devam Edenler / Yarım Kalanlar
- M0 henüz tamamlanmadı: yerel ortamda Docker komutu yok, bu nedenle Compose/HTTP doğrulaması yapılamıyor.
- İlk GitHub Actions çalıştırmasında frontend imajı derlemesi başarılı, backend Ruff adımı başarısız oldu. Ruff lint/format ve mypy yerel olarak düzeltme sonrası geçti; yeni commit/push ve CI sonucu bekleniyor.
- CI'da pytest adımı bulunmuyor; frontend için imaj derleme adımı var, ayrı lint adımı yok. Test ekleme/çalıştırma bu oturumda yapılmadı.
- M0 iskeleti `ai/codex/m0-scaffold` dalında `origin`'e push edildi.

## Sıradaki Adımlar
1. Ruff/mypy düzeltmelerini commit edip `ai/codex/m0-scaffold` dalına push et; otomatik CI sonucunu izle.
2. Docker erişimi sağlandığında Compose servislerini ayağa kaldırıp `/health`, `/version` ve `/api/docs` yollarını doğrula.
3. CI'da pytest ve frontend lint eksiklerini tamamlayıp M0 DoD'yi karşıla; ardından değişiklikleri PR akışına taşı.

## Açık Kararlar (Kullanıcıdan Bekleniyor)
- [x] Teknoloji yığını: Python 3.12 + FastAPI + SQLAlchemy/Alembic + PostgreSQL 16 + APScheduler + HTMX
- [ ] Bildirim kanalı (SMTP / Teams / Telegram)
- [ ] Lisans anahtarları platformda saklanacak mı, yoksa sadece parola yöneticisi referansı mı?

## Karar Kayıtları
| Tarih | Karar | Gerekçe | Karar veren |
|---|---|---|---|
| 2026-10-08 | Sıfırdan kurulum; mevcut envanter/sistem yok, import gerekmiyor (M1'de CSV import opsiyonel) | Kullanıcı beyanı | Kullanıcı |
| 2026-10-08 | M0 ve ilk sürüm için FastAPI + PostgreSQL + HTMX yığını seçildi | İç araçta sunucu tarafı HTML akışı, Next.js'e göre daha az frontend bakım yükü sunuyor | Codex (kullanıcının karar verme yetkisi vermesiyle) |

## Bağımlılık Gerekçeleri
- `fastapi`, `sqlalchemy`, `alembic`, `psycopg`, `pydantic-settings`: API, ORM/migration, PostgreSQL bağlantısı ve ortam yapılandırması için.
- `apscheduler`: M2 yenileme uyarıları ve M4 otomatik kontrollerin zamanlanması için; sürüm `3.11.0` sabitlendi.
- `ruff`, `mypy`, `pytest`: CI lint, tür denetimi ve test altyapısı için sabit geliştirme bağımlılıkları.

## Bilinen Sorunlar
- GitHub erişimi ve kimlik doğrulaması çalışıyor; `ai/codex/m0-scaffold` remote dalı yayınlandı.
- Bu çalışma ortamında Docker komutu bulunmuyor; M0 Docker/HTTP doğrulaması yapılamadı.
- CI backend job'ı Ruff kontrolünde hata verdi; mypy adımına ulaşmadı. Ruff lint/format ve mypy düzeltme sonrası yerel bundled Python ile geçti.
- GitHub repo görünürlüğü ve erişim durumu bu çalışma alanından doğrulanmadı.

## Oturum Günlüğü
### 2026-10-08 — Claude
- Kapsam, `AGENTS.md`, `STATE.md` ve `docs/PLAN.md` hazırlandı; ChatGPT devir promptu yazıldı (`CHATGPT_HANDOFF_PROMPT.md`). Kod yazılmadı.
- Proje bundan sonra ChatGPT ile sürdürülecek (kullanıcı kararı).
- Sonraki ajan: yukarıdaki "Sıradaki Adımlar"dan devam et.

<!-- Yeni oturum şablonu:
### YYYY-AA-GG — <ajan>
- Yapılanlar:
- Yarım kalanlar:
- Commit/dal:
- Sonraki ajana not:
-->

### 2026-10-08 — Codex
- Yapılanlar: Arşiv belgeleri incelendi; HTMX yığını seçildi; M0 iskeleti oluşturuldu; GitHub kimlik doğrulamasıyla `ai/codex/m0-scaffold` remote dalına push edildi.
- Yarım kalanlar: Compose/HTTP doğrulaması (Docker/Python yok), pytest ve frontend lint CI kapsamı.
- Commit/dal: `62cd33c` — `ai/codex/m0-scaffold` (`origin/main` tabanlı).
- Sonraki ajana not: Stack seçimi HTMX olarak kaydedildi. M0 henüz DoD'yi karşılamıyor.

### 2026-10-08 — Codex (devam)
- Yapılanlar: GitHub Actions sonucu incelendi (frontend build başarılı, Ruff başarısız); Ruff hataları düzeltildi; Ruff lint/format ve mypy yerel bundled Python ile geçti.
- Yarım kalanlar: Düzeltmelerin commit/push edilmesi ve yeni CI sonucu; Docker/HTTP doğrulaması (Docker komutu yok); pytest/frontend lint CI adımları.
- Commit/dal: Önceki remote commit `62cd33c`; aktif dal `ai/codex/m0-scaffold`.
- Sonraki ajana not: Bu turda test eklenmedi veya çalıştırılmadı; M0 tamamlanmış sayılmıyor.
