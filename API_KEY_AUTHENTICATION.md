# API Key Authentication System

## Overview

ElectNepal now implements secure API Key authentication for all API endpoints. This allows controlled access to the API by developers, partners, and third-party applications.

## Features

✅ **Secure API Keys**: 256-bit random tokens with `eln_` prefix
✅ **Usage Tracking**: Monitors every API call with logs
✅ **Rate Limiting**: Configurable requests per hour (default: 1000)
✅ **Permission Control**: Read/Write access management
✅ **Automatic Expiration**: Optional expiry dates for keys
✅ **Admin Interface**: Full management through Django admin
✅ **Caching**: Performance optimized with Redis cache support
✅ **OpenAPI Documentation**: API keys integrated in Swagger UI

## Authentication Methods

### 1. API Key Authentication (Recommended for External Apps)
```bash
curl -H "X-API-Key: eln_YOUR_API_KEY_HERE" \
  http://localhost:8000/api/districts/
```

### 2. Session Authentication (For Logged-in Users)
Users who are logged into the website can access APIs through their session cookies.

## Creating API Keys

### Via Management Command (Recommended)

```bash
python manage.py create_api_key \
  --name "Mobile App" \
  --email "developer@example.com" \
  --organization "Example Inc" \
  --rate-limit 5000
```

**Output:**
```
======================================================================
API Key Created Successfully!
======================================================================

Name:         Mobile App
Organization: Example Inc
Email:        developer@example.com
User:         N/A
Permissions:  Read: ✓ | Write: ✗
Rate Limit:   5000 requests/hour

API Key (save this - it won't be shown again):
eln_Org5FPPeMrWV3P2vBlXZh92X4E4Pt6mnzzySAT0iZ6M

======================================================================
```

### Via Django Admin

1. Go to http://localhost:8000/admin/
2. Navigate to **API Auth > API Keys**
3. Click **Add API Key**
4. Fill in the required fields
5. The system auto-generates a secure key on save

## API Key Permissions

### Read-Only Access (Default)
- Can fetch data from all GET endpoints
- Cannot modify, create, or delete resources
- Suitable for public data consumers

### Read-Write Access
```bash
python manage.py create_api_key \
  --name "Admin Tool" \
  --email "admin@example.com" \
  --can-write
```
- Full access to all API endpoints
- Can create, update, and delete resources
- Requires explicit `--can-write` flag

## Rate Limiting

### Default Limits
- **Anonymous Users**: No limit (read-only access via DRF permission)
- **API Key Users**: 1000 requests/hour (configurable per key)

### Customizing Rate Limits
```bash
python manage.py create_api_key \
  --name "Premium Partner" \
  --email "partner@example.com" \
  --rate-limit 10000  # 10,000 requests/hour
```

### Rate Limit Response
When rate limit is exceeded:
```json
{
  "detail": "Rate limit exceeded"
}
```

## Usage Tracking

Every API request is automatically logged with:
- **Endpoint**: Which API was called
- **Method**: GET, POST, PUT, DELETE, etc.
- **IP Address**: Client IP address
- **User Agent**: Browser/app information
- **Response Status**: HTTP status code
- **Timestamp**: When the request was made

### Viewing Usage Logs

**Django Admin:**
1. Go to **API Auth > API Key Usage Logs**
2. Filter by API key, method, or date
3. Export data for analytics

**Python Shell:**
```python
from api_auth.models import APIKey, APIKeyUsageLog

# Get usage for specific key
key = APIKey.objects.get(name="Mobile App")
print(f"Total Requests: {key.total_requests}")
print(f"Last Used: {key.last_used}")

# Get recent logs
recent_logs = APIKeyUsageLog.objects.filter(api_key=key)[:10]
for log in recent_logs:
    print(f"{log.timestamp} - {log.method} {log.endpoint}")
```

## API Endpoints with Authentication

### Location APIs (Public Read)
```bash
# Get all districts
curl -H "X-API-Key: YOUR_KEY" http://localhost:8000/api/districts/

# Get districts by province
curl -H "X-API-Key: YOUR_KEY" http://localhost:8000/api/districts/?province=3

# Get municipalities by district
curl -H "X-API-Key: YOUR_KEY" http://localhost:8000/api/municipalities/?district=27

# Get ward count for municipality
curl -H "X-API-Key: YOUR_KEY" http://localhost:8000/api/municipalities/1/wards/

# Get location statistics
curl -H "X-API-Key: YOUR_KEY" http://localhost:8000/api/statistics/
```

### Candidate APIs (Public Read)
```bash
# Get candidate cards with filters
curl -H "X-API-Key: YOUR_KEY" \
  "http://localhost:8000/candidates/api/cards/?province=3&page=1&page_size=10"

# Get personalized ballot
curl -H "X-API-Key: YOUR_KEY" \
  "http://localhost:8000/candidates/api/my-ballot/?province_id=3&district_id=27"
```

