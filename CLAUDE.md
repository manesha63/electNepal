# ElectNepal - Project Documentation

## Project Overview
A Django-based web application for tracking and displaying independent candidates in Nepal elections. Built with Django 4.2.7, using PostgreSQL database, with comprehensive bilingual support (English/Nepali) and automatic translation capabilities for democratic participation in Nepal.

## Quick Start

### Daily Development
```bash
cd ~/electNepal
source .venv/bin/activate
python manage.py runserver 0.0.0.0:8000
```

### Key URLs
- **Homepage**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/ (admin/adminpass)
- **API Documentation**: http://127.0.0.1:8000/api/docs/ (Swagger UI)
- **API ReDoc**: http://127.0.0.1:8000/api/redoc/
- **Nepali Version**: http://127.0.0.1:8000/ne/
- **Candidate Ballot**: http://127.0.0.1:8000/candidates/ballot/

### Critical Information
- **Admin Username**: admin
- **Admin Password**: adminpass
- **Database**: PostgreSQL (electnepal/electnepal_user/electnepal123)
- **Contact Email**: electnepal5@gmail.com
- **Python Version**: 3.12.3
- **Django Version**: 4.2.7
- **Total Candidates**: 22 (19 approved, 2 pending, 1 rejected)

## IMPORTANT: Candidate Profile Standard
**ALL candidate profiles MUST follow the template defined in CANDIDATE_PROFILE_TEMPLATE.md**

## Current Project Status (January 2025)

### Overall Completion: 95%

### ✅ Fully Complete (100%)
- **Core Infrastructure**: Django project with split settings architecture
- **Database Migration**: PostgreSQL with all data preserved
- **Location Data**: All 753 municipalities loaded
- **Bilingual System**: Complete UI and content translation
- **Authentication**: Signup, login, password reset
- **Candidate Registration**: 4-step wizard with approval workflow
- **Admin Interface**: Enhanced with color-coded verification
- **API Layer**: RESTful APIs with full documentation
- **Testing Suite**: 14 tests, all passing

### 🔄 Mostly Complete (90-95%)
- **Candidate Feed**: Pagination, search, filters (95%)
- **Location Ballot**: Geolocation-based voting (90%)
- **Responsive Design**: Mobile to desktop (95%)
- **Profile Dashboard**: Candidate management (90%)

### 🚧 Partially Complete (30-50%)
- **Email System**: Configuration needed (30%)
- **Media Uploads**: Basic functionality (40%)
- **Social Integration**: Links only (20%)

### ❌ Not Started (0%)
- **Docker Configuration**
- **CI/CD Pipeline**
- **Payment Integration**
- **Analytics System**
- **Campaign Finance Tracking**

## Complete Project Directory Structure

