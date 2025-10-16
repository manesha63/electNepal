# ElectNepal API Documentation

## Overview

ElectNepal provides a comprehensive RESTful API for accessing information about independent candidates in Nepal elections. The API is documented using OpenAPI 3.0 specification with interactive documentation available via Swagger UI and ReDoc.

**Base URL**: `http://localhost:8000` (Development)

## API Documentation Interfaces

### Swagger UI (Interactive API Explorer)
- **URL**: `/api/docs/`
- **Features**:
  - Interactive API testing
  - Request/response examples
  - Parameter documentation
  - Try-it-out functionality

### ReDoc (Beautiful API Documentation)
- **URL**: `/api/redoc/`
- **Features**:
  - Clean, responsive interface
  - Detailed schema documentation
  - Code samples
  - Search functionality

### OpenAPI Schema (Raw Specification)
- **URL**: `/api/schema/`
- **Format**: YAML/JSON
- **Use**: Import into API clients, generate SDKs

## Authentication

Currently, the API endpoints are publicly accessible. Authentication will be added in future versions for protected resources.

## API Endpoints

### Location APIs

#### 1. Get All Districts
```
GET /api/districts/
```

**Description**: Returns a list of all 77 districts in Nepal.

**Query Parameters**:
- `province` (optional, integer): Filter districts by province ID

**Response Example**:
```json
[
  {
    "id": 1,
    "code": "D01",
    "name_en": "Bhojpur",
    "name_ne": "भोजपुर",
    "province": 1,
    "province_name": "Koshi",
    "municipalities_count": 9
  }
]
```

#### 2. Get All Municipalities
```
GET /api/municipalities/
```

**Description**: Returns a list of all 753 municipalities in Nepal.

**Query Parameters**:
- `district` (optional, integer): Filter municipalities by district ID

**Response Example**:
```json
[
  {
    "id": 1,
    "code": "M0101",
    "name_en": "Bhojpur",
    "name_ne": "भोजपुर",
    "district": 1,
    "district_name": "Bhojpur",
    "municipality_type": "municipality",
    "type_display": "Municipality",
    "total_wards": 10
  }
]
```

#### 3. Get Municipality Wards
```
GET /api/municipalities/{municipality_id}/wards/
```

**Description**: Returns ward information for a specific municipality.

**Path Parameters**:
- `municipality_id` (required, integer): Municipality ID

**Response Example**:
```json
{
  "municipality_id": 1,
  "municipality_name": "Bhojpur",
  "total_wards": 10,
  "ward_numbers": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
}
```

#### 4. Get Location Statistics
```
GET /api/statistics/
```

**Description**: Returns statistical information about Nepal's administrative divisions.

**Response Example**:
```json
{
  "total_provinces": 7,
  "total_districts": 77,
  "total_municipalities": 753,
  "total_wards": 6743,
  "municipalities_by_type": {
    "Metropolitan City": 6,
    "Sub-Metropolitan City": 11,
    "Municipality": 276,
    "Rural Municipality": 460
  },
  "last_updated": "2025-10-05T21:07:32.860170Z"
}
```

#### 5. Resolve GPS Coordinates
```
POST /api/georesolve/
```

**Description**: Converts GPS coordinates to Nepal administrative location (placeholder implementation).

**Request Body**:
```json
{
  "lat": 27.7172,
  "lng": 85.3240
}
```

**Note**: This is a placeholder endpoint. Full geolocation resolution requires geospatial data and libraries like GeoDjango.

### Candidate APIs

#### 1. Get Candidate Cards
```
GET /candidates/api/cards/
```

**Description**: Returns paginated list of approved candidates for the main feed display.

**Query Parameters**:
- `page` (optional, integer, default: 1): Page number
- `page_size` (optional, integer, default: 9, max: 48): Items per page
- `q` (optional, string): Search query for candidate name or bio
- `province` (optional, integer): Filter by province ID
- `district` (optional, integer): Filter by district ID
- `municipality` (optional, integer): Filter by municipality ID
- `position` (optional, string): Filter by position level

**Position Options**:
- `federal` - Federal level
- `provincial` - Provincial level
- `mayor` - Mayor
- `deputy_mayor` - Deputy Mayor
- `ward` - Ward Chairperson
- `ward_member` - Ward Member
- `womens_member` - Women's Member
- `dalit_womens_member` - Dalit Women's Member
- `local_executive` - Local Executive

**Response Example**:
```json
{
  "results": [
    {
      "id": 1,
      "full_name": "John Doe",
      "bio_en": "Committed to serving the community...",
      "bio_ne": "समुदायको सेवा गर्न प्रतिबद्ध...",
      "position_level": "ward",
      "position_display": "Ward Chairperson",
      "photo_url": "http://localhost:8000/media/candidates/...",
      "status": "approved",
      "status_color": "green",
      "province_name": "Koshi",
      "district_name": "Bhojpur",
      "municipality_name": "Bhojpur",
      "ward_number": 1,
      "location": "Ward 1, Bhojpur, Bhojpur, Koshi",
      "created_at": "2025-09-29T23:14:12.573421+05:45"
    }
  ],
  "total": 50,
  "page": 1,
  "page_size": 9,
  "total_pages": 6,
  "has_next": true,
  "has_previous": false
}
```

#### 2. Get My Ballot
```
GET /candidates/api/my-ballot/
```

**Description**: Returns candidates for the user's ballot based on their location. Candidates are sorted by relevance (exact ward match > municipality > district > province > federal).

