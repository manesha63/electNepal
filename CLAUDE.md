# ElectNepal - Project Documentation

## Project Overview
A Django-based web application for tracking and displaying independent candidates in Nepal elections. Built with Django 4.2.7, migrated to PostgreSQL database, with bilingual support (English/Nepali) for democratic participation in Nepal.

## Current Project Status (as of 2025-01-14)

### ✅ Completed Features

#### 1. **Core Infrastructure**
   - **Django Project**: `nepal_election_app` with split settings architecture
   - **Database**: Successfully migrated from SQLite to PostgreSQL
     - Database: `electnepal`
     - User: `electnepal_user`
     - All data preserved during migration
   - **Three main apps**: 
     - `core` - Main pages and utilities
     - `locations` - Nepal administrative hierarchy
     - `candidates` - Candidate management system
   - **Security**: Enhanced security headers, CSRF protection, XSS protection

#### 2. **Database Models**
   - **Location Models** (`locations/models.py`):
     - `Province`: 7 provinces with English/Nepali names
     - `District`: 77 districts linked to provinces
     - `Municipality`: 753 municipalities with types and ward counts
   
   - **Candidate Models** (`candidates/models.py`):
     - `Candidate`: Complete profiles with verification workflow
     - `CandidatePost`: Blog posts/updates by candidates
     - `CandidateEvent`: Campaign event management
     - Includes constraints and database indexes for performance

#### 3. **Frontend Features**
   - **Professional Landing Page**:
     - Cookie consent system with localStorage
     - ElectNepal branding
     - Two main CTAs: "Explore Independent Candidates" and "How to Vote"
     - Contact email: chandmanisha002@gmail.com
     - Fully responsive design
   
   - **UI/UX Components**:
     - Tailwind CSS via CDN for styling
     - Alpine.js for interactivity
     - Language switcher (English/Nepali)
     - Inter and Noto Sans Devanagari fonts
     - Custom error pages (404, 500)

#### 4. **Data Management**
   - **Complete Nepal Administrative Data**:
     - **7 Provinces**: All loaded with correct names
     - **77 Districts**: Complete distribution across provinces
     - **753 Municipalities**: 100% loaded (was missing Baudikali, now fixed)
       - 6 Metropolitan Cities
       - 11 Sub-Metropolitan Cities
       - 276 Municipalities
       - 460 Rural Municipalities
     - **6,743 Total Wards**: Represented in municipality model
   
   - **Data Loading Tools**:
     - Custom management command: `load_nepal_locations`
     - Demo candidate loader: `load_demo_candidates`
     - Complete municipality loader scripts

#### 5. **Admin Interface**
   - Enhanced Django admin with:
     - Color-coded verification badges (pending=orange, verified=green, rejected=red)
     - List filters for all models
     - Search functionality
     - Bulk actions for verification
     - Inline editing for related models
   - Superuser: username=`admin`, password=`adminpass`

#### 6. **API Endpoints**
   - `GET /api/districts/?province={id}` - Districts by province
   - `GET /api/municipalities/?district={id}` - Municipalities by district
   - Returns JSON with id, name_en, name_ne fields

#### 7. **Forms and Validation**
   - `CandidateRegistrationForm` - Complete validation
   - `CandidateUpdateForm` - Profile updates
   - `CandidatePostForm` - Blog post creation
   - `CandidateEventForm` - Event management
   - Nepal phone number validation (+977 format)

#### 8. **Testing**
   - Comprehensive test suite with 14 tests
   - All tests passing after fixes
   - Coverage for models, views, and forms

## Technical Stack

### Backend
- **Framework**: Django 4.2.7
- **Database**: PostgreSQL 16
- **Python**: 3.12.3
- **Virtual Environment**: `.venv` in project root
- **Server**: Django development server (Gunicorn ready for production)

### Frontend
- **CSS Framework**: Tailwind CSS (via CDN)
- **JavaScript**: Alpine.js (via CDN)
- **Fonts**: Inter, Noto Sans Devanagari (Google Fonts)
- **Icons**: Font Awesome 6

