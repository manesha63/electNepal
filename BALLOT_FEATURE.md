# Ballot Feature Implementation Documentation

## Overview
The Ballot feature allows users to view independent candidates in their voting area, sorted by location relevance. Users can either use their device's geolocation or manually select their location to see candidates from their ward, municipality, district, and province.

## Implementation Date
January 16, 2025

## Features Implemented

### 1. Geolocation Resolution API
**Endpoint**: `/api/georesolve/`
- **Method**: GET
- **Parameters**: `lat` (latitude), `lng` (longitude)
- **Returns**: Province, District, Municipality, and Ward information
- **Location**: `locations/views.py::geo_resolve()`

Currently uses a simple region-based approximation for Nepal's provinces:
- Validates coordinates are within Nepal boundaries (26.3-30.5°N, 80-88.2°E)
- Special handling for Kathmandu valley area
- Returns hierarchical location data (province → district → municipality → ward)

**Future Enhancement**: Implement PostGIS with proper polygon boundaries for accurate resolution.

### 2. My Ballot API
**Endpoint**: `/candidates/api/my-ballot/`
- **Method**: GET
- **Parameters**:
  - `province_id` (required)
  - `district_id` (optional)
  - `municipality_id` (optional)
  - `ward_number` (optional)
- **Returns**: Sorted list of candidates with relevance ranking
- **Location**: `candidates/views.py::my_ballot()`

**Sorting Logic**:
1. Exact ward match (priority 0)
2. Municipality match (priority 1)
3. District match (priority 2)
4. Province match (priority 3)
5. Federal level (priority 4)

Candidates are further sorted by verification status and name.

### 3. Ballot Page UI
**URL**: `/candidates/ballot/`
- **Template**: `templates/candidates/ballot.html`
- **View**: `candidates/views.py::ballot_view()`

**Features**:
- "Use My Location" button with browser geolocation API
- Manual location selection cascade (Province → District → Municipality → Ward)
- Real-time candidate display with relevance indicators
- Responsive grid layout with candidate cards
- Language-aware content (English/Nepali)
- Privacy notice about location usage

### 4. Frontend JavaScript (Alpine.js)
**Key Functions**:
- `requestLocation()`: Requests browser geolocation permission
- `resolveLocation()`: Converts coordinates to location hierarchy
- `loadDistricts()`, `loadMunicipalities()`: Cascade dropdown loading
- `loadCandidates()`: Fetches and displays candidates
- `searchManual()`: Manual location-based search

## API Endpoints Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/georesolve/` | GET | Resolve lat/lng to location |
| `/api/districts/` | GET | Get districts by province |
| `/api/municipalities/` | GET | Get municipalities by district |
| `/candidates/api/my-ballot/` | GET | Get sorted candidates by location |
| `/candidates/ballot/` | GET | Display ballot page |

## File Changes

### Modified Files:
1. `locations/views.py` - Added `geo_resolve()` function
2. `locations/urls.py` - Added georesolve endpoint
3. `candidates/views.py` - Added `my_ballot()` and `ballot_view()` functions
4. `candidates/urls.py` - Added ballot endpoints
5. `templates/base.html` - Updated Ballot navigation link

### New Files:
1. `templates/candidates/ballot.html` - Ballot page template
2. `BALLOT_FEATURE.md` - This documentation

## User Experience Flow

1. **User clicks "Ballot" in navigation**
   - Directed to `/candidates/ballot/` page

2. **Option A: Use Geolocation**
   - Click "Use My Location" button
   - Browser prompts for location permission
   - If allowed: Coordinates sent to `/api/georesolve/`
   - Location resolved to Province/District/Municipality
   - Candidates loaded and sorted by relevance

3. **Option B: Manual Selection**
   - Select Province from dropdown
   - Districts load automatically
   - Select District (optional)
   - Municipalities load automatically
   - Select Municipality (optional)
   - Enter Ward number (optional)
   - Click "Search Candidates"
   - Candidates loaded and sorted by relevance

## Privacy & Security

- **No coordinate storage**: Location coordinates are processed in-memory only
- **HTTPS recommended**: Geolocation API requires secure context in production
- **User consent**: Clear messaging about location usage
- **Graceful fallback**: Manual selection always available

## Testing

### API Testing:
```bash
# Test georesolve (Kathmandu coordinates)
curl "http://localhost:8000/api/georesolve/?lat=27.7&lng=85.3"

# Test my-ballot
curl "http://localhost:8000/candidates/api/my-ballot/?province_id=3&district_id=27"
```

### Manual Testing:
1. Navigate to `/candidates/ballot/`
2. Test "Use My Location" (allow and deny scenarios)
3. Test manual selection cascade
4. Verify candidate sorting by relevance
5. Test language switching (English/Nepali)

## Known Limitations

1. **Approximate Geolocation**: Currently uses simple lat/lng ranges for provinces
2. **No Ward Polygons**: Ward-level resolution not available via geolocation
3. **Limited to 50 Candidates**: Results capped for performance
4. **No Caching**: Results fetched fresh each time

## Future Enhancements

### Short Term:
1. Implement result caching (Redis)
2. Add pagination for large result sets
3. Include candidate photos in results
4. Add "View Profile" links to candidate cards

### Long Term:
1. **PostGIS Integration**:
   - Install PostGIS extension
   - Add geometry fields to location models
   - Load official Nepal boundary shapefiles
   - Use ST_Contains for accurate point-in-polygon queries

2. **Ward Boundaries**:
   - Source ward-level boundary data
   - Implement ward-level geolocation resolution

3. **Enhanced Sorting**:
   - Add user preferences for sorting
   - Include election type (federal/provincial/local)
   - Distance-based sorting within same level

4. **Performance**:
   - Implement server-side caching
   - Add database indexes for location queries
   - Use select_related/prefetch_related optimization

## Database Indexes Recommended

```sql
-- For better performance
CREATE INDEX idx_candidate_location ON candidates_candidate(province_id, district_id, municipality_id, ward_number);
CREATE INDEX idx_candidate_position ON candidates_candidate(position_level);
CREATE INDEX idx_candidate_status ON candidates_candidate(verification_status);
```

## Deployment Considerations

1. **HTTPS Required**: Browser geolocation requires secure context
2. **CORS Headers**: May need configuration for API access
3. **Rate Limiting**: Consider adding for georesolve endpoint
4. **Error Logging**: Implement proper error tracking
5. **Analytics**: Track location resolution success rates

## Support & Maintenance

- **Contact**: chandmanisha002@gmail.com
- **Dependencies**: Alpine.js 3.x, Django 4.2.7
- **Browser Support**: Modern browsers with Geolocation API

---

## Summary

The Ballot feature successfully implements location-based candidate discovery with both automatic (geolocation) and manual selection options. The implementation prioritizes user privacy, provides graceful fallbacks, and maintains consistency with the existing ElectNepal design system. The feature is fully bilingual and responsive across devices.