# ElectNepal - Empowering Democracy in Nepal 🇳🇵

[![Django](https://img.shields.io/badge/Django-4.2.7-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.12.3-blue.svg)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue.svg)](https://www.postgresql.org/)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-success.svg)]()
[![Bilingual](https://img.shields.io/badge/Bilingual-EN%2FNE-success.svg)]()
[![API](https://img.shields.io/badge/API-OpenAPI%203.0-blue.svg)]()

## 🎯 Project Overview

ElectNepal is a production-ready Django-based web application for tracking and displaying independent candidates in Nepal elections. Built with enterprise-grade bilingual support (English/Nepali), the platform enables democratic participation by providing transparent candidate information to all Nepali citizens.

### ✨ Key Features

- **100% Automated Bilingual System** - Write once in English, display everywhere in both languages
- **Complete Nepal Administrative Data** - All 7 provinces, 77 districts, 753 municipalities
- **Candidate Management** - Comprehensive profiles with automatic translation and admin approval workflow
- **Location-Based Ballot System** - Find candidates based on GPS or manual location selection
- **RESTful API with OpenAPI Documentation** - Full Swagger/ReDoc documentation for all endpoints
- **API Key Authentication** - Secure API access with key-based authentication
- **Responsive Design** - Mobile-friendly interface with WeVote-inspired professional UI
- **Security Hardened** - Input sanitization, rate limiting, XSS protection, CSRF protection
- **Health Monitoring** - Built-in API health check endpoint for monitoring
- **Future-Proof** - Python 3.13+ ready, Django 5.x compatible

## 🚀 Quick Start

### Prerequisites

- Python 3.12.3+
- PostgreSQL 16+
- Virtual environment (venv)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/electNepal.git
cd electNepal
```

2. **Create and activate virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your database credentials
```

5. **Run migrations**
```bash
python manage.py migrate
```

6. **Load location data**
```bash
python manage.py load_nepal_locations --file data/nepal_locations.json
```

7. **Create superuser**
```bash
python manage.py createsuperuser
```

8. **Create API key (optional)**
```bash
python manage.py create_api_key "My App" --email your@email.com
```

9. **Run the development server**
```bash
python manage.py runserver 0.0.0.0:8000
```

Access the application:
- **Homepage**: http://localhost:8000/
- **Nepali Version**: http://localhost:8000/ne/
- **Admin Panel**: http://localhost:8000/admin/
- **API Documentation**: http://localhost:8000/api/docs/ (Swagger UI)
- **API ReDoc**: http://localhost:8000/api/redoc/
- **Health Check**: http://localhost:8000/api/health/

## 🌐 Bilingual System

### How It Works

The bilingual system is **100% automated**. Developers only write content in English, and the system automatically:
- Translates all content to Nepali using Google Translate API
- Caches translations for performance
- Displays the correct language based on URL prefix (`/` = English, `/ne/` = Nepali)
- Falls back gracefully if translation fails
- Tracks machine-translated content with flags

### Key Components

1. **AutoTranslationMixin** - Automatic translation on save for models
2. **Political Dictionary** - 139+ political/administrative terms with accurate translations
3. **Template Tags** - `{% trans %}` tags for UI text translation
4. **Language-Aware APIs** - Returns data based on URL prefix and Accept-Language header
5. **Smart Fallback** - Shows English if Nepali translation missing

For detailed documentation, see [BILINGUAL_SYSTEM_DOCUMENTATION.md](BILINGUAL_SYSTEM_DOCUMENTATION.md)

## 📁 Project Structure

```
electNepal/
├── nepal_election_app/     # Main Django project
│   ├── settings/           # Split settings (base, local, security, postgresql)
│   └── urls.py             # Main URL configuration with i18n patterns
├── core/                   # Core application (base models, utilities)
│   ├── sanitize.py         # Input sanitization utilities
│   └── management/         # Management commands
├── locations/              # Nepal administrative data
│   ├── models.py           # Province, District, Municipality models
│   ├── api_views.py        # RESTful API views with OpenAPI docs
│   └── geolocation.py      # GPS to location resolution
├── candidates/             # Candidate management
│   ├── models.py           # Candidate, CandidateEvent models
│   ├── views.py            # Web views (list, detail, registration)
│   ├── api_views.py        # API endpoints with pagination
│   ├── serializers.py      # DRF serializers
│   ├── forms.py            # Forms with sanitization
│   ├── validators.py       # File validators (Pillow-based)
│   └── translation.py      # Auto-translation system
├── authentication/         # User authentication
│   ├── views.py            # Signup, login, password reset
│   └── forms.py            # Authentication forms
├── api_auth/               # API key authentication
│   ├── authentication.py   # APIKeyAuthentication class
│   └── models.py           # APIKey model
├── analytics/              # Analytics tracking
│   └── middleware.py       # Page view tracking
├── templates/              # Global templates
│   ├── base.html           # Base template with nav/footer
│   ├── candidates/         # Candidate templates
│   └── authentication/     # Auth templates
├── static/                 # Static assets
│   ├── css/                # Custom CSS
│   ├── js/                 # JavaScript files
│   └── images/             # Image assets
├── locale/                 # i18n translation files (264 strings)
├── data/                   # Location data files
└── media/                  # User uploaded files
```

## 🛠️ Technical Stack

### Backend
- **Framework**: Django 4.2.7
- **Database**: PostgreSQL 16
- **API**: Django REST Framework 3.16.1
- **API Documentation**: drf-spectacular (OpenAPI 3.0)
- **Translation**: Google Translate API (googletrans 4.0.0rc1)
- **Authentication**: API Key + Session-based
- **Rate Limiting**: django-ratelimit 4.1.0
- **Security**: bleach 6.2.0 (input sanitization)

### Frontend
- **CSS**: Tailwind CSS (via CDN)
- **JavaScript**: Alpine.js
- **Fonts**: Inter, Noto Sans Devanagari
- **Icons**: Font Awesome 6

### Database Features
- **Full-Text Search**: PostgreSQL GIN indexes
- **Optimized Queries**: select_related, prefetch_related
- **Connection Pooling**: CONN_MAX_AGE for performance
- **Indexes**: Strategic indexes on foreign keys and search fields

## 📊 Current Status (Updated: October 13, 2025)

### ✅ Completed Features (100%)

#### Core Infrastructure
- ✅ Django 4.2.7 with split settings architecture
- ✅ PostgreSQL 16 database with optimized indexes
- ✅ Complete Nepal administrative data (7 provinces, 77 districts, 753 municipalities)
- ✅ Virtual environment with all dependencies

#### Bilingual System
- ✅ 100% automated translation system
- ✅ Political dictionary with 139+ terms
- ✅ Language-aware API responses
- ✅ 264 UI strings translated
- ✅ Machine translation tracking

#### Candidate Management
- ✅ Multi-step registration wizard
- ✅ Admin approval workflow (pending/approved/rejected)
- ✅ Auto-translation of all candidate content
- ✅ Profile dashboard for candidates
- ✅ Event management system
- ✅ Photo and document uploads with validation

#### Authentication & Security
- ✅ User signup/login/logout
- ✅ Password reset functionality
- ✅ Rate limiting (3 registrations/hour per user, 5/hour per IP)
- ✅ Input sanitization with bleach
- ✅ XSS protection
- ✅ CSRF protection
- ✅ SQL injection prevention (ORM)

#### API System
- ✅ RESTful API with DRF
- ✅ OpenAPI 3.0 documentation (Swagger UI + ReDoc)
- ✅ API key authentication
- ✅ Pagination support
- ✅ Language-aware endpoints
- ✅ Health check endpoint (`/api/health/`)
- ✅ Comprehensive error handling

#### File Handling
- ✅ Image validation (5MB max, JPEG/PNG)
- ✅ Document validation (10MB max, PDF)
- ✅ Magic byte validation (prevents fake files)
- ✅ Pillow-based validation (Python 3.13 ready)

#### UI/UX
- ✅ Responsive design (mobile-first)
- ✅ WeVote-inspired professional theme
- ✅ Location-based ballot system
- ✅ GPS geolocation support
- ✅ Search and filtering
- ✅ Paginated candidate feed

#### Code Quality
- ✅ Comprehensive test suite
- ✅ PEP 8 compliant naming
- ✅ No deprecated imports
- ✅ Specific exception handling
- ✅ Django system checks passing

### 🔄 Optional Enhancements

- [ ] Email verification system
- [ ] Docker containerization
- [ ] CI/CD pipeline
- [ ] Advanced analytics dashboard
- [ ] Social media OAuth integration

## 🚀 Recent Updates (October 2025)

### Issue Fixes (Issues #41-#48)
- **#41**: ✅ Replaced broad exception catching with specific handlers
- **#42**: ✅ Added comprehensive input sanitization with bleach
- **#43**: ✅ Optimized API serializers (34-47% smaller payloads)
- **#44**: ✅ Added API health check endpoint
- **#45**: ✅ Fixed misleading code comment
- **#46**: ✅ Verified PEP 8 naming compliance (no issues found)
- **#48**: ✅ Replaced deprecated `imghdr` with Pillow (Python 3.13 ready)

### Security Enhancements
- Added HTML sanitization for all form inputs (34 fields protected)
- Implemented rate limiting on candidate registration
- Enhanced file validation with magic byte checking
- XSS protection with defense-in-depth approach

### Performance Improvements
- Reduced API payload sizes by 34-47%
- Added database connection pooling
- Optimized queries with proper indexes
- Implemented caching for health checks

### API Documentation
- Complete OpenAPI 3.0 specification
- Interactive Swagger UI
- Beautiful ReDoc documentation
- All endpoints fully documented

## 📝 API Documentation

### Health Check
```bash
GET /api/health/              # Check API health
GET /api/version/             # Alias for health check
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-10-13T03:19:14.542512+00:00",
  "database": "connected",
  "api_endpoints": {
    "locations": 837,
    "candidates": 20
  }
}
```

### Candidate API
```bash
GET /candidates/api/cards/              # English candidates (paginated)
GET /ne/candidates/api/cards/           # Nepali candidates
GET /candidates/api/cards/?page=2       # Page 2
GET /candidates/api/cards/?page_size=20 # Custom page size
```

### Location API
```bash
GET /api/districts/?province={id}                    # Districts by province
GET /api/municipalities/?district={id}               # Municipalities by district
GET /api/statistics/                                 # Location statistics
GET /api/georesolve/?lat={lat}&lng={lng}            # GPS to location
```

### Ballot API
```bash
GET /candidates/api/my-ballot/?province_id={id}&district_id={id}&municipality_id={id}&ward_number={num}
```

### Authentication
- **Session Authentication**: For web interface
- **API Key Authentication**: For API access (header: `X-API-Key: your-api-key`)

For complete API documentation, visit `/api/docs/` after starting the server.

## 🧪 Testing

### Run All Tests
```bash
python manage.py test
```

### Run Specific App Tests
```bash
python manage.py test candidates
python manage.py test locations
python manage.py test authentication
```

### Check for Issues
```bash
python manage.py check
python manage.py check --deploy  # Production readiness check
```

### Code Quality
```bash
# Check for deprecation warnings
python -W all manage.py check

# Verify no issues
python manage.py check
```

## 🔧 Management Commands

### Translation Management
```bash
# Ensure all content is translated
python manage.py ensure_all_translations

# Translate existing candidates
python manage.py translate_candidates

# Compile translation files
python manage.py compilemessages
```

### Data Management
```bash
# Load Nepal location data
python manage.py load_nepal_locations --file data/nepal_locations.json

# Load demo candidates for testing
python manage.py load_demo_candidates

# Create test candidate profiles
python manage.py create_test_profiles --count 10
```

### API Management
```bash
# Create API key
python manage.py create_api_key "App Name" --email user@example.com

# List API keys
python manage.py shell
>>> from api_auth.models import APIKey
>>> APIKey.objects.all()
```

### Image Optimization
```bash
# Optimize existing candidate photos
python manage.py optimize_existing_images
```

## 📈 Performance

- **Translation Caching**: Reduces repeated API calls
- **Database Indexes**: GIN indexes for full-text search, B-tree for foreign keys
- **Connection Pooling**: CONN_MAX_AGE for persistent connections
- **Pagination**: 12-20 items per page (configurable)
- **Query Optimization**: select_related/prefetch_related to prevent N+1 queries
- **API Response Time**: ~10-50ms (with caching)

## 🔒 Security

### Implemented Protections
- ✅ **CSRF Protection**: All forms protected
- ✅ **XSS Protection**: Input sanitization + secure headers
- ✅ **SQL Injection**: Django ORM with parameterized queries
- ✅ **Rate Limiting**: 3 registrations/hour per user, 5/hour per IP
- ✅ **Input Sanitization**: bleach library for HTML cleaning
- ✅ **File Validation**: Magic byte checking + size limits
- ✅ **Secure Sessions**: HTTP-only cookies, CSRF tokens
- ✅ **Password Security**: Django's password hashing (PBKDF2)

### Production Security Checklist
- [ ] Set `DEBUG=False`
- [ ] Change `SECRET_KEY` to production value
- [ ] Configure `ALLOWED_HOSTS` for production domain
- [ ] Enable `SECURE_SSL_REDIRECT=True`
- [ ] Set `SESSION_COOKIE_SECURE=True`
- [ ] Set `CSRF_COOKIE_SECURE=True`
- [ ] Configure `SECURE_HSTS_SECONDS`
- [ ] Set up firewall rules
- [ ] Configure backup strategy

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

### Getting Started
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`python manage.py test`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Development Guidelines

#### Bilingual System Rules
- **ALWAYS** use `AutoTranslationMixin` for content models
- **NEVER** manually write Nepali translations
- **ALWAYS** use `{% trans %}` tags for UI text
- **NEVER** hardcode text in templates or views

#### Code Quality
- Follow PEP 8 naming conventions (snake_case for variables/functions)
- Write specific exception handlers (avoid broad `except Exception`)
- Use type hints where appropriate
- Add docstrings to functions and classes
- Run `python manage.py check` before committing

#### Security
- Always sanitize user input
- Use Django forms for validation
- Never trust client-side validation alone
- Test for XSS, CSRF, SQL injection

#### Testing
- Write tests for new features
- Maintain test coverage above 80%
- Test both English and Nepali content
- Test edge cases and error conditions

## 📚 Documentation

### Main Documentation
- **[CLAUDE.md](CLAUDE.md)** - Comprehensive technical documentation (150+ pages)
- **[README.md](README.md)** - This file (project overview and quick start)

### Feature Documentation
- **[BILINGUAL_SYSTEM_DOCUMENTATION.md](BILINGUAL_SYSTEM_DOCUMENTATION.md)** - Bilingual system architecture
- **[BALLOT_FEATURE.md](BALLOT_FEATURE.md)** - Location-based ballot system
- **[CANDIDATE_PROFILE_TEMPLATE.md](CANDIDATE_PROFILE_TEMPLATE.md)** - Standard candidate profile format
- **[CANDIDATE_REGISTRATION_FLOW_PLAN.md](CANDIDATE_REGISTRATION_FLOW_PLAN.md)** - Registration workflow

### API Documentation
- **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** - Complete API reference
- **[API_QUICK_REFERENCE.md](API_QUICK_REFERENCE.md)** - Quick API guide
- **[API_KEY_AUTHENTICATION.md](API_KEY_AUTHENTICATION.md)** - API key setup and usage

### Code Audit Reports
- **[CODE_AUDIT_REPORT.md](CODE_AUDIT_REPORT.md)** - Comprehensive code audit (October 2025)
- **[BILINGUAL_AUDIT_REPORT.md](BILINGUAL_AUDIT_REPORT.md)** - Bilingual system audit
- **[PROJECT_STATUS_REPORT.md](PROJECT_STATUS_REPORT.md)** - Current project status

### Issue Resolution Summaries
- **[ISSUE_42_SUMMARY.md](ISSUE_42_SUMMARY.md)** - Input sanitization implementation
- **[ISSUE_43_SUMMARY.md](ISSUE_43_SUMMARY.md)** - API payload optimization
- **[ISSUE_44_SUMMARY.md](ISSUE_44_SUMMARY.md)** - Health check endpoint
- **[ISSUE_45_SUMMARY.md](ISSUE_45_SUMMARY.md)** - Comment correction
- **[ISSUE_46_SUMMARY.md](ISSUE_46_SUMMARY.md)** - Naming convention verification
- **[ISSUE_48_SUMMARY.md](ISSUE_48_SUMMARY.md)** - Deprecated import fixes

## 🌟 Key Achievements

### Code Quality
- ✅ Zero deprecated imports (Python 3.13+ ready)
- ✅ 100% PEP 8 naming compliance
- ✅ Comprehensive input sanitization
- ✅ Specific exception handling
- ✅ Django system checks passing with 0 errors

### Performance
- ✅ 34-47% smaller API payloads
- ✅ Optimized database queries
- ✅ Full-text search with GIN indexes
- ✅ Connection pooling configured

### Security
- ✅ Input sanitization on 34 form fields
- ✅ Rate limiting on critical endpoints
- ✅ File validation with magic bytes
- ✅ XSS protection with defense-in-depth

### Documentation
- ✅ Complete OpenAPI 3.0 specification
- ✅ 150+ pages of technical documentation
- ✅ Issue resolution summaries
- ✅ API quick reference guides

## 👥 Team

- **Developer Contact**: chandmanisha002@gmail.com
- **Project Status**: Production Ready
- **Last Updated**: October 13, 2025

## 📄 License

This project is proprietary software. All rights reserved.

## 🙏 Acknowledgments

- Django community for the excellent framework
- Google Translate for powering our bilingual system
- PostgreSQL for robust database capabilities
- All contributors and testers who helped improve the platform

---

## 📊 Project Statistics

- **Total Lines of Code**: ~15,000+
- **Python Files**: 50+
- **Templates**: 30+
- **API Endpoints**: 15+
- **Management Commands**: 10+
- **Test Cases**: 30+
- **Documentation Pages**: 20+

---

**ElectNepal - Empowering Democracy in Nepal** 🇳🇵

*Making informed voting decisions accessible to all Nepali citizens*

**Version**: 1.0.0
**Status**: Production Ready
**Build**: Passing ✅
