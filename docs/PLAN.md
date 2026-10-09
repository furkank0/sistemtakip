# docs/PLAN.md — Geliştirme Planı (v1)

> Bu plan, `AGENTS.md` (kurallar) ve `docs/STATE.md` (canlı durum) ile birlikte okunur.
> Plan değişirse önce bu dosya güncellenir, sonra `STATE.md`'ye karar kaydı eklenir.

## 1. Durum Özeti

| Alan | Durum |
|---|---|
| Proje kapsamı ve hedefler | Tamamlandı |
| Çok-AI çalışma protokolü (`AGENTS.md`) | Tamamlandı |
| Canlı durum dosyası (`docs/STATE.md`) | Tamamlandı |
| Geliştirme planı (bu dosya) | Tamamlandı |
| GitHub repo (`furkank0/sistemtakip`) | Oluşturuldu; `main` üzerinde yalnızca boş `README.md`. **Public → Private yapılacak** |
| Mevcut envanter / eski sistem | Yok; sıfırdan kurulum, zorunlu import yok |
| Teknoloji yığını | Varsayılan öneri hazır, **kullanıcı teyidi bekliyor** |
| Kod (M0–M6) | M0 tamamlandı; M1/M2 devam ediyor |

## 2. Kapsam

**Kapsam içi**
- Domain, hosting, VDS ve lisanslı ürünlerin merkezi envanteri ve yenileme takibi
- Bitiş tarihi eşiklerine göre bildirim
- Günlük/haftalık rutin kontrol checklist'leri (standart şablonlar, çalıştırma kaydı, geçmiş)
- Otomatik kontroller: domain expiry, TLS sertifika expiry, DNS, HTTP/TCP/ICMP erişilebilirlik
- Denetim kaydı (audit log), roller, LDAP/AD ile giriş (sonraki aşama)

