# Simple Search Engine

Simple Search Engine adalah aplikasi web yang memungkinkan Anda untuk melakukan crawling dan indexing pada website tertentu, kemudian melakukan pencarian pada data yang telah diindeks. Aplikasi ini dibangun dengan Flask untuk backend dan HTML/CSS/JavaScript untuk frontend.

## Fitur Utama

- **Web Crawler**: Melakukan crawling pada website yang diizinkan
- **Indexing System**: Menyimpan dan mengindeks konten website ke database
- **Search Engine**: Mencari konten berdasarkan kata kunci
- **Admin Panel**: Mengelola domain yang diizinkan dan melakukan crawling
- **Responsive Design**: Antarmuka yang responsif untuk desktop dan mobile

## Teknologi yang Digunakan

### Backend
- **Flask**: Framework web Python
- **SQLAlchemy**: ORM untuk database
- **SQLite**: Database untuk menyimpan indeks
- **BeautifulSoup**: Parser HTML untuk ekstraksi konten
- **Requests**: HTTP client untuk crawling
- **Flask-CORS**: Untuk menangani CORS

### Frontend
- **HTML5**: Struktur halaman web
- **CSS3**: Styling dengan gradient dan animasi
- **JavaScript**: Interaksi dan komunikasi dengan API
- **Font Awesome**: Icon library

## Struktur Proyek

```
simple_search_engine/
├── backend/
│   └── search_engine_backend/
│       ├── src/
│       │   ├── models/
│       │   │   └── page.py          # Model database
│       │   ├── routes/
│       │   │   └── search.py        # API routes
│       │   ├── static/              # Frontend files
│       │   │   ├── index.html
│       │   │   ├── style.css
│       │   │   └── script.js
│       │   ├── database/
│       │   │   └── app.db           # SQLite database
│       │   ├── crawler.py           # Web crawler
│       │   ├── indexer.py           # Search indexer
│       │   └── main.py              # Entry point
│       ├── venv/                    # Virtual environment
│       └── requirements.txt
├── frontend/                        # Frontend source files
│   ├── index.html
│   ├── style.css
│   └── script.js
└── todo.md                          # Task tracking
```

## Instalasi dan Setup

### Prasyarat
- Python 3.11+
- pip (Python package manager)

### Langkah Instalasi

1. **Clone atau download repository**
   ```bash
   cd simple_search_engine/backend/search_engine_backend
   ```

2. **Aktifkan virtual environment**
   ```bash
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Jalankan aplikasi**
   ```bash
   python src/main.py
   ```

5. **Akses aplikasi**
   Buka browser dan kunjungi: `http://localhost:5000`

## Penggunaan

### 1. Menambahkan Domain yang Diizinkan

1. Klik tombol **Admin** di pojok kanan atas
2. Di section **Kelola Domain**, masukkan nama domain (contoh: `example.com`)
3. Klik **Tambah Domain**

### 2. Melakukan Crawling

1. Di panel admin, section **Crawl URLs**
2. Masukkan URL yang ingin di-crawl (satu per baris)
3. Klik **Mulai Crawling**
4. Sistem akan mengambil dan mengindeks konten dari URL tersebut

### 3. Melakukan Pencarian

1. Di halaman utama, masukkan kata kunci di kotak pencarian
2. Tekan Enter atau klik tombol search
3. Hasil pencarian akan ditampilkan dengan informasi:
   - Judul halaman
   - URL
   - Deskripsi/konten
   - Domain dan tanggal crawling

### 4. Melihat Statistik

Di panel admin, section **Statistik** menampilkan:
- Total halaman yang diindeks
- Total domain yang diizinkan

## API Endpoints

### Search API
- `GET /api/search?q={query}&limit={limit}` - Mencari halaman
- `GET /api/domains` - Mendapatkan daftar domain yang diizinkan
- `POST /api/domains` - Menambah domain baru
- `POST /api/crawl` - Melakukan crawling URL
- `GET /api/stats` - Mendapatkan statistik
- `GET /api/pages` - Mendapatkan daftar halaman yang diindeks

### Contoh Request

```bash
# Mencari dengan kata kunci "example"
curl "http://localhost:5000/api/search?q=example&limit=10"

# Menambah domain baru
curl -X POST http://localhost:5000/api/domains \
  -H "Content-Type: application/json" \
  -d '{"domain": "example.com"}'

# Crawling URLs
curl -X POST http://localhost:5000/api/crawl \
  -H "Content-Type: application/json" \
  -d '{"urls": ["https://example.com", "https://example.com/page1"]}'
```

## Konfigurasi

### Database
- Database SQLite disimpan di `src/database/app.db`
- Tabel utama: `pages` dan `allowed_domains`

### Crawler Settings
- Delay antar request: 1 detik (dapat diubah di `crawler.py`)
- User-Agent: `SimpleSearchEngine/1.0 (+http://localhost:5000)`
- Timeout: 10 detik per request

### Security
- CORS diaktifkan untuk semua origin
- Input validation pada semua endpoint
- SQL injection protection melalui SQLAlchemy ORM

## Pengembangan

### Menambah Fitur Baru

1. **Backend**: Tambahkan route baru di `src/routes/search.py`
2. **Frontend**: Update `script.js` untuk komunikasi API
3. **Database**: Modifikasi model di `src/models/page.py` jika perlu

### Testing

Aplikasi telah diuji dengan:
- Penambahan domain
- Crawling website example.com
- Pencarian konten
- Responsivitas UI
- Error handling

### Deployment

Untuk deployment production:
1. Gunakan server WSGI seperti Gunicorn
2. Setup reverse proxy dengan Nginx
3. Gunakan database PostgreSQL untuk performa lebih baik
4. Implementasi rate limiting
5. Setup monitoring dan logging

## Troubleshooting

### Error "Module not found"
```bash
# Pastikan virtual environment aktif
source venv/bin/activate
# Install ulang dependencies
pip install -r requirements.txt
```

### Database Error
```bash
# Hapus database dan buat ulang
rm src/database/app.db
python src/main.py
```

### CORS Error
- Pastikan Flask-CORS terinstall
- Check konfigurasi CORS di `main.py`

## Kontribusi

1. Fork repository
2. Buat branch fitur baru
3. Commit perubahan
4. Push ke branch
5. Buat Pull Request

## Lisensi

Proyek ini menggunakan lisensi MIT. Silakan gunakan dan modifikasi sesuai kebutuhan.

## Kontak

Untuk pertanyaan atau saran, silakan buat issue di repository ini.