### Key Dependencies
```
Django==4.2.7
psycopg2-binary==2.9.9
pillow==10.1.0
python-decouple==3.8
dj-database-url==2.1.0
gunicorn==21.2.0
redis==5.0.1
```

## Current Project Structure
```
~/electNepal/
├── .venv/                    # Python virtual environment
├── .env                      # Environment variables (PostgreSQL config)
├── .gitignore               # Git ignore configuration
├── manage.py                # Django management script
├── requirements.txt         # Python dependencies
├── CLAUDE.md               # This documentation file
│
├── nepal_election_app/     # Main Django project
│   ├── __init__.py
│   ├── urls.py            # Main URL configuration with i18n
│   ├── wsgi.py            # WSGI configuration
│   ├── asgi.py            # ASGI configuration
│   └── settings/          # Split settings architecture
│       ├── __init__.py    # Auto-imports from local.py
│       ├── base.py        # Base settings (shared)
│       ├── local.py       # Development settings (PostgreSQL)
│       ├── cache.py       # Cache configuration
│       ├── email.py       # Email settings
│       ├── logging.py     # Logging configuration
│       ├── postgresql.py  # PostgreSQL specific settings
│       └── security.py    # Security headers and middleware
│
├── core/                   # Core application
│   ├── models.py          # Core models (minimal)
│   ├── views.py           # HomeView, AboutView, HowToVoteView
│   ├── urls.py            # Core URL patterns
│   ├── admin.py           # Admin registration
│   ├── apps.py            # App configuration
│   ├── tests.py           # Core tests
│   └── templates/core/    
│       ├── home.html      # Landing page with cookie consent
│       ├── about.html     # About page (needs content)
│       └── how_to_vote.html # Voting guide (needs content)
│
├── locations/              # Locations management
│   ├── models.py          # Province, District, Municipality models
│   ├── views.py           # API views for location filtering
│   ├── urls.py            # API endpoint configuration
│   ├── admin.py           # Enhanced admin with filters
│   ├── apps.py            # App configuration
│   ├── tests.py           # Location tests
│   ├── migrations/        # Database migrations
│   └── management/
│       └── commands/
│           └── load_nepal_locations.py  # Data loader command
│
├── candidates/             # Candidate management
│   ├── models.py          # Candidate, Post, Event models
│   ├── views.py           # List and detail views
│   ├── urls.py            # Candidate URL patterns
│   ├── admin.py           # Enhanced admin with badges
│   ├── apps.py            # App configuration
│   ├── forms.py           # Registration and update forms
│   ├── tests.py           # Comprehensive test suite
│   ├── migrations/        # Including constraint migration
│   ├── management/
│   │   └── commands/
│   │       └── load_demo_candidates.py  # Demo data loader
│   └── templates/candidates/
│       ├── list.html      # Candidate listing (needs enhancement)
│       └── detail.html    # Candidate profile (needs enhancement)
│
├── templates/              # Global templates
│   ├── base.html          # Base template with nav, footer, cookie consent
│   ├── 404.html           # Custom 404 error page
│   └── 500.html           # Custom 500 error page
│
├── static/                 # Static assets
│   ├── css/               # Custom CSS files
│   ├── js/                # JavaScript files
│   │   └── main.js        # Cookie consent logic
│   └── images/            # Image assets
│
├── media/                  # User uploaded files (empty)
├── locale/                 # i18n translation files (to be populated)
├── data/                   # Data files
│   ├── nepal_locations.json           # Initial location data
│   ├── complete_nepal_data.json       # Complete municipality data
│   └── nepal_data_with_municipalities.json  # Full hierarchy
│
├── old_scripts_backup/     # Archived data loading scripts
│   ├── check_db_status.py
│   ├── diagnose_missing_municipalities.py
│   ├── final_complete_loader.py
│   ├── generate_complete_data.py
│   ├── load_753_municipalities.py
│   ├── load_all_municipalities.py
│   ├── load_complete_municipalities.py
│   ├── parse_nepal_data.py
│   └── verify_complete_data.py
│
└── scripts/                # Utility scripts (currently empty)
```

## Environment Configuration