**Kapsam dışı (v1)**
- Sunucu içi ajan kurulumu veya konfigürasyon yönetimi
- Ödeme/faturalama entegrasyonu
- Firewall/hypervisor üzerinde yazma yetkili otomasyon (v1'de her şey read-only)

## 3. Mimari (Varsayılan Öneri)

> Kullanıcı itiraz etmedikçe geçerlidir. Değişiklik ADR ile yapılır (`docs/adr/`). Kullanıcı karar yetkisini devredince HTMX seçildi ve `STATE.md`'ye kaydedildi.

```
[Browser] → [Reverse proxy (TLS)] → [Frontend (Next.js veya HTMX)]
                                  → [Backend API (FastAPI)] → [PostgreSQL]
                                           ↑
                                  [Scheduler/Worker (APScheduler)]
                                  → otomatik kontroller, bildirimler
```

- Backend: Python 3.12, FastAPI, SQLAlchemy 2.x, Alembic, Pydantic v2
- DB: PostgreSQL 16
- Worker: APScheduler (aynı konteyner veya ayrı `worker` servisi)
- Frontend: HTMX + Jinja2
- Dağıtım: Docker Compose, Ubuntu 24.04 LTS, reverse proxy (Caddy veya Nginx)
- Test/kalite: pytest, ruff, mypy, pre-commit; CI: GitHub Actions

## 4. Hedef Repo Yapısı

```
sistemtakip/
├─ AGENTS.md
├─ README.md
├─ .env.example
├─ .gitignore
├─ .github/workflows/ci.yml
├─ docs/
│  ├─ STATE.md
│  ├─ PLAN.md
│  └─ adr/                 # mimari karar kayıtları (0001-...)
├─ backend/
│  ├─ app/ (api/, core/, models/, schemas/, services/, jobs/)
│  ├─ alembic/
│  ├─ tests/
│  └─ pyproject.toml
├─ frontend/
└─ deploy/
   ├─ docker-compose.yml
   └─ proxy/
```

## 5. Veri Modeli

`AGENTS.md` Bölüm 4'teki tablolara ek olarak:

| Tablo | Amaç |
|---|---|
| `users`, `roles`, `user_roles` | Giriş ve yetkilendirme (M5) |
| `vendors` | Sağlayıcı/registrar/üretici kayıtları (ad, destek iletişimi, panel URL'i) |
| `tags`, `asset_tags` | Gruplama (site, departman, proje) |
| `contacts` | Varlık sorumluları ve bildirim alıcıları |

Uygulanan tür alanları: `domain` (registrar, nameserver'lar), `hosting` (paket, yönetim URL'si), `vds` (IP, işletim sistemi, vCPU/RAM/disk), `license` (ürün, koltuk sayısı). Tür alanları isteğe bağlıdır; tür değiştirilince eski türe ait alanlar temizlenir. Lisans anahtarı ve erişim bilgileri tutulmaz; yalnızca güvenli bir `vault_ref` yaklaşımı sonraki karar olarak kalır.

## 6. Yol Haritası

Her milestone için **Bitti Tanımı (DoD):** kod + test + migration + doküman güncel + `STATE.md` güncel + CI yeşil.

### M0 — Temel İskele
- [x] Repo klasör yapısı, `.gitignore`, `.env.example`, `README.md` (kurulum adımları)
- [x] `deploy/docker-compose.yml`: `db`, `backend`, `frontend`, `proxy`
- [x] Backend: FastAPI iskeleti, `/health` ve `/version` endpoint'leri, config yönetimi (env)
- [x] Alembic init + ilk boş migration
- [x] CI: Ruff + mypy + pytest + frontend imaj build
- [x] pre-commit hook'ları
- **DoD:** `docker compose up` ile tüm servisler ayağa kalkar, `/health` 200 döner, CI yeşil.

### M1 — Varlık Yönetimi ve Pano
- [x] `assets`, `vendors`, `tags`, `contacts` modelleri ve migration'ları
- [x] CRUD API + validasyon (tarih tutarlılığı, zorunlu alanlar)
- [x] Liste ekranı: arama, filtre (tür, sağlayıcı, etiket, durum), sıralama, sayfalama
- [x] Detay/düzenleme formu (türe göre dinamik alanlar)
- [x] Pano: 30/60/90 gün içinde bitenler, süresi dolanlar, türe göre sayılar, aylık/yıllık maliyet özeti
- [x] CSV dışa aktarım
- [ ] CSV içe aktarım (opsiyonel, şablonlu; yapılmadı)
- [x] Temel audit log (oluşturma/güncelleme/silme)
- **Durum:** Tamamlandı. CSV içe aktarma opsiyonel olup bu milestone kapsamına alınmadı.
- **DoD:** Kullanıcı dört varlık türünü ekleyip düzenleyebilir; pano doğru hesaplar; API testleri geçer.

### M2 — Yenileme Uyarı Motoru
- [x] Uyarı kuralları: varsayılan 60/30/14/7/1 gün ve süresi dolduğunda; varlık bazında geçersiz kılma
- [x] Scheduler job'u: günlük çalışır, kuralları değerlendirir
- [x] Tekilleştirme: aynı varlık+eşik için tekrar gönderim yok (`notifications` tablosu)
- [x] Kuyruktaki bekleyen uyarıyı 1, 3 veya 7 gün ertele; bitiş zamanını kaydet ve audit'e yaz
- [ ] SMTP e-posta gönderimi + günlük özet (digest) e-postası
- [x] "Yenilendi" aksiyonu: yeni bitiş tarihini girer, bekleyen eski dönem uyarılarını kapatır ve yeni uyarı döngüsü başlatır
- [x] Test modu (gerçek e-posta göndermeden önizleme)
- **Durum:** Değerlendirme, kuyruk, 1/3/7 günlük erteleme ve "Yenilendi" akışı hazır. Kullanıcı kanal kararını ertelediği için SMTP e-posta/digest gönderimi kapalı.
- **DoD:** Zaman mock'lanarak yazılmış testlerle eşikler doğru tetiklenir ve tekrarlanmaz.

### M3 — Günlük Rutin Kontrol Checklist'leri
- [ ] `check_templates` CRUD (madde sırası, zorunlu/opsiyonel, açıklama/talimat metni)
- [ ] Sıklık: günlük, haftalık, aylık; belirlenen günde otomatik `check_run` oluşturma
- [ ] Çalıştırma ekranı: madde bazında `ok / warn / fail / na` + not; tamamlayan kişi ve zaman damgası
- [ ] Geçmiş, tamamlanma oranı, geciken kontroller görünümü
- [ ] Başlangıç şablonları (örnek, kullanıcı düzenler): yedek işleri sonucu, disk/kapasite, VPN tünelleri, güvenlik/SIEM uyarıları, AV/EDR konsolu, yaklaşan yenilemeler
- **DoD:** Şablondan günlük çalıştırma üretilir, tamamlanır ve geçmişte raporlanır.

### M4 — Otomatik Kontroller
- [ ] Kontrol türleri: `rdap` (domain expiry), `tls` (sertifika bitişi), `dns`, `http`, `tcp`, `icmp`
- [ ] Worker: zamanlama, timeout, eşzamanlılık sınırı, sonuç geçmişi (`auto_checks` sonuçları)
- [ ] Durum modeli: `ok / warn / fail`; durum **değişince** uyarı, flap koruması (ardışık N hata)
- [ ] Domain `expires_at` değerini RDAP sonucuyla karşılaştırma ve uyuşmazlık uyarısı
- [ ] DNS değişiklik tespiti (NS/MX/A/TXT için önceki sonuçla fark)
- [ ] SSRF koruması: hedefler için izin listesi/engel listesi; iç ağ hedefleri yalnızca açıkça izin verilirse
- **DoD:** Her kontrol türü için birim testi; hatalı/yanıtsız hedef worker'ı kilitlemez.
- **Doğrulanacak:** `.tr` gibi bazı uzantılarda RDAP desteği olmayabilir; bu durumda bitiş tarihi manuel girilir ve otomatik kontrol opsiyonel kalır.

### M5 — Kimlik Doğrulama, Roller, Audit
- [ ] Yerel kullanıcılar (argon2 parola hash), oturum yönetimi, oturum zaman aşımı
- [ ] Roller: `admin`, `operator`, `viewer`; endpoint bazlı yetki kontrolü
- [ ] LDAP/AD girişi (bind + grup→rol eşleme), TLS zorunlu (LDAPS/StartTLS)
- [ ] Audit log tamamlanması: kim, ne zaman, neyi, önceki/sonraki değer; görüntüleme ekranı
- [ ] Opsiyonel: TOTP 2FA
- **DoD:** Yetkisiz erişim testleri geçer; LDAP ayarları ortam değişkeniyle yönetilir.

### M6 — Raporlama ve Sertleştirme
- [ ] Aylık yenileme ve maliyet raporu (CSV/PDF)
- [ ] Veritabanı yedekleme/geri yükleme betiği ve dokümanı
- [ ] `/metrics` (Prometheus uyumlu) ve yapılandırılmış loglama
- [ ] Güvenlik gözden geçirmesi: bağımlılık taraması, başlık/CSP, rate limit, secret taraması (CI)
- [ ] Ubuntu üzerinde kurulum ve işletim kılavuzu (runbook)
- [ ] Opsiyonel: sağlayıcı/registrar API entegrasyonları
- **DoD:** Sıfır Ubuntu sunucuda dokümana bakarak kurulum yapılabilir; yedekten geri dönüş denenmiştir.

## 7. Güvenlik Gereksinimleri (Tüm Milestone'lar)

- Repoda sır yok; yalnızca `.env.example`. CI'da secret taraması.
- Kimlik bilgisi/lisans anahtarı saklanacaksa alan düzeyinde şifreleme; v1'de yalnızca `vault_ref`.
- Üretim sistemlerine dokunan kod varsayılan read-only; yazma işlemleri ayrı onay gerektirir.
- Girdi doğrulama, parametrik sorgular, rate limit, güvenli HTTP başlıkları.
- Bağımlılık sürümleri sabit; eklenen her paketin gerekçesi `STATE.md`'ye yazılır.
- Loglarda parola, token, lisans anahtarı bulunmaz.

## 8. Açık Kararlar

1. Teknoloji yığını teyidi (özellikle frontend: Next.js mi, HTMX mi?)
2. Repo görünürlüğü: Public → **Private**
3. Bildirim kanalı: SMTP (v1) dışında Teams/Telegram gerekli mi?
4. LDAP/AD ortamı bilgileri (M5 öncesi): sunucu, base DN, grup yapısı
5. Hedef sunucu: Ubuntu sürümü, Docker izni, alan adı ve TLS sertifika yöntemi (iç CA / Let's Encrypt)

## 9. Riskler

| Risk | Önlem |
|---|---|
| Ajanlar arası çakışan değişiklikler | Dal-başına-ajan, küçük commit, `STATE.md` disiplini |
| Bağlam kaybı (kredi/limit) | Her adımdan sonra `STATE.md` + WIP commit |
| Hassas veri sızıntısı | Private repo, secret taraması, `vault_ref` yaklaşımı |
| RDAP kapsamı (.tr vb.) | Manuel tarih + opsiyonel otomatik kontrol |
| Kapsam kayması | M0–M2 çıkana kadar yeni özellik eklenmez |
