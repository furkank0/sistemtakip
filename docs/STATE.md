# docs/STATE.md — Canlı Proje Durumu

> Her ajan oturum sonunda (veya kesinti öncesi) bu dosyayı günceller. En yeni oturum **en üstte** olmalıdır.

- **Son güncelleyen:** Codex — M0 temel iskelet
- **Tarih:** 2026-10-08
- **Repo:** https://github.com/furkank0/sistemtakip
- **Aktif dal:** `ai/codex/m0-scaffold`
- **Son commit:** `8bac3f7` (`chore: add M0 project scaffold`)

## Özet
Proje başlangıç aşamasında. Teknoloji yığını kullanıcı adına değerlendirildi: Python 3.12, FastAPI, SQLAlchemy, Alembic, PostgreSQL 16, APScheduler ve HTMX. M0 temel iskeleti `ai/codex/m0-scaffold` dalında hazırlandı.

## Tamamlananlar
- [x] Proje kapsamı ve çok-AI çalışma protokolü yazıldı (`AGENTS.md`)
- [x] Canlı durum dosyası oluşturuldu (`docs/STATE.md`)
- [x] Detaylı geliştirme planı yazıldı (`docs/PLAN.md`)
- [x] ChatGPT devir promptu hazırlandı (`CHATGPT_HANDOFF_PROMPT.md`)
- [x] Dört proje belgesi çalışma alanındaki hedef yollarına yerleştirildi
- [x] M0 temel iskeleti eklendi: FastAPI health/version, boş Alembic revizyonu, HTMX için frontend servisi, Caddy proxy ve PostgreSQL Compose tanımı
- [x] `.env.example`, `.gitignore`, README, Ruff/mypy CI ve pre-commit yapılandırması eklendi

## Devam Edenler / Yarım Kalanlar
- M0 henüz tamamlanmadı: Docker servisleri başlatılmadı/doğrulanmadı, otomatik test yok, CI'da pytest adımı ve frontend lint/build adımları yok (frontend statik Nginx imajı olarak derleniyor).
- M0 değişiklikleri `ai/codex/m0-scaffold` dalında commit edildi; remote'a push bekliyor.

## Sıradaki Adımlar
1. Docker Compose kurulu ve erişilebilir olduğunda servisleri ayağa kaldırıp `/health`, `/version` ve `/api/docs` yollarını doğrula.
2. M0 CI kapsamını testler ve frontend kalite işleriyle tamamla; ardından M0 DoD'yi kapat.
3. GitHub kaynağını bu çalışma alanına bağla, ajan dalı oluştur ve değişiklikleri commit et.

## Açık Kararlar (Kullanıcıdan Bekleniyor)
- [x] Teknoloji yığını: Python 3.12 + FastAPI + SQLAlchemy/Alembic + PostgreSQL 16 + APScheduler + HTMX
- [ ] Bildirim kanalı (SMTP / Teams / Telegram)
- [ ] Lisans anahtarları platformda saklanacak mı, yoksa sadece parola yöneticisi referansı mı?

## Karar Kayıtları
| Tarih | Karar | Gerekçe | Karar veren |
|---|---|---|---|
| 2026-10-08 | Sıfırdan kurulum; mevcut envanter/sistem yok, import gerekmiyor (M1'de CSV import opsiyonel) | Kullanıcı beyanı | Kullanıcı |
| 2026-10-08 | M0 ve ilk sürüm için FastAPI + PostgreSQL + HTMX yığını seçildi | İç araçta sunucu tarafı HTML akışı, Next.js'e göre daha az frontend bakım yükü sunuyor | Codex (kullanıcının karar verme yetkisi vermesiyle) |

## Bilinen Sorunlar
- GitHub `origin/main` erişilebilir; değişiklikler ayrı ajan dalında tutuluyor.
- M0 Docker/HTTP doğrulaması henüz çalıştırılmadı.
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
- Yapılanlar: Arşiv belgeleri incelendi; kullanıcı adına HTMX yığını seçildi; temel M0 uygulama iskeleti eklendi; kaynak `origin/main` alındı ve ajan dalı oluşturuldu.
- Yarım kalanlar: Compose/HTTP doğrulaması, test ve frontend CI kapsamı; dalın remote'a gönderilmesi.
- Commit/dal: `8bac3f7` — `ai/codex/m0-scaffold` (`origin/main` tabanlı).
- Sonraki ajana not: Stack seçimi HTMX olarak kaydedildi. M0 henüz DoD'yi karşılamıyor.
