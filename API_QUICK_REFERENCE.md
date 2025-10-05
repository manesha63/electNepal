# ElectNepal API - Quick Reference

## 📚 Documentation URLs

| Resource | URL | Description |
|----------|-----|-------------|
| **Swagger UI** | http://localhost:8000/api/docs/ | Interactive API explorer |
| **ReDoc** | http://localhost:8000/api/redoc/ | Beautiful documentation |
| **OpenAPI Schema** | http://localhost:8000/api/schema/ | Raw specification |

## 🚀 Quick Start

### 1. View Documentation
```bash
# Start the server
python manage.py runserver

# Open in browser
http://localhost:8000/api/docs/
```

### 2. Test All Endpoints
```bash
python test_api_endpoints.py
```

### 3. Download API Schema
```bash
curl http://localhost:8000/api/schema/ > openapi.yaml
```

## 📍 Location APIs

### Get Districts
```bash
# All districts
curl http://localhost:8000/api/districts/

# Districts in province 1
curl "http://localhost:8000/api/districts/?province=1"
```

### Get Municipalities
```bash
# All municipalities
curl http://localhost:8000/api/municipalities/

# Municipalities in district 1
curl "http://localhost:8000/api/municipalities/?district=1"
```

### Get Municipality Wards
```bash
curl http://localhost:8000/api/municipalities/1/wards/
```

### Get Statistics
```bash
curl http://localhost:8000/api/statistics/
```

## 👥 Candidate APIs

### Get Candidate Cards
```bash
# Basic list (page 1, 9 items)
curl http://localhost:8000/candidates/api/cards/

# With pagination
curl "http://localhost:8000/candidates/api/cards/?page=1&page_size=20"

# Search candidates
curl "http://localhost:8000/candidates/api/cards/?q=test"

# Filter by province
curl "http://localhost:8000/candidates/api/cards/?province=1"

# Filter by position
curl "http://localhost:8000/candidates/api/cards/?position=ward"

# Combined filters
curl "http://localhost:8000/candidates/api/cards/?province=1&position=ward&page=1"
```

### Get My Ballot
```bash
# Full location specified
curl "http://localhost:8000/candidates/api/my-ballot/?province_id=1&district_id=1&municipality_id=1&ward_number=1"

# With pagination
curl "http://localhost:8000/candidates/api/my-ballot/?province_id=1&district_id=1&page_size=10"
```

## 🔍 Common Filters

### Position Types
- `federal` - Federal level
- `provincial` - Provincial level
- `mayor` - Mayor
- `deputy_mayor` - Deputy Mayor
- `ward` - Ward Chairperson
- `ward_member` - Ward Member
- `womens_member` - Women's Member
- `dalit_womens_member` - Dalit Women's Member
- `local_executive` - Local Executive

### Pagination Parameters
- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 9, max: 48)

### Search Parameter
- `q` - Search query (searches name and bio)

## 📊 Response Format

### Paginated Response
```json
{
  "results": [...],
  "total": 50,
  "page": 1,
  "page_size": 9,
  "total_pages": 6,
  "has_next": true,
  "has_previous": false
}
```

### Candidate Card
```json
{
  "id": 1,
  "full_name": "John Doe",
  "bio_en": "English bio",
  "bio_ne": "नेपाली बायो",
  "position_level": "ward",
  "position_display": "Ward Chairperson",
  "photo_url": "http://localhost:8000/media/...",
  "status": "approved",
  "province_name": "Koshi",
  "district_name": "Bhojpur",
  "municipality_name": "Bhojpur",
  "ward_number": 1,
  "location": "Ward 1, Bhojpur, Bhojpur, Koshi"
}
```

### Ballot Candidate
```json
{
  "id": 1,
  "full_name": "Jane Smith",
  "relevance_score": 5,
  "location_match": "Exact Ward Match",
  ...
}
```

## 🧪 Testing

### Run All Tests
```bash
python test_api_endpoints.py
```

### Expected Output
```
Total Tests: 14
Passed: 14 ✓
Failed: 0 ✗
Success Rate: 100.0%
🎉 All tests passed!
```

## 📖 Documentation Files

- `API_DOCUMENTATION.md` - Complete API reference
- `API_IMPLEMENTATION_SUMMARY.md` - Implementation details
- `API_QUICK_REFERENCE.md` - This file
- `CLAUDE.md` - Project documentation (Section 16)

## 🔗 Related Files

- `/home/manesha/electNepal/api_documentation.py` - Documentation views
- `/home/manesha/electNepal/locations/api_views.py` - Location APIs
- `/home/manesha/electNepal/locations/serializers.py` - Location serializers
- `/home/manesha/electNepal/candidates/api_views.py` - Candidate APIs
- `/home/manesha/electNepal/candidates/serializers.py` - Candidate serializers
- `/home/manesha/electNepal/test_api_endpoints.py` - Test suite

## 💡 Tips

1. **Use Swagger UI** for testing APIs interactively
2. **Use ReDoc** for beautiful documentation reading
3. **Download schema** to generate client SDKs
4. **Run tests** before deploying to verify all endpoints work
5. **Check pagination** for large result sets

## 🌐 Bilingual Support

All content is available in both languages:
- `*_en` fields = English content
- `*_ne` fields = Nepali content

Example:
- `bio_en` - English biography
- `bio_ne` - Nepali biography (नेपाली)

---

**Quick Links:**
- Swagger UI: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/
- Schema: http://localhost:8000/api/schema/
