# ElectNepal - Empowering Democracy in Nepal 🇳🇵

[![Django](https://img.shields.io/badge/Django-4.2.7-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.12.3-blue.svg)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue.svg)](https://www.postgresql.org/)
[![Status](https://img.shields.io/badge/Status-90%25%20Complete-yellow.svg)]()
[![Bilingual](https://img.shields.io/badge/Bilingual-EN%2FNE-success.svg)]()

## 🎯 Project Overview

ElectNepal is a comprehensive Django-based web application for tracking and displaying independent candidates in Nepal elections. Built with a strong focus on bilingual support (English/Nepali), the platform enables democratic participation by providing transparent candidate information to all Nepali citizens.

### ✨ Key Features

- **100% Automated Bilingual System** - Write once in English, display everywhere in both languages
- **Complete Nepal Administrative Data** - All 7 provinces, 77 districts, 753 municipalities
- **Candidate Management** - Comprehensive profiles with automatic translation
- **Location-Based Ballot System** - Find candidates based on your location
- **Responsive Design** - Mobile-friendly interface with modern UI/UX
- **API-First Architecture** - RESTful APIs with language awareness

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

8. **Run the development server**
```bash
python manage.py runserver 0.0.0.0:8000
```

Access the application:
- English: http://localhost:8000/
- Nepali: http://localhost:8000/ne/
- Admin: http://localhost:8000/admin/

## 🌐 Bilingual System

### How It Works

The bilingual system is **100% automated**. Developers only write content in English, and the system automatically:
- Translates all content to Nepali using Google Translate API
- Caches translations for performance
- Displays the correct language based on user preference
- Falls back gracefully if translation fails

### Key Components

1. **BilingualModel** - Base class for all content models
2. **AutoTranslationMixin** - Automatic translation on save
3. **Template Tags** - `{% load bilingual %}` for UI translations
4. **Language-Aware APIs** - Returns data based on URL prefix

For detailed documentation, see [BILINGUAL_SYSTEM_DOCUMENTATION.md](BILINGUAL_SYSTEM_DOCUMENTATION.md)

## 📁 Project Structure

```
electNepal/
├── nepal_election_app/     # Main Django project
├── core/                   # Core application
├── locations/              # Nepal administrative data
├── candidates/             # Candidate management
├── templates/              # Global templates
├── static/                 # Static assets
├── locale/                 # Translation files
├── data/                   # Location data files
└── media/                  # User uploads
```

## 🛠️ Technical Stack

### Backend
- **Framework**: Django 4.2.7
- **Database**: PostgreSQL 16
- **Translation**: Google Translate API (googletrans)
- **Cache**: 30-day translation caching

### Frontend
- **CSS**: Tailwind CSS (via CDN)
- **JavaScript**: Alpine.js
- **Fonts**: Inter, Noto Sans Devanagari
- **Icons**: Font Awesome 6

## 📊 Current Status

### ✅ Completed (90%)

- ✅ Core infrastructure and database
- ✅ Complete location data (753 municipalities)
- ✅ Bilingual system (100% operational)
- ✅ Candidate management system
- ✅ API endpoints with language awareness
- ✅ Responsive UI/UX design
- ✅ Admin interface
- ✅ Location-based ballot system

### 🔄 In Progress (10%)

- [ ] User authentication system
- [ ] Email notifications
- [ ] Production deployment
- [ ] Docker configuration

## 📝 API Documentation

### Candidate API
```
GET /candidates/api/cards/         # English candidates
GET /ne/candidates/api/cards/      # Nepali candidates
```

### Location API
```
GET /api/districts/?province={id}
GET /api/municipalities/?district={id}
```

### Ballot API
```
GET /candidates/api/my-ballot/?province_id={}&district_id={}&municipality_id={}&ward_number={}
```

## 🧪 Testing

Run the test suite:
```bash
python manage.py test
```

Run specific app tests:
```bash
python manage.py test candidates
python manage.py test locations
```

## 🔧 Management Commands

### Translate all content
```bash
python manage.py ensure_all_translations
```

### Load demo candidates
```bash
python manage.py load_demo_candidates
```

### Validate bilingual compliance
```bash
python manage.py shell
>>> from core.bilingual_validator import run_validation
>>> run_validation()
```

## 📈 Performance

- Translation caching: 30 days per unique text
- Database indexes on foreign keys
- Optimized queries with select_related/prefetch_related
- Pagination for large datasets

## 🔒 Security

- CSRF protection enabled
- XSS protection headers
- SQL injection prevention (ORM)
- Environment variables for secrets
- Secure password hashing

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Follow existing code conventions
4. Ensure bilingual compliance (never hardcode translations)
5. Write tests for new features
6. Submit a pull request

### Development Guidelines

- **ALWAYS** inherit from `BilingualModel` for content models
- **NEVER** manually write Nepali translations
- **ALWAYS** use `{% trans %}` tags for UI text
- **NEVER** hardcode text in templates

## 📚 Documentation

- [CLAUDE.md](CLAUDE.md) - Detailed technical documentation
- [BILINGUAL_SYSTEM_DOCUMENTATION.md](BILINGUAL_SYSTEM_DOCUMENTATION.md) - Bilingual system guide
- [CANDIDATE_PROFILE_TEMPLATE.md](CANDIDATE_PROFILE_TEMPLATE.md) - Candidate profile standard
- [BALLOT_FEATURE.md](BALLOT_FEATURE.md) - Ballot system documentation

## 👥 Team

- **Developer Contact**: chandmanisha002@gmail.com
- **Project Status**: Active Development
- **Last Updated**: September 20, 2025

## 📄 License

This project is proprietary software. All rights reserved.

## 🙏 Acknowledgments

- Django community for the excellent framework
- Google Translate for powering our bilingual system
- All contributors and testers

---

**ElectNepal - Empowering Democracy in Nepal** 🇳🇵

*Making informed voting decisions accessible to all Nepali citizens*