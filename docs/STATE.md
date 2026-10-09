# docs/STATE.md — Canlı Proje Durumu

## 2026-10-09 16:55 — Copilot — M2 yenilendi akışı

- **Git durumu:** `ai/codex/m0-complete`; bu özellik ve teslim kaydı commit/push bekliyor.
- **Yapılanlar:** `POST /api/assets/{id}/renew` yeni bitiş tarihi doğrulamasıyla eklendi. Yenileme, süresi geçmiş varlığı aktif eder; eski döneme ait bekleyen bildirimleri `renewed` durumuna geçirip asset ve bildirim değişikliklerini audit'e yazar. Uyarı kuyruğundan açılan modal yeni tarihi alıyor; yeni expiry değeri yeni bildirim döngüsünün anahtarıdır. İptal edilmiş, bitiş tarihi olmayan ya da bitiş tarihi ileri alınmayan varlıklar reddedilir.
- **Değişen dosyalar:** [backend/app/api.py](../backend/app/api.py), [backend/app/schemas.py](../backend/app/schemas.py), [backend/tests/test_main.py](../backend/tests/test_main.py), [frontend/app.js](../frontend/app.js), [frontend/index.html](../frontend/index.html), [docs/PLAN.md](./PLAN.md), [docs/STATE.md](./STATE.md), [docs/AI_SESSION_LOG.md](./AI_SESSION_LOG.md).
- **Doğrulama:** Backend pytest 19/19; Ruff check/format, mypy, Pylance diagnostics, `node --check` ve `git diff --check` başarılı. Backend ve frontend Compose imajları build edilip başlatıldı; `/health` `ok`. Tarayıcı API mock'u ile modal, min tarih, POST payload ve başarı mesajı doğrulandı; kapat/vazgeç eylemleri POST göndermiyor. UI testinde gerçek veritabanına yazılmadı. Bağımlılıklardan Python 3.14 deprecation uyarıları devam ediyor.
- **Yarım kalanlar / bilinenler:** SMTP e-posta/digest, kullanıcı kanal kararı beklediğinden kapalı. Bildirim eyleminin tarayıcı testi API mock'u ile yapılmış; backend davranışı gerçek DB'li pytest ile test edilmiştir.
- **Sıradaki sıra:** 1) Kullanıcı bildirim kanalını seçene kadar dış gönderimi kapalı tut. 2) M2 teslim/durum kaydını push et. 3) M3 checklist şablonlarının CRUD ve çalıştırma akışına geç.
- **Kullanıcıdan beklenen:** E-posta/SMTP, Teams veya Telegram kanal tercihi.

## 2026-10-09 16:39 — Copilot — Responsive arayüz teslim kaydı

- **Git durumu:** `ai/codex/m0-complete`; responsive arayüz `5b9b845`, durum/günlük kaydı `c3ea5bf` commit'leriyle `origin/ai/codex/m0-complete` dalına push edildi; yerel ve uzak HEAD eşit, çalışma ağacı temiz.
- **Yapılanlar:** Ana içerik alanının sabit kenar çubuğuyla toplam genişliği aşması giderildi. 800px altında menü üstte iki sütunlu navigasyona geçiyor; panolar, formlar, başlıklar, varlık filtreleri ve sayfalama dar ekranlara uyarlanıyor. Dar ekranda geniş tablolar kendi içinde kaydırılıyor; audit ayrıntıları kısa gösterilip tam alan listesi `title` içinde tutuluyor.
- **Değişen dosyalar:** [frontend/styles.css](../frontend/styles.css), [frontend/app.js](../frontend/app.js), [docs/STATE.md](./STATE.md), [docs/AI_SESSION_LOG.md](./AI_SESSION_LOG.md).
- **Doğrulama:** `node --check frontend/app.js`, `git diff --check` başarılı. Compose frontend yeniden build edildi; `/health` `ok`. Tarayıcıda dashboard/varlıklar/ayarlar 350, 750 ve 1280 CSS px genişliklerinde kontrol edildi; sayfa geneli yatay taşma yok, tablo kaydırmaları kendi kapsayıcısında. 350px mobil görünümünde navigasyon ve sağlayıcı formu görsel olarak kontrol edildi.
- **Yarım kalanlar / bilinenler:** M2 yenilendi akışı ve kanal seçimine bağlı e-posta/digest bekliyor.
- **Sıradaki sıra:** 1) M2 yenilendi akışını tamamla, kanal kararını bekle. 2) Seçilen bildirim kanalına göre dış gönderimi tamamla. 3) M3 checklist şablonlarına geç.
- **Kullanıcıdan beklenen:** Bildirim kanalı seçimi (SMTP/e-posta, Teams veya Telegram).

