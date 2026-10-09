# docs/STATE.md — Canlı Proje Durumu

> Her ajan oturum sonunda (veya kesinti öncesi) bu dosyayı günceller. En yeni oturum **en üstte** olmalıdır.

## 2026-10-09 — Codex — Docker Compose doğrulaması

- **Dal:** `ai/codex/m0-complete`
- **Yapılanlar:** Docker Desktop 4.94.0 kuruldu ve Docker Engine/Compose v5.5.1 doğrulandı. `deploy/docker-compose.yml` stack'i PostgreSQL, backend, frontend ve Caddy proxy ile başarıyla çalışıyor. Backend imajına Alembic dosyaları eklendi ve container başlangıcında `alembic upgrade head` çalışacak şekilde ayarlandı; PostgreSQL üzerinde `0001_initial` ve `0002_assets` migration'ları başarıyla uygulandı. Frontend imajına CSS/JS dosyaları eklendi. Compose proxy kullanımında API'nin aynı origin üzerinden çağrılması düzeltildi.
- **Doğrulama:** `http://127.0.0.1:8080/`, `/health`, `/api/docs`, `/styles.css`, `/app.js` ve `/api/assets/dashboard` HTTP 200 döndü. Chrome üzerinde dashboard arayüzü açıldı; başlangıç verisi olmadığı için özet kartları ve tablo 0 kayıt gösteriyor.
- **Testler:** Önceki backend 6 test, Ruff/mypy ve frontend `node --check` kontrolleri başarılı. Compose build, servis sağlığı ve gerçek PostgreSQL migration akışı başarılı.
- **Yarım kalanlar:** Docker Compose tarafında teknik blokaj kalmadı. Örnek varlık kaydı eklenmedi; kullanıcı arayüzden kendi kayıtlarını girebilir. Yeni terminalde Docker Desktop PATH'i yenilenene kadar mevcut shell'de Docker yolu açıkça eklenebilir.
- **Sıradaki adımlar:** Bu Docker düzeltmelerini commit etmek; M1 kapsamında sağlayıcı/tag ilişkileri ve CSV dışa aktarımını eklemek; ardından M2 yenileme uyarı motoruna geçmek.

## 2026-10-09 — Codex

- **Dal:** `ai/codex/m0-complete`
- **Yapılanlar:** Proje güncellendi; Docker erişiminin olmadığı doğrulandı; yerel geliştirme için SQLite fallback'i eklendi; `alembic upgrade head` başarıyla çalıştı; backend `http://127.0.0.1:8000`, frontend `http://127.0.0.1:5173` adreslerinde başlatıldı. FastAPI endpoint testleri eklendi ve CI'a pytest adımı eklendi. M1'in ilk dilimi olarak `assets` SQLAlchemy modeli, `0002_assets` migration'ı, create/list/detail/update/delete API'ları, tip/durum filtreleri, sayfalama ve `/api/assets/dashboard` özet endpoint'i eklendi. Frontend'e responsive dashboard, özet kartları, varlık tablosu, filtreler, yeni varlık modal formu ve düzenle/sil işlemleri eklendi. Gerçek SQLite dosyasında create/list/delete smoke testi geçti; yeniden çalıştırılabilir VS Code görevleri eklendi.
- **Testler:** `pytest` 6 test geçti; Ruff lint/format, mypy ve frontend `node --check` geçti; OpenAPI rotaları, `/health`, dashboard ve UI HTTP 200 ile doğrulandı.
- **Yarım kalanlar:** Docker Desktop/Engine bu makinede kurulu olmadığı için PostgreSQL + Caddy Compose stack'i ve gerçek PostgreSQL migration testi yapılamadı. Python proje aralığı `>=3.12,<3.13`, makinedeki yerel yorumlayıcı 3.14.2; Docker/üretim uyumluluğu için Python 3.12 kurulmalı.
- **Sıradaki adımlar:** Docker ve Python 3.12 kurulumundan sonra migration'ı PostgreSQL üzerinde çalıştırıp Compose stack'ini proxy üzerinden doğrulamak; sağlayıcı/tag ilişkilerini ve CSV dışa aktarımını eklemek; M1 tamamlanınca yenileme uyarı motoruna geçmek.

- **Son güncelleyen:** Codex — M0 Compose CI sonucu
- **Tarih:** 2026-10-08
- **Repo:** https://github.com/furkank0/sistemtakip
- **Aktif dal:** `ai/codex/m0-scaffold`
- **Son commit:** `f284342` (`ci: validate Docker Compose configuration`)

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
- İlk GitHub Actions çalıştırmasında frontend imajı derlemesi başarılı, backend Ruff adımı başarısız oldu. Düzeltme sonrası ikinci çalıştırmada backend kalite ve frontend imajı adımları başarılı oldu.
- Compose dosyası için CI yapılandırma doğrulaması eklendi ve geçti.
- CI'da pytest adımı bulunmuyor; frontend için imaj derleme adımı var, ayrı lint adımı yok. Test ekleme/çalıştırma bu oturumda yapılmadı.
- M0 iskeleti `ai/codex/m0-scaffold` dalında `origin`'e push edildi.

## Sıradaki Adımlar
1. Docker erişimi sağlandığında Compose servislerini ayağa kaldırıp `/health`, `/version` ve `/api/docs` yollarını doğrula.
2. M0 CI'a pytest/testler ve frontend lint adımlarını ekle; ardından CI kapsamını tamamla.
3. M0 DoD karşılandıktan sonra `ai/codex/m0-scaffold` değişikliklerini PR akışına taşı.

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
- Son GitHub Actions çalıştırması (`37839336795`) başarılı: `compose-config`, `backend-quality` ve `frontend-build` geçti.
- `ai/codex/m0-scaffold` remote ile eşit; çalışma ağacı temiz.
- Test/pytest adımı ve ayrı frontend lint adımı CI'da henüz yok.
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
- Yapılanlar: İlk Ruff hataları düzeltildi; Ruff lint/format ve mypy yerel bundled Python ile geçti; Actions çalıştırması `37839336795` içinde Compose config, backend-quality ve frontend-build başarılı oldu.
- Yarım kalanlar: Docker/HTTP doğrulaması (Docker komutu yok); pytest/testler ve frontend lint CI adımları.
- Commit/dal: `f284342` — `ai/codex/m0-scaffold`; remote ile eşit.
- Sonraki ajana not: Bu turda test eklenmedi veya çalıştırılmadı; M0 tamamlanmış sayılmıyor.