```
~/electNepal/
├── .venv/                    # Python virtual environment
├── .env                      # Environment variables (PostgreSQL config)
├── .env.example             # Example environment configuration
├── .gitignore               # Git ignore configuration
├── manage.py                # Django management script
├── requirements.txt         # Python dependencies
├── CLAUDE.md               # This documentation file (main reference)
├── API_DOCUMENTATION.md    # Complete API documentation
├── BALLOT_FEATURE.md       # Ballot feature documentation
├── CANDIDATE_PROFILE_TEMPLATE.md  # Mandatory candidate profile format
├── CANDIDATE_REGISTRATION_FLOW_PLAN.md  # Registration workflow docs
├── test_api_endpoints.py   # API testing script
├── api_documentation.py    # API documentation views
│
├── nepal_election_app/     # Main Django project directory
│   ├── __init__.py
│   ├── urls.py            # Main URL configuration with i18n patterns
│   ├── wsgi.py            # WSGI configuration for production
│   ├── asgi.py            # ASGI configuration
│   └── settings/          # Split settings architecture
│       ├── __init__.py    # Auto-imports from local.py
│       ├── base.py        # Base settings (shared across environments)
│       ├── local.py       # Development settings (DEBUG=True)
│       ├── production.py  # Production settings (not yet configured)
│       ├── cache.py       # Redis cache configuration
│       ├── email.py       # Email/SMTP settings
│       ├── logging.py     # Logging configuration
│       ├── postgresql.py  # PostgreSQL specific settings
│       └── security.py    # Security headers and middleware
│
├── authentication/          # Authentication app
│   ├── __init__.py
│   ├── models.py          # Uses Django's built-in User model
│   ├── views.py           # SignupView, LoginView, PasswordResetView
│   ├── urls.py            # Auth URL patterns
│   ├── admin.py           # Admin registration
│   ├── apps.py            # App configuration
│   ├── forms.py           # CandidateSignupForm with validation
│   ├── tests.py           # Authentication tests
│   ├── migrations/        # Database migrations
│   └── templates/authentication/
│       ├── login.html     # Bilingual login page
│       ├── signup.html    # Registration page
│       ├── password_reset.html  # Password reset form
│       └── registration_info.html  # Registration process info
│
├── core/                   # Core application
│   ├── __init__.py
│   ├── models.py          # Core models (minimal, mostly uses other apps)
│   ├── views.py           # HomeView, AboutView, HowToVoteView
│   ├── urls.py            # Core URL patterns
│   ├── admin.py           # Admin registration
│   ├── apps.py            # App configuration
│   ├── tests.py           # Core tests
│   └── templates/core/
│       ├── home.html      # Landing page with cookie consent
│       ├── about.html     # About ElectNepal (needs content)
│       └── how_to_vote.html # Voting guide (needs content)
│
├── locations/              # Nepal locations management
│   ├── __init__.py
│   ├── models.py          # Province, District, Municipality models
│   ├── views.py           # Legacy API views
│   ├── api_views.py       # RESTful API views with DRF
│   ├── serializers.py     # DRF serializers for API
│   ├── urls.py            # Location API endpoints
│   ├── admin.py           # Enhanced admin with filters
│   ├── apps.py            # App configuration
│   ├── tests.py           # Location tests
│   ├── migrations/        # Database migrations
│   └── management/
│       └── commands/
│           └── load_nepal_locations.py  # Data loader command
│
├── candidates/             # Candidate management system
│   ├── __init__.py
│   ├── models.py          # Candidate, CandidatePost, CandidateEvent models
│   ├── views.py           # Registration, dashboard, profile views
│   ├── api_views.py       # REST API views for candidates
│   ├── serializers.py     # DRF serializers
│   ├── urls.py            # Candidate URL patterns
│   ├── admin.py           # Enhanced admin with bilingual support
│   ├── apps.py            # App configuration
│   ├── forms.py           # Registration, update, post, event forms
│   ├── tests.py           # Comprehensive test suite
│   ├── translation.py     # Auto-translation system with Google Translate
│   ├── migrations/        # Including bilingual field migrations
│   ├── management/
│   │   └── commands/
│   │       ├── load_demo_candidates.py  # Demo data loader
│   │       ├── translate_candidates.py  # Bulk translation
│   │       └── backfill_bilingual.py   # Bilingual data backfill
│   └── templates/candidates/
│       ├── feed_simple_grid.html  # Main candidate feed
│       ├── feed_paginated.html   # Paginated feed variant
│       ├── list.html             # Candidate listing
│       ├── detail.html           # Candidate profile page
│       ├── ballot.html           # Location-based ballot
│       ├── register.html         # 4-step registration wizard
│       ├── registration_success.html  # Post-registration page
│       └── dashboard.html        # Candidate dashboard
│
├── templates/              # Global templates
│   ├── base.html          # Base template with nav, footer, language switcher
│   ├── 404.html           # Custom 404 error page
│   └── 500.html           # Custom 500 error page
│
├── static/                 # Static assets
│   ├── css/               # Custom CSS files
│   ├── js/                # JavaScript files
│   │   └── main.js        # Cookie consent, language switcher
│   └── images/            # Logo and other images
│
├── media/                  # User uploaded files
│   ├── candidate_photos/  # Profile photos
│   └── documents/         # Uploaded documents
│
├── locale/                 # Translation files
│   └── ne/
│       └── LC_MESSAGES/
│           ├── django.po  # Nepali translations (264 strings)
│           └── django.mo  # Compiled translations
│
├── data/                   # Data files
│   ├── nepal_locations.json           # Initial location data
│   ├── complete_nepal_data.json       # Complete municipality data
│   └── nepal_data_with_municipalities.json  # Full hierarchy
│
├── old_scripts_backup/     # Archived data loading scripts
│   └── [various data loading scripts]
│
└── scripts/                # Utility scripts (empty)
```

## Core Features & Components

### 1. Bilingual System (English/Nepali)
**Component**: `candidates/translation.py`, `locale/ne/`
- **Auto-Translation**: GoogleTranslate API integration
- **URL Structure**: `/` (English), `/ne/` (Nepali)
- **Coverage**: 264 UI strings + all dynamic content
- **Machine Translation Tracking**: `is_mt_*` fields
- **Political Dictionary**: 139+ specialized terms