**Query Parameters**:
- `province_id` (optional, integer): User's province ID
- `district_id` (optional, integer): User's district ID
- `municipality_id` (optional, integer): User's municipality ID
- `ward_number` (optional, integer): User's ward number
- `page` (optional, integer, default: 1): Page number
- `page_size` (optional, integer, default: 20, max: 100): Items per page

**Response Example**:
```json
{
  "candidates": [
    {
      "id": 15,
      "full_name": "Jane Smith",
      "bio_en": "Local leader with 10 years experience...",
      "bio_ne": "१० वर्षको अनुभव भएको स्थानीय नेता...",
      "position_level": "ward",
      "photo_url": null,
      "province_name": "Koshi",
      "district_name": "Bhojpur",
      "municipality_name": "Bhojpur",
      "ward_number": 1,
      "relevance_score": 5,
      "location_match": "Exact Ward Match"
    }
  ],
  "location": {
    "province": "Koshi",
    "district": "Bhojpur",
    "municipality": "Bhojpur",
    "ward": 1
  },
  "total": 13,
  "page": 1,
  "page_size": 20,
  "total_pages": 1,
  "has_next": false,
  "has_previous": false
}
```

**Relevance Scoring**:
- Score 5: Exact Ward Match (same municipality, same ward, ward-level position)
- Score 4: Municipality Match (same municipality, municipality-level position)
- Score 3: District Match (same district)
- Score 2: Provincial Match (same province, provincial position)
- Score 1: Federal Level (federal position)
- Score 0: Other

## Data Models

### Province
- `id`: Integer (Primary Key)
- `code`: String (10 chars, unique)
- `name_en`: English name (100 chars)
- `name_ne`: Nepali name (100 chars)
- `districts_count`: Integer (related districts count)

### District
- `id`: Integer (Primary Key)
- `code`: String (10 chars, unique)
- `name_en`: English name (100 chars)
- `name_ne`: Nepali name (100 chars)
- `province`: Foreign Key to Province
- `province_name`: String (related)
- `municipalities_count`: Integer (related municipalities count)

### Municipality
- `id`: Integer (Primary Key)
- `code`: String (20 chars, unique)
- `name_en`: English name (100 chars)
- `name_ne`: Nepali name (100 chars)
- `district`: Foreign Key to District
- `district_name`: String (related)
- `municipality_type`: Choice Field
  - `metropolitan_city`
  - `sub_metropolitan_city`
  - `municipality`
  - `rural_municipality`
- `type_display`: String (human-readable type)
- `total_wards`: Integer (1-35)

### Candidate
- `id`: Integer (Primary Key)
- `full_name`: String
- `bio_en`: Text (English biography)
- `bio_ne`: Text (Nepali biography)
- `education_en`: Text (English)
- `education_ne`: Text (Nepali)
- `experience_en`: Text (English)
- `experience_ne`: Text (Nepali)
- `manifesto_en`: Text (English)
- `manifesto_ne`: Text (Nepali)
- `position_level`: Choice Field (see position options above)
- `photo_url`: String (full URL to photo)
- `status`: Choice Field
  - `pending`: Awaiting approval
  - `approved`: Published
  - `rejected`: Not approved
- `province`: Foreign Key to Province
- `district`: Foreign Key to District
- `municipality`: Foreign Key to Municipality (optional)
- `ward_number`: Integer (1-35, optional)
- `created_at`: DateTime
- `updated_at`: DateTime

## Error Responses

### 400 Bad Request
```json
{
  "error": "Invalid parameter value"
}
```

### 404 Not Found
```json
{
  "error": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error"
}
```

## Pagination

All list endpoints support pagination with the following parameters:
- `page`: Page number (starts at 1)
- `page_size`: Number of items per page

Response includes:
- `total`: Total number of items
- `page`: Current page number
- `page_size`: Items per page
- `total_pages`: Total number of pages
- `has_next`: Boolean indicating if there's a next page
- `has_previous`: Boolean indicating if there's a previous page

## Filtering and Search

### Location-based Filtering
Use cascading filters to narrow down results:
1. Filter by province
2. Then by district (within province)
3. Then by municipality (within district)
4. Then by ward (within municipality)

### Search
The `q` parameter searches across:
- Candidate full name
- English biography
- Nepali biography

## Bilingual Support

All location names and candidate content are available in both English and Nepali:
- Fields ending in `_en` contain English content
- Fields ending in `_ne` contain Nepali content

Content is automatically translated using machine translation when saved.

## Rate Limiting

(To be implemented in production)

## Versioning

Current API Version: 1.0.0

Version information is included in the OpenAPI schema and documentation headers.

## Testing

Use the included test script to verify all endpoints:

```bash
python test_api_endpoints.py
```

## Development Tools

### View API Documentation
- Swagger UI: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/

### Download OpenAPI Schema
```bash
curl http://localhost:8000/api/schema/ > openapi.yaml
```

### Generate API Client
Use the OpenAPI schema to generate client libraries in various languages using tools like:
- OpenAPI Generator
- Swagger Codegen
- AutoRest

## Support

For API support and questions:
- Email: electnepal5@gmail.com
- GitHub Issues: [Repository URL]

## Changelog

### Version 1.0.0 (2025-10-05)
- Initial API documentation with drf-spectacular
- Location APIs (districts, municipalities, wards, statistics)
- Candidate APIs (cards, ballot, search, filters)
- Bilingual support for all content
- Paginated responses
- OpenAPI 3.0 specification
- Interactive documentation (Swagger UI, ReDoc)

---

**Last Updated**: October 5, 2025
**API Version**: 1.0.0
**Django Version**: 4.2.7
**DRF Version**: 3.16.1
**drf-spectacular Version**: 0.28.0