## 2026-10-09 16:27 — Copilot — Sağlayıcı düzenleme/silme commit/push

- **Git durumu:** `ai/codex/m0-complete`; sağlayıcı düzenleme/silme ve ayar hizası `8718975` commit'iyle `origin/ai/codex/m0-complete` dalına push edildi. Bu durum/günlük güncellemesi docs commit'i olarak push edilecek.
- **Yapılanlar:** Sağlayıcı düzenleme API'si ve ayarlar formu eklendi; yinelenen ad kontrollü 409 döndürüyor. Sağlayıcı adı değişince bağlı varlıkların görünen adı güncelleniyor; silerken ilişkiler kaldırılıyor ancak varlığın görünen eski sağlayıcı adı korunuyor. Sağlayıcı ve bağlantılı varlık değişiklikleri audit log'a yazılıyor. Ayarlar ekranına silme onayı, düzenleme iptali ve Türkçe sağlayıcı audit etiketleri eklendi. Kişi formundaki beşinci elemanın (buton) yeni satıra düşerek hizayı bozması düzeltildi; masaüstü/tablet ve mobil grid kuralları eklendi.
- **Doğrulama:** Backend pytest 17/17; Ruff check/format, mypy, Pylance diagnostics, `node --check` ve `git diff --check` geçti. Compose rebuild sonrası `/health` `ok`, migration head `0010_notification_snooze`. Tarayıcı mock'u ile sağlayıcı düzenle/sil akışları kontrol edildi; kalıcı sağlayıcı verisine dokunulmadı. Form alanlarının hizası aynı satır/tablet grid düzeninde kontrol edildi.
- **Bilinenler:** Python 3.14 üzerinde FastAPI/Starlette kaynaklı deprecation uyarıları devam ediyor. Bildirim kanalı seçilmediği için e-posta gönderimi kapalı.
- **Sıradaki sıra:** 1) M2 "Yenilendi" akışını tamamla ve kanal kararını bekle. 2) Seçilen kanala göre e-posta/digest'i uygula. 3) Sonrasında M3 checklist şablonlarına geç.
- **Kullanıcıdan beklenen:** E-posta/Teams/Telegram bildirim kanalı kararı daha sonra.

## 2026-10-09 16:12 — Copilot — M2 erteleme commit/push

- **Git durumu:** `ai/codex/m0-complete`; M2 erteleme özelliği `bdffece` commit'iyle `origin/ai/codex/m0-complete` dalına push edildi. Bu teslim kaydı düzeltmesi ayrı docs commit'i olarak push ediliyor. `.env` commit dışında.
- **Kullanıcı kararı:** Bekleyen yenileme uyarıları 1, 3 veya 7 gün ertelenebilir.
- **Yapılanlar:** Bildirim modeline `snoozed_until` eklendi; `0010_notification_snooze` ileri/geri alınabilir migration'ı oluşturuldu. `POST /api/notifications/{id}/snooze` yalnızca 1/3/7 gün değerlerini kabul ediyor, yalnızca bekleyen uyarıları erteliyor ve değişikliği audit log'a yazıyor. Ayarlar ekranındaki kuyrukta her uyarı için üç erteleme seçeneği ve erteleme bitişi gösteriliyor. E-posta gönderimi yapılmıyor.
- **Mevcut konum:** M0/M1 tamamlandı. M2 eşik değerlendirme, kuyruk, scheduler ve snooze hazır; e-posta/digest için kanal kararı ve "Yenilendi" akışı bekliyor. M3+ başlamadı.
- **Çalışma ortamı:** Compose PostgreSQL migration head `0010_notification_snooze`; `/health` `ok`; servisler çalışıyor. Veritabanına test uyarısı eklenmedi.
- **Doğrulama:** Backend pytest 17/17; Ruff check/format, mypy, Pylance diagnostics, `node --check` ve `git diff --check` başarılı. UI tarayıcıda API mock'u ile 1/3/7 seçenekleri, `days:3` isteği ve ertelendi görünümü doğrulandı; kalıcı veri yazılmadı. Python 3.14'te FastAPI/Starlette kaynaklı deprecation uyarıları sürüyor.
- **Sıradaki sıra:** 1) Kullanıcıdan SMTP/Teams/Telegram kanal kararını al; dış gönderim şimdilik kapalı. 2) "Yenilendi" akışını tamamla ve seçilen kanala göre e-posta/digest ekle. 3) M2 kapanınca M3 checklist şablonlarına geç.
- **Kullanıcıdan beklenen:** Bildirim kanalı seçimi; e-posta gönderimi kanal kararı olmadan kapalı kalacak.

