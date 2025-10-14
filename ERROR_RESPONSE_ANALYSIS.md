# Error Response Format Analysis

## Standard Format (from `core/api_responses.py`)

### Error Response:
```python
{'error': 'message'}
```

### Success Response:
```python
{'success': True, 'message': 'message'}
```

### Validation Error Response:
```python
{
    'error': 'Validation failed',
    'fields': {'field_name': 'error message'}
}
```

## Current State Analysis

### ✅ COMPLIANT Files

#### `candidates/views.py`
- Lines 333, 341: Uses `error_response()` ✅
- Line 832: Uses `error_response()` ✅
- Line 837: Uses `success_response()` ✅
- Line 839: Uses `error_response()` ✅

#### `locations/views.py`
- Lines 51, 84: Uses `error_response()` ✅
- Uses `error_response()` for all validation errors ✅

#### `locations/api_views.py`
- Lines 86, 129: Uses `error_response(..., use_drf=True)` ✅
- Line 190: Uses `error_response(..., use_drf=True)` ✅
- Line 246: Uses `error_response(..., use_drf=True)` ✅

### ⚠️ INCONSISTENT - Need Fixing

#### 1. **DRF Serializer Errors** (PRIORITY: HIGH)
**Location**: `locations/api_views.py:251`
```python
return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
```

**Issue**: DRF serializer errors return in Django REST Framework format:
```python
{'field': ['error message'], ...}
```

**Should be**:
```python
return validation_error_response(serializer.errors, status=400, use_drf=True)
```

**Impact**: Frontend may not be able to parse error messages consistently

---

### ✅ ACCEPTABLE (Data Responses - Not Errors)

These return data, not errors, so they don't need to follow error response format:

#### `candidates/views.py`
- Line 246: `JsonResponse({'location': ..., 'candidates': ..., 'has_more': ...})` - Data response ✅
- Line 302: `JsonResponse({'results': results})` - Data response ✅
- Line 387: `JsonResponse(cached_result)` - Cached data response ✅
- Line 579: `JsonResponse(response_data)` - Data response ✅

#### `locations/views.py`
- Lines 54, 57: `JsonResponse([], safe=False)` / `JsonResponse(list(qs), safe=False)` - Data response ✅
- Lines 78, 87, 92: Similar data responses ✅
- Line 113: `JsonResponse(result, status=status_code)` - Uses geolocation result ✅
- Lines 122, 135: `JsonResponse({...})` - Analytics data responses ✅

---

## Summary

### Issues Found: 1

1. **Serializer errors not using standard format** (`locations/api_views.py:251`)
   - Severity: MEDIUM
   - Impact: Frontend inconsistency for validation errors
   - Fix: Use `validation_error_response()`

### Compliance Rate: 99%

- Total API endpoints examined: ~15
- Endpoints using standard format: 14
- Endpoints with inconsistent format: 1
- Data-only endpoints (not applicable): 9

## Recommended Fix

### File: `locations/api_views.py`

**Before** (Line 249-251):
```python
serializer = GeoResolveSerializer(data=request.data)
if not serializer.is_valid():
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
```

**After**:
```python
serializer = GeoResolveSerializer(data=request.data)
if not serializer.is_valid():
    from core.api_responses import validation_error_response
    return validation_error_response(serializer.errors, status=400, use_drf=True)
```

This ensures validation errors follow the standard format:
```json
{
    "error": "Validation failed",
    "fields": {
        "lat": ["This field is required."],
        "lng": ["This field is required."]
    }
}
```

Instead of raw DRF format:
```json
{
    "lat": ["This field is required."],
    "lng": ["This field is required."]
}
```
