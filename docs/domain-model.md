# MediaAtlas — Domain Model (v1)

## 1. Domain ve amaç

MediaAtlas; oyun, film, dizi, anime ve kitapların keşfedildiği ve kullanıcının bu içerikleri kişisel kütüphanesine ekleyerek durum, not ve puan bilgilerini yönettiği bir masaüstü uygulamasıdır.

Uygulamanın **domain'i**, medya içeriğinin kendisi ile kullanıcının o içerikle olan kişisel ilişkisini modellemektir. İlk sürüm tek kullanıcılı, yerel çalışan bir uygulamadır.

### Kapsam

- Beş medya türü: `GAME`, `MOVIE`, `TV_SERIES`, `ANIME`, `BOOK`.
- Dış API'lerden içerik arama ve içerik detaylarını görüntüleme.
- Kütüphaneye ekleme/çıkarma, durum değiştirme, kişisel not ve 1–10 arası puan verme.
- **My Library** ekranında `All` ve her medya türü için ayrı sekmeler. `All` görünümünde türlere göre gruplama.
- İleride dizi/anime için API'den çekilmiş bölüm listesinde isteğe bağlı, tek tıkla **izlendi** işaretleme.

### Kapsam dışı (ilk sürüm)

- Oyun görev/quest takibi.
- Manuel sayfa sayısı, oynama saati veya izlenen dakika girme.
- Medya oynatma, çevrimiçi hesaplar, bulut senkronizasyonu ve sosyal özellikler.

## 2. Temel domain kavramları

### `MediaItem` — içeriğin kendisi

Bir medya öğesinin dış kaynaktan elde edilen, kişisel olmayan bilgilerini temsil eder.

| Field | Python type | Zorunlu | Açıklama |
|---|---|---|---|
| `source` | `str` | Evet | Veri sağlayıcısı: `rawg`, `tmdb`, `jikan`, `openlibrary` gibi |
| `external_id` | `str` | Evet | Kaynağın içerik kimliği; boş olmamalı |
| `media_type` | `MediaType` (Enum) | Evet | `GAME`, `MOVIE`, `TV_SERIES`, `ANIME`, `BOOK` |
| `title` | `str` | Evet | Boş veya yalnızca boşluk karakterlerinden oluşamaz |
| `description` | `str | None` | Hayır | API'de açıklama yoksa `None` |
| `cover_url` | `str | None` | Hayır | Kapak/poster adresi; yoksa `None` |
| `release_date` | `date | None` | Hayır | Tam tarih biliniyorsa; değilse `None` |
| `genres` | `tuple[str, ...]` | Hayır | Tür etiketleri; başlangıç değeri boş tuple |

**Identity:** Aynı medya öğesini ayırt etmek için `(source, media_type, external_id)` üçlüsünü kullanırız. Yalnızca `external_id` yeterli değildir; farklı API'ler aynı ID'yi verebilir. Ayrıca tek API içerisinde farklı içerik tiplerinin ID alanları çakışabilir (ör. TMDB film ve dizi kimlikleri).

`MediaItem`, kişisel puan veya izlenme durumu taşımaz. O alanlar `LibraryEntry`'ye aittir.

### `LibraryEntry` — kullanıcının içeriğe ilişkin kaydı

Kullanıcının belirli bir medya öğesini kişisel kütüphanesine eklemesiyle oluşur.

| Field | Python type | Zorunlu | Açıklama |
|---|---|---|---|
| `media_key` | `tuple[str, MediaType, str]` | Evet | İlgili `MediaItem`'ın kimliği (source, type, external_id) |
| `status` | `LibraryStatus` (Enum) | Evet | `PLANNED`, `IN_PROGRESS`, `COMPLETED`, `ON_HOLD`, `DROPPED` |
| `rating` | `int | None` | Hayır | Yalnızca `COMPLETED` durumunda 1–10 arası; aksi hâlde `None` |
| `notes` | `str` | Hayır | Kişisel not; varsayılan `""` |
| `added_at` | `datetime` | Evet | Kütüphaneye eklendiği zaman |
| `completed_at` | `datetime | None` | Hayır | Tamamlandıysa tarih; aksi hâlde `None` |

İlk sürüm tek kullanıcıya ait olduğu için ayrıca `user_id` gerekmiyor. İleride çok kullanıcılı yapıya geçilirse bu model genişletilebilir.

### Enum'lar

- `MediaType`: `GAME`, `MOVIE`, `TV_SERIES`, `ANIME`, `BOOK`.
- `LibraryStatus`: `PLANNED`, `IN_PROGRESS`, `COMPLETED`, `ON_HOLD`, `DROPPED`.

Domain'deki durumlar **ortak ve dil bağımsızdır**. Arayüz bunları medya türüne göre gösterebilir: Game → *Oynuyorum*, Book → *Okuyorum*, Movie/TV/Anime → *İzliyorum*. Böylece aynı iş kuralları yeniden kullanılabilir.