## 2026-10-09 14:57 — Copilot — M1 commit ve push

- **Git durumu:** `ai/codex/m0-complete`; M1 contacts/liste çalışmaları ve birikmiş maliyet/audit/M2 değişiklikleri `c33466a` commit'iyle `origin/ai/codex/m0-complete` dalına push edildi. Bu durum/log güncellemesi takip eden dokümantasyon commit'ine dahil ediliyor. `.env` ignore kapsamında ve commit dışında.
- **Yapılanlar:** Asset list API'sine DB seviyesinde sayfalama, kayıt toplamı, `name/type/expires_at/status` sıralama ve name/vendor/owner araması eklendi. UI'da 25/50/100 sayfa boyutu, önceki/sonraki, toplam arama sonucu ve artan/azalan sıralama eklendi. Pano verisi liste filtresi/sayfalamasından bağımsız tam varlık listesi isteğiyle hesaplanıyor. Contacts yönetimi aşaması da tamamlandı.
- **Mevcut konum:** M0 tamamlandı. M1'de contacts, asset CRUD, dashboard, maliyet, CSV export, audit ve liste arama/filtre/sıralama/sayfalama hazır; tür bazlı form alanları eksik. CSV içe aktarım opsiyonel. M2 kuyruk/eşik/scheduler hazır; bildirim kanalı, yenilendi ve snooze eksik. M3+ başlamadı.
- **Çalışma ortamı:** Compose PostgreSQL `0008_contacts (head)`; backend/frontend yeniden build edilip başlatıldı. `/health` `ok`; mevcut demo varlık sayısı 4, veritabanına test kaydı yazılmadı.
- **Doğrulama:** Backend pytest 15/15; Ruff check/format, mypy, `node --check`, Pylance API diagnostics ve `git diff --check` başarılı. Testler API paging offsets, out-of-range offset clamp, ascending/descending sort, case-insensitive search ve hatalı sort inputlarını kapsıyor. Canlı API `total=4`, `limit=2` ile iki sıralı kayıt döndürdü; tarayıcıda 4 kayıt, sıralama ve sayfa özeti doğrulandı. Python 3.14 üzerinde bağımlılıklardan deprecation uyarıları görüldü.
- **Sıradaki sıra:** 1) Tür bazlı alan gereksinimlerini mevcut varlık alanları/API şemalarıyla eşle. 2) Formda tür seçimine göre alanları göster/gizle ve uygun doğrulamaları ekle. 3) CRUD ve UI testleriyle doğrula; M1'i kapat.
- **Kullanıcıdan beklenen:** CSV içe aktarım opsiyonel kapsamda; kullanıcı talebi olmadan eklenmeyecek. Bildirim kanalı ve lisans vault-ref kararı açık.

## 2026-10-09 14:49 — Copilot — M1 contacts yönetimi

