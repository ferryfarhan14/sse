# API Documentation - Simple Search Engine

## Base URL
```
http://localhost:5000/api
```

## Authentication
Tidak ada authentication yang diperlukan untuk API ini.

## Endpoints

### 1. Search Pages

**Endpoint:** `GET /search`

**Description:** Mencari halaman berdasarkan kata kunci

**Parameters:**
- `q` (required): Query string untuk pencarian
- `limit` (optional): Maksimal jumlah hasil (default: 10, max: 50)

**Example Request:**
```bash
curl "http://localhost:5000/api/search?q=example&limit=5"
```

**Example Response:**
```json
{
  "query": "example",
  "results": [
    {
      "id": 1,
      "url": "https://example.com",
      "title": "Example Domain",
      "content": "Example Domain Example Domain This domain is for use in illustrative examples...",
      "description": "Example domain for documentation",
      "keywords": "example, domain, test",
      "domain": "example.com",
      "crawled_at": "2025-06-30T03:56:45.123456",
      "last_updated": "2025-06-30T03:56:45.123456",
      "is_active": true
    }
  ],
  "total": 1
}
```

### 2. Get Allowed Domains

**Endpoint:** `GET /domains`

**Description:** Mendapatkan daftar domain yang diizinkan untuk di-crawl

**Example Request:**
```bash
curl "http://localhost:5000/api/domains"
```

**Example Response:**
```json
{
  "domains": ["example.com", "test.com"],
  "total": 2
}
```

### 3. Add Allowed Domain

**Endpoint:** `POST /domains`

**Description:** Menambahkan domain baru ke daftar yang diizinkan

**Request Body:**
```json
{
  "domain": "newdomain.com"
}
```

**Example Request:**
```bash
curl -X POST http://localhost:5000/api/domains \
  -H "Content-Type: application/json" \
  -d '{"domain": "newdomain.com"}'
```

**Example Response:**
```json
{
  "message": "Domain newdomain.com added successfully",
  "domain": "newdomain.com"
}
```

### 4. Crawl URLs

**Endpoint:** `POST /crawl`

**Description:** Melakukan crawling pada daftar URL yang diberikan

**Request Body:**
```json
{
  "urls": [
    "https://example.com",
    "https://example.com/page1",
    "https://example.com/page2"
  ]
}
```

**Example Request:**
```bash
curl -X POST http://localhost:5000/api/crawl \
  -H "Content-Type: application/json" \
  -d '{
    "urls": [
      "https://example.com",
      "https://example.com/page1"
    ]
  }'
```

**Example Response:**
```json
{
  "message": "Successfully indexed 2/2 pages",
  "indexed_count": 2,
  "total_urls": 2
}
```

### 5. Get Statistics

**Endpoint:** `GET /stats`

**Description:** Mendapatkan statistik sistem indexing

**Example Request:**
```bash
curl "http://localhost:5000/api/stats"
```

**Example Response:**
```json
{
  "total_pages": 15,
  "total_domains": 3,
  "pages_per_domain": {
    "example.com": 10,
    "test.com": 3,
    "demo.com": 2
  }
}
```

### 6. Get Indexed Pages

**Endpoint:** `GET /pages`

**Description:** Mendapatkan daftar halaman yang telah diindeks

**Parameters:**
- `domain` (optional): Filter berdasarkan domain
- `limit` (optional): Maksimal jumlah hasil (default: 20, max: 100)
- `offset` (optional): Offset untuk pagination (default: 0)

**Example Request:**
```bash
curl "http://localhost:5000/api/pages?domain=example.com&limit=10&offset=0"
```

**Example Response:**
```json
{
  "pages": [
    {
      "id": 1,
      "url": "https://example.com",
      "title": "Example Domain",
      "content": "Example Domain Example Domain This domain is for use...",
      "description": "Example domain for documentation",
      "keywords": "example, domain, test",
      "domain": "example.com",
      "crawled_at": "2025-06-30T03:56:45.123456",
      "last_updated": "2025-06-30T03:56:45.123456",
      "is_active": true
    }
  ],
  "total": 1,
  "limit": 10,
  "offset": 0
}
```

## Error Responses

### 400 Bad Request
```json
{
  "error": "Query parameter 'q' is required"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error"
}
```

## Rate Limiting

Saat ini tidak ada rate limiting yang diimplementasikan. Untuk production, disarankan untuk menambahkan rate limiting.

## CORS

API mendukung CORS untuk semua origin. Header yang diset:
- `Access-Control-Allow-Origin: *`
- `Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS`
- `Access-Control-Allow-Headers: Content-Type, Authorization`

## Data Models

### Page Model
```json
{
  "id": "integer",
  "url": "string (max 500 chars)",
  "title": "string (max 200 chars)",
  "content": "text",
  "description": "text",
  "keywords": "string (max 500 chars)",
  "domain": "string (max 100 chars)",
  "crawled_at": "datetime (ISO format)",
  "last_updated": "datetime (ISO format)",
  "is_active": "boolean"
}
```

### Domain Model
```json
{
  "id": "integer",
  "domain": "string (max 100 chars)",
  "is_active": "boolean",
  "added_at": "datetime (ISO format)"
}
```

## Usage Examples

### Python Example
```python
import requests

# Search for pages
response = requests.get('http://localhost:5000/api/search', params={'q': 'example'})
results = response.json()

# Add domain
response = requests.post('http://localhost:5000/api/domains', 
                        json={'domain': 'newdomain.com'})

# Crawl URLs
response = requests.post('http://localhost:5000/api/crawl',
                        json={'urls': ['https://example.com']})
```

### JavaScript Example
```javascript
// Search for pages
fetch('/api/search?q=example')
  .then(response => response.json())
  .then(data => console.log(data));

// Add domain
fetch('/api/domains', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({domain: 'newdomain.com'})
})
.then(response => response.json())
.then(data => console.log(data));

// Crawl URLs
fetch('/api/crawl', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({urls: ['https://example.com']})
})
.then(response => response.json())
.then(data => console.log(data));
```

## Notes

1. **Domain Validation**: Hanya URL dari domain yang terdaftar di `allowed_domains` yang dapat di-crawl
2. **Content Extraction**: Sistem mengekstrak teks dari HTML dan menghapus script, style, dan elemen navigasi
3. **Duplicate Handling**: URL yang sama akan di-update jika di-crawl ulang
4. **Search Algorithm**: Menggunakan LIKE query pada title, content, description, dan keywords
5. **Database**: Menggunakan SQLite untuk development, disarankan PostgreSQL untuk production