### 2. Authentication System
**Component**: `authentication/` app
- **User Registration**: Email-based signup
- **Login System**: Username/password authentication
- **Password Reset**: Email-based recovery
- **Session Management**: Django sessions
- **CSRF Protection**: On all forms

### 3. Candidate Registration Flow
**Component**: `candidates/views.py`, `candidates/forms.py`
- **Step 1**: Basic Information (name, age, phone, email)
- **Step 2**: Location Selection (cascading dropdowns)
- **Step 3**: Content (bio, education, experience, manifesto)
- **Step 4**: Review & Submit
- **Approval Workflow**: Admin verification required
- **Auto-Translation**: All content to Nepali on save

### 4. Location-Based Ballot System
**Component**: `candidates/api_views.py`, `templates/candidates/ballot.html`
- **Geolocation**: Browser API for coordinates
- **Resolution**: GPS → Province/District/Municipality/Ward
- **Sorting**: Candidates by location relevance
- **Privacy**: No coordinate storage
- **Manual Fallback**: Dropdown selection

### 5. Candidate Feed System
**Component**: `candidates/api_views.py`, Alpine.js frontend
- **Grid Layout**: Responsive 1-4 columns
- **Pagination**: 12 candidates per page
- **Search**: Real-time filtering
- **Filters**: Location and position
- **Cards**: Photo, name, position, location, status

### 6. Admin Interface
**Component**: Django Admin customizations
- **Color Badges**: Orange (pending), Green (verified), Red (rejected)
- **Bulk Actions**: Approve/reject multiple
- **Search**: By name, location, position
- **Filters**: Status, province, district
- **Inline Editing**: Posts and events

### 7. API System
**Component**: Django REST Framework + drf-spectacular
- **Documentation**: OpenAPI 3.0 specification
- **Interactive**: Swagger UI and ReDoc
- **Endpoints**: 15+ documented APIs
- **Pagination**: Standard pagination on lists
- **Filtering**: Query parameter based

### 8. Database Models

#### Candidate Model
```python
- user (OneToOne)
- full_name
- photo
- age
- phone_number (optional)
- bio_en/bio_ne (auto-translate)
- education_en/education_ne
- experience_en/experience_ne
- manifesto_en/manifesto_ne
- position_level (7 choices)
- province/district/municipality/ward_number
- status (pending/approved/rejected)
- admin_notes
- approved_at/approved_by
- website/facebook_url/donation_link
- created_at/updated_at
```

#### Location Models
```python
Province (7 records)
- code, name_en, name_ne

District (77 records)
- province (FK), code, name_en, name_ne

Municipality (753 records)
- district (FK), code, name_en, name_ne
- municipality_type, total_wards
```

## Technical Stack Details

### Backend Dependencies
```
Django==4.2.7
djangorestframework==3.16.1
drf-spectacular==0.28.0
psycopg2-binary==2.9.9
pillow==10.1.0
python-decouple==3.8
dj-database-url==2.1.0
gunicorn==21.2.0
redis==5.0.1
googletrans==4.0.0-rc1
httpx==0.13.3
polib==1.2.0
django-ratelimit==4.1.0
```

### Frontend Stack
- **CSS**: Tailwind CSS 3.x (CDN)
- **JavaScript**: Alpine.js 3.x (CDN)
- **Fonts**: Inter, Noto Sans Devanagari
- **Icons**: Font Awesome 6

### Environment Configuration (.env)
```
SECRET_KEY=django-insecure-w0^8@k#s$9p&2z!5m3r7n@v4x1c6y*u+q%jhbgfa=_de!@#$%
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# PostgreSQL
DATABASE_URL=postgresql://electnepal_user:electnepal123@localhost:5432/electnepal
DB_NAME=electnepal
DB_USER=electnepal_user
DB_PASSWORD=electnepal123
DB_HOST=localhost
DB_PORT=5432

# AWS SES (needs configuration)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_SES_REGION=
DEFAULT_FROM_EMAIL=
```

## Development Commands

### Database Management
```bash
# Migrations
python manage.py makemigrations
python manage.py migrate

# Load data
python manage.py load_nepal_locations --file data/nepal_locations.json
python manage.py load_demo_candidates

# Database access
psql -U electnepal_user -d electnepal

# Backup
pg_dump -U electnepal_user -d electnepal > backup_$(date +%Y%m%d).sql
```

### Translation Management
```bash
# Extract strings for translation
python manage.py makemessages -l ne

# Compile translations
python manage.py compilemessages

# Auto-translate candidates
python manage.py translate_candidates

# Backfill bilingual fields
python manage.py backfill_bilingual
```

