# docs/STATE.md — Canlı Proje Durumu

## 2026-10-09 — Codex — Sağlayıcı yönetimi

- **Dal:** `ai/codex/m0-complete`
- **Yapılanlar:** `vendors` tablosu ve geri alınabilir `0004_vendors` migration'ı eklendi. Varlıklar `vendor_id` ile sağlayıcılara bağlandı; eski serbest metin `vendor` alanı geriye dönük uyumluluk için korundu. Sağlayıcı listeleme/oluşturma/silme API'ları, varlık sağlayıcı filtresi ve CSV filtresi eklendi. Ayarlar ekranına sağlayıcı yönetimi, varlık formuna sağlayıcı seçimi ve Varlıklar ekranına sağlayıcı filtresi/sütunu eklendi.
- **Örnek veriler:** Dört demo sağlayıcı oluşturuldu ve dört demo varlıkla ilişkilendirildi. Bu kayıtlar gerçek sistem verisi değildir.
- **Doğrulama:** Compose PostgreSQL üzerinde `0004_vendors` migration'ı uygulandı. Chrome'da Ayarlar ekranında 4 sağlayıcı, Varlıklar ekranında sağlayıcı filtresi ve sağlayıcı sütunu doğrulandı. Backend testleri 9/9, Ruff, frontend `node --check` ve `git diff --check` başarılı.
- **Yarım kalanlar:** Eski serbest metin sağlayıcı kayıtları otomatik normalize edilmiyor; mevcut demo kayıtları yeni ilişki alanına bağlandı. Aylık/yıllık maliyet ayrıştırması ve audit log temeli M1 içinde kaldı.
- **Sıradaki adımlar:** M1'i tamamlamak için maliyet özetini aylık/yıllık ayrıştırmak ve temel audit log'u eklemek; ardından M2 yenileme uyarı motoruna geçmek.

> Her ajan oturum sonunda (veya kesinti öncesi) bu dosyayı günceller. En yeni oturum **en üstte** olmalıdır.

## 2026-10-09 — Codex — Genel Bakış dashboard detayları

- **Dal:** `ai/codex/m0-complete`
- **Yapılanlar:** Genel Bakış yalnızca sayaç gösteren yapıdan çıkarıldı. Yaklaşan yenilemeler tablosu, varlık türü dağılımı ve kayıtlı toplam maliyet özeti eklendi. Yenileme satırları kalan gün sayısını hesaplıyor ve 30 gün altını vurguluyor.
- **Doğrulama:** Frontend Docker imajı yeniden oluşturuldu. Chrome üzerinde 4 demo varlık; `demo-web-hosting` için 42 gün, `demo.example.com` için 84 gün ve toplam `₺30.650` kayıtlı maliyet görünür olarak doğrulandı. `node --check` ve `git diff --check` başarılı.
- **Sıradaki adımlar:** Sağlayıcı yönetimi ve filtresini eklemek; maliyet özetini aylık/yıllık ayrıştırmak; audit log temelini oluşturmak.

## 2026-10-09 — Codex — Sol menü panelleri

- **Dal:** `ai/codex/m0-complete`
- **Yapılanlar:** Sol menü hash tabanlı çalışan sayfa geçişlerine dönüştürüldü. Genel Bakış ve Varlıklar ayrıştırıldı; Kontroller paneline RDAP/WHOIS, TLS, DNS/HTTP ve TCP/ICMP hazırlık kartları eklendi. Ayarlar paneline API bağlantı durumu, Compose PostgreSQL bilgisi ve Swagger bağlantısı eklendi. Aktif menü, sayfa başlığı ve yeni varlık düğmesi seçili panele göre güncelleniyor.
- **Doğrulama:** Frontend Docker imajı yeniden oluşturuldu. Chrome üzerinde `#checks` ve `#settings` ekranları açıldı; Ayarlar ekranı API durumunu `Bağlı`, Kontroller ekranı dört planlanan kontrol kartını gösterdi. `node --check` ve `git diff --check` başarılı.
- **Yarım kalanlar:** Kontroller ekranı şu an hazırlık paneli; uç nokta modeli ve gerçek scheduler M4 aşamasında eklenecek. Sağlayıcı tablosu, maliyet özeti ve temel audit log da M1 içinde kaldı.
- **Sıradaki adımlar:** Sağlayıcı tablosu ve seçim/filtre akışını eklemek; ardından pano maliyet özetini ve audit log temelini tamamlamak.

## 2026-10-09 — Codex — Etiket ilişkileri

- **Dal:** `ai/codex/m0-complete`
- **Yapılanlar:** `tags` ve `asset_tags` tabloları ile geri alınabilir `0003_tags` migration'ı eklendi. Etiket oluşturma/listeleme/silme API'ları, varlık oluşturma/güncellemede `tag_ids`, varlık listesi ve CSV dışa aktarımında `tag_id` filtresi eklendi. Arayüzde etiket filtresi, çoklu etiket seçimi ve tabloda etiket gösterimi eklendi. Mevcut serbest metin sağlayıcı alanı geriye dönük uyumluluk için korundu.
- **Örnek veriler:** Demo ortamına 4 örnek varlık eklendi: domain, hosting, VDS ve lisans. İki demo etiketi kullanılıyor (`Demo - Kritik`, `Demo - Yenileme`); kayıtlar gerçek sistem verisi değildir.
- **Testler:** Backend testleri 8/8 geçti; Ruff, frontend `node --check` ve diff kontrolü başarılı.
- **Doğrulama:** Compose imajları yeniden oluşturuldu; PostgreSQL üzerinde `0003_tags` migration'ı başarıyla uygulandı. Proxy üzerinden tag oluşturma, varlık etiketleme, `tag_id` filtreleme, CSV dışa aktarım ve temizleme smoke testi geçti.
- **Yarım kalanlar:** Sağlayıcıların normalize edilmesi, maliyet özeti ve temel audit log dilimleri kaldı.
- **Sıradaki adımlar:** Sağlayıcı tablosu ve varlık-provider ilişkisine geçmek; sağlayıcı filtresini arayüze taşımak; maliyet özeti eklemek.

## 2026-10-09 — Codex — CSV dışa aktarım

- **Dal:** `ai/codex/m0-complete`
- **Yapılanlar:** `GET /api/assets/export.csv` endpoint'i eklendi. `type` ve `status` filtrelerini destekliyor, tüm varlık alanlarını UTF-8 BOM'lu CSV olarak indiriyor ve Excel uyumluluğu için ek dosya başlığı gönderiyor. Arayüzde seçili filtrelerle çalışan `CSV indir` düğmesi eklendi.
- **Doğrulama:** Compose imajları yeniden oluşturuldu; proxy üzerinden filtreli CSV endpoint'i HTTP 200 döndü. Yanıt `Content-Disposition` ile indirilebilir ve UTF-8 BOM içeriyor.
- **Testler:** Backend testleri 7/7 geçti; Ruff ve frontend `node --check` başarılı.
- **Yarım kalanlar:** M1'de sağlayıcı/tag modelleri, maliyet özeti ve audit log dilimi kaldı. CSV içe aktarım opsiyonel olduğu için bu adımda eklenmedi.
- **Sıradaki adımlar:** Sağlayıcı/tag veri modeline ve migration'ına geçmek; varlık filtrelerini sağlayıcı/etiket ile genişletmek; maliyet özeti ve temel audit log dilimini tamamlamak.

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