## Security Best Practices

### 1. Keep API Keys Secret
❌ **DON'T**: Commit keys to Git repositories
❌ **DON'T**: Share keys in public forums
❌ **DON'T**: Hardcode keys in client-side JavaScript

✅ **DO**: Store in environment variables
✅ **DO**: Use server-side code for API calls
✅ **DO**: Rotate keys periodically

### 2. Use HTTPS in Production
```python
# settings/production.py
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
```

### 3. Set Expiration Dates
For temporary partners or trials:
```python
from datetime import timedelta
from django.utils import timezone

key = APIKey.objects.get(name="Trial Account")
key.expires_at = timezone.now() + timedelta(days=30)
key.save()
```

### 4. Deactivate Compromised Keys
```python
key = APIKey.objects.get(name="Compromised Key")
key.is_active = False
key.save()
```

## Error Responses

### Invalid API Key
```json
{
  "detail": "Invalid API key"
}
```

### Expired API Key
```json
{
  "detail": "API key is inactive or expired"
}
```

### Rate Limit Exceeded
```json
{
  "detail": "Rate limit exceeded"
}
```

### Missing Permissions
```json
{
  "detail": "You do not have permission to perform this action."
}
```

## Integration Examples

### JavaScript (Node.js)
```javascript
const axios = require('axios');

const apiKey = process.env.ELECTNEPAL_API_KEY;

axios.get('http://localhost:8000/api/districts/', {
  headers: {
    'X-API-Key': apiKey
  }
})
.then(response => {
  console.log(response.data);
})
.catch(error => {
  console.error('API Error:', error.response.data);
});
```

### Python
```python
import os
import requests

api_key = os.getenv('ELECTNEPAL_API_KEY')

response = requests.get(
    'http://localhost:8000/api/districts/',
    headers={'X-API-Key': api_key}
)

if response.status_code == 200:
    data = response.json()
    print(f"Found {len(data)} districts")
else:
    print(f"Error: {response.json()}")
```

### cURL
```bash
export API_KEY="eln_YOUR_API_KEY_HERE"

curl -H "X-API-Key: $API_KEY" \
  "http://localhost:8000/api/districts/?province=3"
```

## Testing API Keys

### Test Suite
```bash
# Create a test key
python manage.py create_api_key \
  --name "Test Key" \
  --email "test@example.com"

# Test valid key
curl -H "X-API-Key: YOUR_KEY" http://localhost:8000/api/districts/

# Test invalid key
curl -H "X-API-Key: invalid_key" http://localhost:8000/api/districts/

# Test without key (should still work for read-only)
curl http://localhost:8000/api/districts/
```

## Admin Interface

### API Key List View
- Color-coded status badges (Active/Inactive)
- Permission badges (Read/Write)
- Usage statistics (total requests, last used)
- Search by name, organization, email
- Filter by status, permissions

### API Key Detail View
- **Key Information**: Auto-generated key, name
- **Owner Information**: User, organization, email
- **Permissions**: Active status, read/write, rate limit, expiration
- **Usage Statistics**: Total requests, last used timestamp
- **Metadata**: Notes, created/updated dates

### Usage Log View
- Read-only log viewer
- Filter by method, status, date
- Search by endpoint, IP address
- Date hierarchy for easy navigation

## Production Deployment

### 1. Update Settings
```python
# settings/production.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

### 2. Configure Environment
```bash
export DJANGO_SETTINGS_MODULE=nepal_election_app.settings.production
export ELECTNEPAL_API_KEY=your_production_key
```

### 3. Monitor Usage
- Set up alerts for rate limit violations
- Review usage logs regularly
- Rotate keys periodically (every 90 days)

## FAQ

### Q: Can I use multiple API keys?
**A:** Yes! Create separate keys for each application/partner for better tracking.

### Q: What happens if I lose my API key?
**A:** Generate a new key and deactivate the old one. Keys cannot be retrieved once created.

### Q: Can I increase my rate limit?
**A:** Yes, contact admin or update via Django admin panel.

### Q: Are API keys required for all endpoints?
**A:** No, read-only access works without API keys. Keys provide authentication and tracking.

### Q: How do I revoke access?
**A:** Deactivate the API key in Django admin or set `is_active=False`.

## Support

For API key issues or questions:
- **Email**: chandmanisha002@gmail.com
- **Admin Panel**: http://localhost:8000/admin/api_auth/
- **Documentation**: http://localhost:8000/api/docs/

---

**Implementation Date**: October 5, 2025
**Version**: 1.0.0
**Status**: ✅ Production Ready