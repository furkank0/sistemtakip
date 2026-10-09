# sistemtakip

Kurum içi varlık/lisans envanteri, yenileme takibi, rutin kontrol listeleri ve sistem kontrolleri için web platformu.

## Geliştirme ortamı

Docker kurulu değilse backend yerel geliştirme için varsayılan olarak `backend/sistemtakip.db` SQLite veritabanını kullanır. Bu profil CRUD geliştirmesi ve arayüz doğrulaması içindir; Compose çalışırken `DATABASE_URL` PostgreSQL'e yönlendirilir.

Yerel backend kurulumu:

```powershell
cd backend
..\.venv\Scripts\python.exe -m alembic upgrade head
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

Frontend'i ayrı terminalde çalıştırmak için:

```powershell
cd frontend
..\.venv\Scripts\python.exe -m http.server 5173
```

1. Docker Engine ve Docker Compose eklentisini kurun.
2. `.env.example` dosyasını `.env` olarak kopyalayın ve yerel geliştirme parolalarını değiştirin.
3. Servisleri başlatın:

   ```sh
   docker compose -f deploy/docker-compose.yml --env-file .env up --build
   ```

4. Uygulamayı `http://localhost:8080` adresinde, API belgelerini `http://localhost:8080/api/docs` adresinde açın.

Yerel geliştirme yapılandırmasındaki varsayılan kimlik bilgilerini üretim ortamında kullanmayın. Üretim sırları repoya eklenmez.

## Servisler

- `db`: PostgreSQL 16
- `backend`: FastAPI API ve HTMX sayfalarını sunan Python uygulaması
- `frontend`: statik HTMX giriş ekranı
- `proxy`: Caddy reverse proxy

## Proje belgeleri

- [Geliştirme planı](docs/PLAN.md)
- [Canlı durum ve kararlar](docs/STATE.md)
- [Ajan çalışma kuralları](AGENTS.md)