- **Git durumu:** `ai/codex/m0-complete`, HEAD `5cfa11b`; birikmiş maliyet/audit/M2 ve bu contacts değişiklikleri yerel, commit/push edilmedi. `.env` ignore kapsamında.
- **Yapılanlar:** Contacts modeli ve asset-contact many-to-many ilişkisi, geri alınabilir `0008_contacts` migration'ı, contacts listele/oluştur/sil API'ları eklendi. Asset create/update/read kişi atamalarını destekliyor; audit diff kişi ilişki kimliklerini izliyor; CSV ilgili kişi adlarını içeriyor. Ayarlar ekranında kişi yönetimi ve varlık formunda çoklu kişi seçimi var.
- **Mevcut konum:** M0 tamamlandı. M1 contacts dahil model/API kapsamını, pano/maliyet, CSV export ve temel audit'i içeriyor; UI sayfalama/kullanıcı kontrollü sıralama ve tür bazlı alanlar eksik. M2 eşik değerlendirmesi, günlük scheduler, tekrar önleme ve gönderimsiz kuyruk hazır; SMTP/digest kanal kararı bekliyor; yenilendi/snooze eksik. M3+ başlamadı.
- **Migration / çalışma ortamı:** Compose PostgreSQL Alembic `0008_contacts (head)`; volume korunuyor. Uygulama `http://127.0.0.1:8080/`, `/health` `ok`.
- **Doğrulama:** Backend pytest 14/14; Ruff lint/format, mypy, frontend `node --check`, Pylance diagnostics ve `git diff --check` başarılı. Contacts CRUD/asset assign/clear/delete, hatalı ID/boş ad ve CSV export test edildi. Tarayıcıda kişi yönetimi ve asset edit formundaki contact multi-select doğrulandı; DB'ye test kişisi veya varlığı eklenmedi.
- **Sıradaki sıra:** 1) M1 liste arayüzü sayfalama ve kullanıcı kontrollü sıralama. 2) Domain/hosting/VDS/lisans alanlarını forma göre koşullu göster ve API şemalarıyla tutarlı yap. 3) M1 test/CI ile kapanış; sonra M2 yenilendi/snooze. SMTP/digest yalnızca kullanıcı kanal kararı sonrası.
- **Kullanıcıdan beklenen:** Bildirim kanalı şimdilik ertelendi. Lisans anahtarı saklama kararı açık; vault-ref yaklaşımı korunmalı.

## 2026-10-09 14:31 — Copilot — Yol haritası durumunu eşitleme

- **Git durumu:** `ai/codex/m0-complete`, HEAD `5cfa11b`; önceki maliyet/audit/M2 değişiklikleri bu dalda yerel ve commit/push edilmedi. `.env` ignore kapsamında.
- **Yapılanlar:** `AGENTS.md` ve bu belgede milestone işaretleri ayrıntılı plandaki gerçek ilerlemeyle eşleştirildi. M0 tamamlandı; M1 ve M2 kısmi olarak tanımlandı. Eski Docker/CI notları güncel doğrulamayla değiştirildi.
- **Mevcut konum:** M0 tamamlandı. M1'in asset/vendor/tag CRUD, maliyet özeti/pano, CSV export ve temel audit kapsamı var; contacts modeli, arayüzde gerçek sayfalama ve kullanıcı kontrollü sıralama, varlık türüne özel form alanları eksik. M2'nin eşik değerlendirmesi, günlük scheduler, tekrar önleme ve gönderimsiz kuyruğu hazır; kullanıcı kanal kararını ertelediği için gönderim yok; yenilendi/snooze eksik. M3+ başlamadı.
- **Önceki doğrulamalar:** 13/13 backend testi, Ruff, mypy, `node --check` ve `git diff --check` geçti. Compose PostgreSQL Alembic `0007_renewal_notifications (head)`, `/health` `ok`; tarayıcıda Ayarlar kuyruğu kontrol edildi. Tam migration zincirinin SQLite doğrulaması eski `0004_vendors` revision'ının SQLite uyumsuz constraint alter'ı nedeniyle bloklandı.
- **Sıradaki sıra:** 1) M1 contacts modeli/API/migration/UI. 2) Liste UI sayfalaması ve kullanıcı kontrollü sıralama ile tür bazlı form alanları. 3) M1 test/CI ile kapatıldıktan sonra M2 yenilendi/snooze. SMTP/digest yalnızca kullanıcı kanal tercihi sonrası.
- **Kullanıcıdan beklenen:** Bildirim kanalı şimdilik ertelendi. Lisans anahtarı saklama yaklaşımı kararı açık; M3'e geçmeden önce kalan M1 işlerini tamamlamak hedefleniyor.

