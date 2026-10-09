# AI Oturum Geliştirme Günlüğü

Bu dosya, projede çalışan tüm AI ajanları arasındaki ortak devir günlüğüdür. Her ajan, kendi geliştirme oturumunda yaptığı işleri ve sonraki planı oturum sonunda en üste yeni bir kayıt olarak ekler.

## Kayıt kuralları

- Yeni kayıt dosyanın en üstüne eklenir.
- Tarih ve saat Türkiye saatiyle (`Europe/Istanbul`) yazılır.
- Kod, migration, test, Docker, veri ve arayüz değişiklikleri somut dosya/commit bilgileriyle belirtilir.
- Yarım kalan işler, bilinen hatalar ve kullanıcıdan beklenen bilgi açıkça yazılır.
- Kayıt eklenmeden oturum tamamlanmış sayılmaz.
- Hassas bilgi, parola, token, gerçek müşteri verisi veya sır günlükte yer almaz.

## Kayıt şablonu

```markdown
## YYYY-MM-DD HH:mm Europe/Istanbul — <AI adı> — <konu>

- **Dal / commit:** `<branch>` / `<commit>`
- **Bu oturumda yapılanlar:**
  - ...
- **Değişen dosyalar:**
  - [dosya](../relative/path)
- **Doğrulama:**
  - ...
- **Yarım kalanlar / bilinen sorunlar:**
  - ...
- **Sonraki plan:**
  1. ...
  2. ...
- **Kullanıcıdan beklenen:**
  - ... veya `Yok`
```

## 2026-10-09 11:13 Europe/Istanbul — Codex — Ortak AI devir günlüğü oluşturuldu

- **Dal / commit:** `ai/codex/m0-complete` / `ad302a5`
- **Bu oturumda yapılanlar:** Tüm AI ajanlarının ortak kullanacağı bu günlük dosyası oluşturuldu. Oturum sonu kaydının zorunlu olması için [AGENTS.md](../AGENTS.md) güncellenecek.
- **Değişen dosyalar:** [AI_SESSION_LOG.md](./AI_SESSION_LOG.md), [AGENTS.md](../AGENTS.md)
- **Doğrulama:** Yerel dal ve `origin/ai/codex/m0-complete` aynı commit'te.
- **Yarım kalanlar / bilinen sorunlar:** Yok.
- **Sonraki plan:** Yeni ajan bu dosyanın en üstüne kendi tarih-saatli kaydını ekleyerek devam edecek.
- **Kullanıcıdan beklenen:** Yok.
