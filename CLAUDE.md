# Nepal Election App - Project Documentation

## Project Overview
A Django-based web application for tracking and displaying independent candidates in Nepal elections. Built with Django 4.2.7, using SQLite for development with plans to migrate to PostgreSQL for production.

## Current Project Status (as of 2025-01-13)

### ✅ Completed Features
1. **Django Project Structure**
   - Project name: `nepal_election_app`
   - Three main apps: `core`, `locations`, `candidates`
   - Split settings configuration (base/local)
   - SQLite database for development

2. **Models Implemented**
   - **Location Models** (`locations/models.py`):
     - `Province`: Stores Nepal's provinces
     - `District`: Districts linked to provinces
     - `Municipality`: Municipalities with types (metropolitan, sub-metropolitan, municipality, rural)
   
   - **Candidate Models** (`candidates/models.py`):
     - `Candidate`: Complete candidate profiles with verification system
     - `CandidatePost`: Blog/update posts by candidates
     - `CandidateEvent`: Campaign events

3. **URLs and Views**
   - Main URL routing with i18n support
   - Core app views: HomeView, AboutView, HowToVoteView
   - Location API endpoints for districts and municipalities
   - Candidate list and detail views

4. **Templates**
   - Base template with Tailwind CSS CDN
   - Language switcher (English/Nepali)
   - Responsive design with Inter and Noto Sans Devanagari fonts
   - Alpine.js for interactivity

5. **Data Management**
   - Custom management command: `load_nepal_locations`
   - Sample data loaded (1 province, 1 district, 1 municipality)
   - Admin interface configured for all models

6. **Authentication**
   - Superuser created: username=`admin`, password=`adminpass`

## Technical Stack

### Backend
- **Framework**: Django 4.2.7
- **Database**: SQLite (development), PostgreSQL ready
- **Python**: 3.12.3
- **Virtual Environment**: `.venv` in project root

### Frontend
- **CSS Framework**: Tailwind CSS (via CDN)
- **JavaScript**: Alpine.js (via CDN)
- **Fonts**: Inter, Noto Sans Devanagari (Google Fonts)

### Key Dependencies (requirements.txt)
```
Django==4.2.7
psycopg2-binary
pillow
python-decouple
dj-database-url
gunicorn
redis
```

## Project Structure
```
~/electNepal/
├── .venv/                    # Python virtual environment
├── .env                      # Environment variables
├── .gitignore               # Git ignore file
├── manage.py                # Django management script
├── requirements.txt         # Python dependencies
├── db.sqlite3              # SQLite database
│
├── nepal_election_app/     # Main project directory
│   ├── __init__.py
│   ├── urls.py            # Main URL configuration
│   ├── wsgi.py
│   ├── asgi.py
│   └── settings/          # Split settings
│       ├── __init__.py    # Imports from local.py
│       ├── base.py        # Base settings
│       └── local.py       # Development settings
│
├── core/                   # Core app
│   ├── models.py          # (Currently minimal)
│   ├── views.py           # Home, About, HowToVote views
│   ├── urls.py            # Core URL patterns
│   ├── admin.py
│   └── templates/core/    # Core templates
│       ├── home.html
│       ├── about.html
│       └── how_to_vote.html
│
├── locations/              # Locations app
│   ├── models.py          # Province, District, Municipality
│   ├── views.py           # API views for locations
│   ├── urls.py            # API endpoints
│   ├── admin.py           # Admin registration
│   └── management/
│       └── commands/
│           └── load_nepal_locations.py  # Data loader
│
├── candidates/             # Candidates app
│   ├── models.py          # Candidate, CandidatePost, CandidateEvent
│   ├── views.py           # List and detail views
│   ├── urls.py            # Candidate routes
│   ├── admin.py           # Admin registration
│   └── templates/candidates/
│       ├── list.html      # Candidate list page
│       └── detail.html    # Candidate detail page
│
├── templates/              # Global templates
│   └── base.html          # Base template with Tailwind
│
├── static/                 # Static files directory (empty)
├── media/                  # Media files directory (empty)
├── locale/                 # i18n translations directory (empty)
├── data/                   # Data files
│   └── nepal_locations.json  # Sample location data
└── scripts/                # Utility scripts directory (empty)
```

## Database Schema

### Locations App
- **Province**: code, name_en, name_ne
- **District**: province (FK), code, name_en, name_ne
- **Municipality**: district (FK), code, name_en, name_ne, municipality_type, total_wards