## 2026-10-09 11:23 — Copilot — Oturum kapatışı

- **Git durumu:** `ai/codex/m0-complete`; oturum başında `git pull --ff-only` çalıştırıldı. `origin/ai/codex/m0-complete` ile eşit ve çalışma ağacı başlangıçta temizdi.
- **Yapılanlar:** Uygulama kodunda değişiklik yapılmadı. Oturum kapatış notu [docs/AI_SESSION_LOG.md](./AI_SESSION_LOG.md) dosyasının en üstüne eklendi.
- **Doğrulama:** `git diff --check` başarılı; kod/test çalıştırılmadı (uygulama kodu değişmedi).
- **Yarım kalanlar:** Maliyet özetinin aylık/yıllık ayrıştırılması, audit log temeli, M2 yenileme eşikleri ve bildirim motoru.
- **Sıradaki adım:** Önce dashboard maliyetini aylık/yıllık özetle; ardından temel audit log'u ekle ve M2'ye geç.
- **Kullanıcıdan beklenen:** Bildirim kanalı ve lisans anahtarı saklama yaklaşımı için [Açık Kararlar](#açık-kararlar-kullanıcıdan-bekleniyor) bölümündeki kararlar.

## 2026-10-09 11:13 — Codex — Git senkronizasyonu

- **Git durumu:** `git pull --ff-only origin ai/codex/m0-complete` çalıştırıldı; yerel dal ve uzak dal eşit, çalışma ağacı temizdi.
- **Yapılanlar:** Uygulama kodunda değişiklik yapılmadı. Senkronizasyon oturumu [docs/AI_SESSION_LOG.md](./AI_SESSION_LOG.md) içine kaydedildi.
- **Sıradaki adım:** Maliyet özetini aylık/yıllık ayrıştırmak.

## 2026-10-09 — Codex — Devir hazırlığı

- **Git durumu:** `ai/codex/m0-complete` dalı GitHub'daki `origin/ai/codex/m0-complete` ile eşit ve çalışma ağacı temizdir. Son commit: `cd3264e feat: add vendor management Agent: other`.
- **Tamamlanan kapsam:** M0 iskeleti ve Docker Compose; PostgreSQL/Alembic; FastAPI asset CRUD; dashboard; etiketler; CSV dışa aktarım; sol menü panelleri; demo veriler; sağlayıcı modeli, ilişkisi, API'ları ve arayüz yönetimi.
- **Çalışan ortam:** Compose tanımı [deploy/docker-compose.yml](../deploy/docker-compose.yml) içindedir. Servisler PostgreSQL, backend, frontend ve Caddy proxy'dir. Uygulama proxy üzerinden `http://127.0.0.1:8080/` adresinde çalışır; API belgeleri `/api/docs` yolundadır. Docker yolu yeni PowerShell oturumlarında gerekirse `C:\Program Files\Docker\Docker\resources\bin` olarak PATH'e eklenmelidir.
- **Demo durumu:** PostgreSQL'de 4 demo varlık, 2 demo etiket ve 4 demo sağlayıcı bulunmaktadır. Demo kayıtları gerçek sistem verisi değildir.
- **Doğrulananlar:** Backend `pytest` 9/9, Ruff, frontend `node --check`, `git diff --check`; Chrome'da dashboard, varlıklar ve ayarlar ekranları doğrulandı. Python testleri `backend` klasöründen çalıştırılmalıdır: `..\.venv\Scripts\python.exe -m pytest tests -q`.
- **Yarım kalanlar:** Eski serbest metin sağlayıcıların otomatik normalize edilmesi, aylık/yıllık maliyet ayrıştırması, audit log, gerçek otomatik kontroller ve kimlik doğrulama.
- **Sıradaki somut adımlar:** 1) dashboard maliyetini aylık/yıllık özetle, 2) değişiklikleri audit log'a yaz, 3) M2 yenileme eşikleri ve SMTP bildirim motoruna geç.
- **Devir notu:** Yeni ajan önce [AGENTS.md](../AGENTS.md) ve bu dosyayı okumalı, `git pull` yapmalı, mevcut dalı ezmemeli ve devam etmeden önce çalışma ağacını kontrol etmelidir.

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
- [ ] Bildirim kanalı (SMTP / Teams / Telegram) — kullanıcı şimdilik erteledi; gönderim kapalı
- [ ] Lisans anahtarları platformda saklanacak mı, yoksa sadece parola yöneticisi referansı mı?