### Testing
```bash
# Run all tests
python manage.py test

# Specific app
python manage.py test candidates

# With coverage
coverage run --source='.' manage.py test
coverage report

# API testing
python test_api_endpoints.py
```

## Known Issues & Technical Debt

### 🔴 Critical (Must Fix)
1. **Email Verification**: Not implemented - users can use fake emails
2. **Translation Performance**: 10-30 second delays during registration
3. **Search Inefficiency**: No full-text search, uses ILIKE
4. **Password Reset**: Missing password_reset_confirm view

### 🟠 High Priority
1. **No Image Optimization**: 5MB photos slow page loads
2. **Missing Transactions**: Registration can partially fail
3. **No Loading States**: Users submit forms multiple times
4. **Pagination UI**: Breaks with 1000+ candidates

### 🟡 Medium Priority
1. **Redis Unused**: Configured but not implemented
2. **No Remember Me**: Sessions expire quickly
3. **Dropdowns Reset**: On validation errors
4. **No Export**: Cannot export candidate data
5. **Generic Errors**: Not user-friendly messages

## Production Deployment Checklist

### Security Requirements
- [ ] Change SECRET_KEY to production value
- [ ] Set DEBUG=False
- [ ] Configure ALLOWED_HOSTS with domain
- [ ] Enable HTTPS with SSL certificate
- [ ] Set SECURE_SSL_REDIRECT=True
- [ ] Configure CSRF_COOKIE_SECURE=True
- [ ] Set SESSION_COOKIE_SECURE=True
- [ ] Implement rate limiting
- [ ] Configure firewall rules

### Performance Optimization
- [ ] Enable Redis caching
- [ ] Configure database pooling
- [ ] Add database indexes
- [ ] Implement CDN for static files
- [ ] Enable gzip compression
- [ ] Optimize images (WebP format)
- [ ] Minify CSS/JavaScript

### Infrastructure Setup
- [ ] Configure Nginx as reverse proxy
- [ ] Setup Gunicorn workers
- [ ] Configure systemd services
- [ ] Setup log rotation
- [ ] Implement monitoring (Sentry)
- [ ] Configure automated backups
- [ ] Setup staging environment

## API Endpoints Reference

### Location APIs
- `GET /api/districts/?province={id}` - Get districts by province
- `GET /api/municipalities/?district={id}` - Get municipalities by district
- `GET /api/wards/?municipality={id}` - Get ward count
- `GET /api/statistics/` - Location statistics
- `GET /api/georesolve/?lat={}&lng={}` - GPS to location

### Candidate APIs
- `GET /candidates/api/cards/` - Paginated candidate feed
- `GET /candidates/api/my-ballot/` - Location-based ballot
- `GET /candidates/api/search/` - Search candidates
- `GET /candidates/api/{id}/` - Single candidate details

### Documentation
- `GET /api/schema/` - OpenAPI schema
- `GET /api/docs/` - Swagger UI
- `GET /api/redoc/` - ReDoc interface

## How Features Work - Technical Details

### Candidate Feed Pagination
1. Alpine.js `candidateGrid()` component initializes
2. Fetches `/candidates/api/cards/?page=1`
3. Django Paginator returns 12 candidates
4. Frontend renders responsive grid
5. "More" button loads next page
6. "Previous" appears after 3 pages

### Auto-Translation Flow
1. User submits English content
2. `AutoTranslationMixin.autotranslate_missing()` called
3. Checks each `_en` field for content
4. If `_ne` is empty, calls Google Translate API
5. Saves translation and sets `is_mt_*=True`
6. Never overwrites existing Nepali content

### Location Cascade
1. User selects Province
2. AJAX call to `/api/districts/?province={id}`
3. Populates District dropdown
4. User selects District
5. AJAX call to `/api/municipalities/?district={id}`
6. Populates Municipality dropdown
7. Ward input appears based on municipality

## Support & Documentation

- **Primary Email**: electnepal5@gmail.com
- **Documentation Files**:
  - `CLAUDE.md` - This main documentation
  - `API_DOCUMENTATION.md` - Complete API guide
  - `BALLOT_FEATURE.md` - Ballot system details
  - `CANDIDATE_PROFILE_TEMPLATE.md` - Profile standards
  - `CANDIDATE_REGISTRATION_FLOW_PLAN.md` - Registration workflow

---

**Last Updated**: January 2025
**Project Status**: 95% Complete (Development Phase)
**Working Directory**: ~/electNepal
**Next Priority**: Email verification with AWS SES, Redis cache implementation, production deployment setup