### Candidates App
- **Candidate**: 
  - User info: user (FK), full_name, photo, date_of_birth, phone_number
  - Content: bio_en/ne, education_en/ne, experience_en/ne, manifesto_en/ne
  - Position: position_level, province, district, municipality, ward_number, constituency_code
  - Verification: verification_status, verification_document, verification_notes, verified_at, verified_by
  - Social: website, facebook_url, donation_link
  - Timestamps: created_at, updated_at

## How to Run the Project

### 1. Navigate to project directory
```bash
cd ~/electNepal
```

### 2. Activate virtual environment
```bash
source .venv/bin/activate
```

### 3. Install dependencies (if needed)
```bash
pip install -r requirements.txt
```

### 4. Run migrations (if needed)
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Load sample data (if needed)
```bash
python manage.py load_nepal_locations --file data/nepal_locations.json
```

### 6. Create superuser (if needed)
```bash
# Already created: admin/adminpass
# To create new one:
python manage.py createsuperuser
```

### 7. Run development server
```bash
python manage.py runserver 0.0.0.0:8000
```

### 8. Access the application
- Homepage: http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin/
- API Districts: http://127.0.0.1:8000/api/districts/?province=1
- API Municipalities: http://127.0.0.1:8000/api/municipalities/?district=1
- Candidates: http://127.0.0.1:8000/candidates/

## Environment Variables (.env)
```
SECRET_KEY=change-me
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

## API Endpoints

### Location APIs
- `GET /api/districts/?province={id}` - Get districts by province
- `GET /api/municipalities/?district={id}` - Get municipalities by district

Both return JSON arrays with id, name_en, name_ne fields.

## Next Steps / TODO

### Immediate Tasks
1. **Candidate Registration Form**
   - Multi-step form for candidate self-registration
   - File upload for verification documents
   - Image upload for candidate photos

2. **Enhanced Admin Interface**
   - Custom admin actions for verification workflow
   - Filters and search for candidates
   - Bulk operations

3. **Complete i18n**
   - Translate all static strings
   - Set up translation files for Nepali
   - Add language persistence in sessions

4. **Search and Filters**
   - Search candidates by name
   - Filter by province/district/municipality
   - Filter by position level
   - Filter by verification status

5. **Candidate Dashboard**
   - Edit profile
   - Manage posts and events
   - View analytics

### Future Enhancements
1. **Production Setup**
   - Switch to PostgreSQL
   - Add Docker configuration
   - Set up Nginx + Gunicorn
   - Configure static/media file serving
   - SSL/HTTPS setup

2. **Additional Features**
   - Voter registration
   - Election results tracking
   - Campaign finance reporting
   - Social media integration
   - Email notifications
   - SMS integration

3. **Performance Optimization**
   - Add caching (Redis)
   - Database query optimization
   - Static file CDN
   - Image optimization

4. **Security**
   - Two-factor authentication
   - Rate limiting
   - CAPTCHA for forms
   - Security headers
   - Regular security audits

## Testing Commands

### Run Django tests
```bash
python manage.py test
```

### Check for issues
```bash
python manage.py check
```

### Collect static files (for production)
```bash
python manage.py collectstatic
```

## Git Commands Reference

### Check status
```bash
git status
```

### Add all files
```bash
git add -A
```

### Commit changes
```bash
git commit -m "Your message"
```

### View commit history
```bash
git log --oneline
```

## Troubleshooting

### Port already in use
```bash
lsof -i :8000 | grep LISTEN | awk '{print $2}' | xargs kill -9
```

### Reset database
```bash
rm db.sqlite3
python manage.py migrate
python manage.py load_nepal_locations --file data/nepal_locations.json
```

### Clear Python cache
```bash
find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null
```

## Important Notes

1. **Virtual Environment**: Always activate `.venv` before working
2. **Settings**: Using split settings - `local.py` for development
3. **Database**: SQLite for dev, prepare for PostgreSQL in production
4. **Static Files**: Using CDN for CSS/JS in development
5. **Media Files**: Configure proper storage for production
6. **Security**: Change SECRET_KEY and disable DEBUG for production
7. **Admin Access**: Current credentials are admin/adminpass

## Project Philosophy

This project aims to:
- Provide transparent information about independent candidates
- Support democratic participation in Nepal
- Ensure accessibility in both English and Nepali
- Maintain simplicity and usability for all citizens
- Build trust through verification processes

---

**Last Updated**: 2025-01-13
**Current Working Directory**: ~/electNepal
**Python Version**: 3.12.3
**Django Version**: 4.2.7
**Database**: SQLite (Development)