## Karar Kayıtları
| Tarih | Karar | Gerekçe | Karar veren |
|---|---|---|---|
| 2026-10-08 | Sıfırdan kurulum; mevcut envanter/sistem yok, import gerekmiyor (M1'de CSV import opsiyonel) | Kullanıcı beyanı | Kullanıcı |
| 2026-10-08 | M0 ve ilk sürüm için FastAPI + PostgreSQL + HTMX yığını seçildi | İç araçta sunucu tarafı HTML akışı, Next.js'e göre daha az frontend bakım yükü sunuyor | Codex (kullanıcının karar verme yetkisi vermesiyle) |
| 2026-10-09 | Maliyet periyodu aylık/yıllık/tek seferlik/belirtilmemiş olarak tutulacak; eski kayıtlar belirtilmemiş kalacak ve farklı para birimleri ayrı gösterilecek | Kur dönüşümü veya eski kayıtların periyodu tahmin edilmeyecek | Kullanıcı |
| 2026-10-09 | Bildirim kanalı seçimi ve dışa gönderim şimdilik ertelendi; uyarılar yalnızca veritabanı kuyruğunda birikir | SMTP/Teams/Telegram kararı verilene kadar dış sistemlere mesaj gitmemesi | Kullanıcı |
| 2026-10-09 | Bekleyen yenileme uyarıları 1, 3 veya 7 gün ertelenebilir | Kullanıcı kuyruk satırından hızlı erteleme seçeneği istedi | Kullanıcı |

## Bağımlılık Gerekçeleri
- `fastapi`, `sqlalchemy`, `alembic`, `psycopg`, `pydantic-settings`: API, ORM/migration, PostgreSQL bağlantısı ve ortam yapılandırması için.
- `apscheduler`: M2 yenileme uyarıları ve M4 otomatik kontrollerin zamanlanması için; sürüm `3.11.0` sabitlendi.
- `ruff`, `mypy`, `pytest`: CI lint, tür denetimi ve test altyapısı için sabit geliştirme bağımlılıkları.

## Bilinen Sorunlar
- Mevcut çalışma ortamında Docker Compose çalışıyor; servisler Up, PostgreSQL healthy ve `/health` `ok`.
- CI yapılandırması (`.github/workflows/ci.yml`) backend Ruff lint/format, mypy, pytest; Compose config ve frontend image build adımlarını içeriyor. Bu yerel, henüz commit edilmemiş değişikliklerin GitHub Actions sonucu yok.
- Yerel testler Python 3.14 ile çalıştırıldı; proje paketi Python `>=3.12,<3.13` hedefliyor ve Compose backend imajı Python 3.12 kullanıyor. Yerel deprecation uyarıları Python sürüm farkıyla ilişkili.
- Migration zincirinin baştan SQLite üzerinde yürütülmesi mevcut `0004_vendors` migration'ının SQLite'ta desteklenmeyen foreign-key constraint ALTER işlemi nedeniyle mümkün değil; PostgreSQL Compose zinciri `0007_renewal_notifications` seviyesine başarıyla yükseldi.
- M1/M2 açık maddeler yukarıda listelenmiştir; gerçek SMTP/webhook gönderimi kullanıcı kanal kararı olmadan devreye alınmamalı.

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