### Current .env file
```
SECRET_KEY=django-insecure-w0^8@k#s$9p&2z!5m3r7n@v4x1c6y*u+q%jhbgfa=_de!@#$%
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# PostgreSQL Configuration
DATABASE_URL=postgresql://electnepal_user:electnepal123@localhost:5432/electnepal
DB_NAME=electnepal
DB_USER=electnepal_user
DB_PASSWORD=electnepal123
DB_HOST=localhost
DB_PORT=5432
```

## Database Schema Details

### Locations App
- **Province** (7 records)
  - code: CharField(10, unique)
  - name_en: CharField(100)
  - name_ne: CharField(100)

- **District** (77 records)
  - province: ForeignKey(Province)
  - code: CharField(10, unique)
  - name_en: CharField(100)
  - name_ne: CharField(100)

- **Municipality** (753 records)
  - district: ForeignKey(District)
  - code: CharField(20, unique)
  - name_en: CharField(100)
  - name_ne: CharField(100)
  - municipality_type: CharField(choices)
  - total_wards: IntegerField(default=1)

### Candidates App
- **Candidate**
  - User info: user, full_name, photo, date_of_birth, phone_number
  - Content: bio_en/ne, education_en/ne, experience_en/ne, manifesto_en/ne
  - Position: position_level, province, district, municipality, ward_number
  - Verification: status, document, notes, verified_at, verified_by
  - Social: website, facebook_url, donation_link
  - Timestamps: created_at, updated_at
  - Constraints: unique user, valid phone, positive ward number

- **CandidatePost**
  - candidate: ForeignKey
  - title_en/ne, content_en/ne
  - is_published, published_at
  - created_at, updated_at

- **CandidateEvent**
  - candidate: ForeignKey
  - title_en/ne, description_en/ne
  - event_date, location_en/ne
  - created_at, updated_at

## Comparison with Original Development Plan

### ✅ Achieved Goals
1. **Core Structure**: Django project with 3 apps as planned
2. **Database**: Successfully migrated to PostgreSQL (ahead of plan)
3. **Complete Location Data**: All 753 municipalities loaded (100%)
4. **Admin Interface**: Enhanced with verification workflow
5. **API Endpoints**: Location filtering APIs functional
6. **i18n Support**: Framework in place for English/Nepali
7. **Responsive Design**: Tailwind CSS implementation
8. **Cookie Consent**: GDPR-compliant implementation
9. **Security**: Headers and protection implemented
10. **Testing**: Comprehensive test suite with 100% passing

### 🔄 In Progress
1. **Candidate Registration**: Forms created, views need implementation
2. **i18n Translations**: Framework ready, translations needed
3. **Search/Filters**: Backend ready, frontend implementation needed

### ❌ Not Yet Started
1. **Candidate Dashboard**: Self-service portal for candidates
2. **Email Notifications**: System for alerts and updates
3. **Social Media Integration**: OAuth and sharing features
4. **Campaign Finance**: Reporting and tracking system
5. **Voter Registration**: Voter management system
6. **Docker Configuration**: Containerization for deployment
7. **Production Deployment**: Nginx, Gunicorn, SSL setup

## Known Issues & Technical Debt

### 🔴 Critical Issues (Fixed)
- ✅ Missing Baudikali municipality - FIXED
- ✅ SQLite to PostgreSQL migration - COMPLETED
- ✅ Weak SECRET_KEY - FIXED (but needs production key)
- ✅ Test failures - ALL FIXED

### 🟡 Important Issues
1. **Incomplete Templates**: About and HowToVote pages need content
2. **No Static File Collection**: Need to run collectstatic for production
3. **Missing Translations**: Nepali translations not implemented
4. **Limited Candidate Views**: List/detail templates are minimal
5. **No Media Upload**: Photo upload not configured

### 🟢 Minor Issues
1. **Duplicate Settings Files**: Multiple settings in backup
2. **Empty Directories**: scripts/ directory unused
3. **No Caching**: Redis installed but not configured
4. **No Logging**: Logging configuration exists but not used

## Immediate Next Steps (Priority Order)

### 1. **Complete Candidate Registration Flow** (2-3 days)
```python
# Create registration view in candidates/views.py
# Wire up form to save candidates
# Add success/error messages
# Create registration template
```

