# Sistem Takip — AI Devir Notu

Bu belge, başka bir AI ajanın projeyi kaldığı yerden güvenli biçimde devralması içindir.

## Git durumu

- Repository: `https://github.com/furkank0/sistemtakip`
- Aktif dal: `ai/codex/m0-complete`
- Uzak dal: `origin/ai/codex/m0-complete`
- Son commit: `cd3264e feat: add vendor management Agent: other`
- Devir öncesi çalışma ağacı temizdir.
- `main` dalına doğrudan push yapılmamalıdır.

Başlangıçta çalıştır:

```powershell
git pull --ff-only origin ai/codex/m0-complete
Get-Content AGENTS.md
Get-Content docs/STATE.md
```

## Çalışan sistem

Compose dosyası [deploy/docker-compose.yml](../deploy/docker-compose.yml) içindedir. Stack PostgreSQL, FastAPI backend, statik frontend ve Caddy proxy servislerinden oluşur.

- Uygulama: `http://127.0.0.1:8080/`
- Swagger: `http://127.0.0.1:8080/api/docs`
- Sağlık: `http://127.0.0.1:8080/health`

Docker komutu yeni PowerShell oturumunda bulunamazsa Docker Desktop yolu PATH'e eklenebilir:

```powershell
$env:Path = 'C:\Program Files\Docker\Docker\resources\bin;' + $env:Path
docker compose -f deploy/docker-compose.yml ps
```

Backend container başlangıcında Alembic migration'larını uygular. Son migration `0004_vendors` sağlayıcı tablosunu ve `assets.vendor_id` ilişkisini ekler.

## Mevcut özellikler

- Asset CRUD: domain, hosting, VDS, lisans
- Asset tip/durum/etiket/sağlayıcı filtreleri
- Sağlayıcı CRUD ve varlık ilişkisi
- Etiket CRUD ve çoklu etiket ilişkisi
- CSV dışa aktarım
- Dashboard sayaçları, yaklaşan yenilemeler, tür dağılımı ve kayıtlı maliyet
- Kontroller paneli için RDAP/TLS/DNS-HTTP/TCP-ICMP hazırlık kartları
- Ayarlar panelinde API/Compose durumu ve sağlayıcı yönetimi
- PostgreSQL ve SQLite fallback desteği

Demo PostgreSQL verisi: 4 varlık, 2 etiket ve 4 sağlayıcı. Gerçek sistem verisi değildir.

## Test ve kalite

Python ortamı proje kökündeki `.venv` içindedir. Testleri `backend` klasöründen çalıştır:

```powershell
cd backend
..\.venv\Scripts\python.exe -m pytest tests -q
..\.venv\Scripts\python.exe -m ruff check app tests
cd ..
node --check frontend/app.js
git diff --check
```

## Sıradaki geliştirme sırası

1. Dashboard maliyetini aylık/yıllık özet ve sağlayıcı kırılımıyla genişlet.
2. Asset/sağlayıcı/etiket değişiklikleri için temel audit log yazımını ekle.
3. M2 yenileme eşiklerini ve SMTP bildirim motorunu geliştir.
4. Sonraki aşamalarda checklist, gerçek otomatik kontroller ve LDAP/AD kimlik doğrulamaya geç.

Değişiklik yaparken [AGENTS.md](../AGENTS.md) içindeki güvenlik, migration, test, branch ve devir kurallarına uy.

Oturumlar arası ortak kayıt için [AI_SESSION_LOG.md](./AI_SESSION_LOG.md) dosyasını kullan. Her oturum sonunda yeni kaydı dosyanın en üstüne ekle.