## 3. İlişkiler

```text
MediaItem (0 veya 1 LibraryEntry)
  source
  media_type
  external_id
  title
      |
      | Kullanıcı kütüphaneye ekler
      v
LibraryEntry
  media_key  ----> MediaItem kimliği
  status
  rating
  notes
  added_at
```

- Katalogda görünen her `MediaItem`, kütüphanede bulunmak zorunda değildir.
- Tek kullanıcılı ilk sürümde bir `MediaItem` için **en fazla bir** `LibraryEntry` bulunur.
- Kütüphaneden çıkarma, dış API'deki içeriği silmek anlamına gelmez.
- SQLite aşamasında yerel bir `media_items.id` anahtarı ve `library_entries.media_item_id` foreign key'i kullanabiliriz. Domain tasarımını bugünden veritabanı ID'sine bağımlı hâle getirmiyoruz.

## 4. Business rules / validation

1. **Geçerli kimlik:** `source` ve `external_id` boş olamaz; `media_type` tanımlı bir `MediaType` olmalı.
2. **Geçerli başlık:** `title.strip()` boş olamaz.
3. **Duplicate engelleme:** Bir medya anahtarı `(source, media_type, external_id)` kişisel kütüphanede en fazla bir kez bulunabilir. Tekrar ekleme ikinci kayıt oluşturmaz; mevcut kayıt gösterilir.
4. **Rating aralığı:** `rating` verildiyse `int` olmalı ve `1 <= rating <= 10` kuralına uymalı. `bool`, Python'da `int` alt sınıfı olsa da puan olarak kabul edilmez.
5. **Rating ve status ilişkisi:** `rating`, yalnızca `status == COMPLETED` iken verilebilir. `PLANNED`, `IN_PROGRESS`, `ON_HOLD` ve `DROPPED` durumlarında `rating is None` olmalıdır.
6. **Status değişikliği:** Kullanıcı tamamlanmış bir içeriği başka duruma alırsa, önceki puanın silinip silinmeyeceği açıkça sorulmalı; ilk sürümde onay sonrası `rating = None` yapılır. `completed_at` da `None` olur.
7. **Completed date:** `status == COMPLETED` durumunda `completed_at` atanabilir; diğer durumlarda `None` olmalıdır. Tamamlanma tarihi, eklenme tarihinden önce olamaz (uygulamanın kaydettiği işlemler için).
8. **API eksik verisi:** `description`, `cover_url`, `release_date` gibi opsiyonel alanlar eksikse `None` ile temsil edilir; sahte değer üretilmez.
9. **Offline erişim:** Kullanıcının kütüphanesi internete veya API yanıtlarına bağımlı olmadan açılabilmelidir; gerekli içerik bilgileri yerel olarak saklanacaktır.

Validation'ların bir kısmı domain modellerinde, kayıt tekilliği gibi kurallar ise ileride service/repository ve SQLite constraints seviyesinde uygulanacaktır.

## 5. Bölüm takibi (ileriki aşama)

TV Series ve Anime detay sayfalarında API mevcutsa sezon/bölüm listesi gösterilir. Kullanıcı yalnızca **izlendi / izlenmedi** olarak işaretler. Bölüm numarası veya ismi manuel girilmez. API'de bölüm listesi eksikse özellik devre dışı kalabilir.

Bu özelliği bugünkü iki modele eklemiyoruz; ileride ayrı `Episode` ve `WatchedEpisode` modelleriyle ele alacağız. Genel `ProgressService` oluşturmayacağız.

## 6. Sorumluluk sınırları

- **Domain (`mediaatlas/domain/`)**: Modeller, Enum'lar, kurallar. PySide6, HTTP ve SQLite import etmez.
- **GUI (`mediaatlas/gui/`)**: Kullanıcıya bilgi gösterir, işlemleri tetikler; domain kurallarının tek kaynağı olmaz.
- **Providers (ileride)**: RAWG/TMDB/Jikan/Open Library cevaplarını `MediaItem` formatına dönüştürür.
- **Services (ileride)**: Kütüphaneye ekleme/çıkarma, durum güncelleme gibi use-case'leri yönetir.
- **Repositories (ileride)**: SQLite üzerinden kalıcı verileri okur ve yazar.

## 7. Task 1 acceptance criteria

- [x] Domain ve uygulamanın amacı tanımlandı.
- [x] `MediaItem` alanları ve tipleri belirlendi.
- [x] `LibraryEntry` alanları ve tipleri belirlendi.
- [x] Dış API kimlikleri için çakışmaya dayanıklı bir strateji seçildi.
- [x] İki model arasındaki ilişki açıklandı.
- [x] En az üç validation/business rule yazıldı.
- [x] Bu belgede GUI, database veya API implementasyonu yapılmadı.

**Sonraki adım:** Day 2 Task 2'de `Enum` ve `dataclass` konularını öğrenip bu modeli saf Python koduna dönüştürmek.