### 2. **Implement Search and Filtering** (1-2 days)
```python
# Add search to candidate list view
# Implement location-based filtering
# Add verification status filter
# Create filter UI components
```

### 3. **Add Nepali Translations** (2-3 days)
```bash
python manage.py makemessages -l ne
# Translate .po files
python manage.py compilemessages
```

### 4. **Enhance Candidate Templates** (1-2 days)
- Complete candidate profile page
- Add candidate posts display
- Show upcoming events
- Implement social sharing

### 5. **Configure Media Uploads** (1 day)
```python
# settings/base.py
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# urls.py
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### 6. **Setup Email System** (1 day)
- Configure SMTP settings
- Create email templates
- Implement verification emails
- Add contact form functionality

### 7. **Create Candidate Dashboard** (3-4 days)
- Login/logout views
- Profile editing
- Post management
- Event management
- Analytics view

## Development Commands

### Daily Development
```bash
cd ~/electNepal
source .venv/bin/activate
python manage.py runserver 0.0.0.0:8000
```

### Database Operations
```bash
# Make migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Load location data
python manage.py load_nepal_locations --file data/nepal_locations.json

# Create superuser
python manage.py createsuperuser

# Database shell
python manage.py dbshell
```

### Testing
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test candidates
python manage.py test locations

# Run with verbosity
python manage.py test --verbosity=2
```

### Production Preparation
```bash
# Collect static files
python manage.py collectstatic

# Check deployment readiness
python manage.py check --deploy

# Generate SECRET_KEY
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

## PostgreSQL Management

### Access Database
```bash
psql -U electnepal_user -d electnepal
```

### Backup Database
```bash
pg_dump -U electnepal_user -d electnepal > backup_$(date +%Y%m%d).sql
```

### Restore Database
```bash
psql -U electnepal_user -d electnepal < backup_20250114.sql
```

## Security Checklist for Production

- [ ] Change SECRET_KEY to production value
- [ ] Set DEBUG=False
- [ ] Configure ALLOWED_HOSTS properly
- [ ] Enable HTTPS/SSL
- [ ] Set secure cookie settings
- [ ] Configure CSRF properly
- [ ] Add rate limiting
- [ ] Set up firewall rules
- [ ] Regular security updates
- [ ] Implement backup strategy

## Performance Optimization Checklist

- [ ] Enable database connection pooling
- [ ] Configure Redis caching
- [ ] Add database indexes (partially done)
- [ ] Optimize queries with select_related/prefetch_related
- [ ] Implement pagination
- [ ] Compress static files
- [ ] Use CDN for static assets
- [ ] Optimize images
- [ ] Enable gzip compression
- [ ] Profile slow queries

## Deployment Roadmap

### Phase 1: Development (Current)
- ✅ Local development environment
- ✅ PostgreSQL database
- ✅ Basic features implemented
- 🔄 Testing and debugging

### Phase 2: Staging (Next)
- [ ] Setup staging server
- [ ] Configure Nginx
- [ ] Setup Gunicorn
- [ ] SSL certificates
- [ ] Domain configuration

### Phase 3: Production
- [ ] Production server setup
- [ ] Load balancing
- [ ] Monitoring (Sentry, etc.)
- [ ] Backup automation
- [ ] CI/CD pipeline

## Project Philosophy

This project aims to:
- **Democratize Information**: Provide transparent candidate information
- **Support Democracy**: Enable informed voting decisions
- **Ensure Accessibility**: Bilingual support for all Nepali citizens
- **Build Trust**: Verification system for authentic candidates
- **Promote Participation**: Easy registration for independent candidates

## Contact & Support

- **Developer Contact**: chandmanisha002@gmail.com
- **Project Repository**: [To be added]
- **Documentation**: This file (CLAUDE.md)
- **Admin Access**: http://127.0.0.1:8000/admin/ (admin/adminpass)

---

**Last Updated**: 2025-01-14
**Current Working Directory**: ~/electNepal
**Python Version**: 3.12.3
**Django Version**: 4.2.7
**Database**: PostgreSQL 16
**Status**: Development Phase - 60% Complete