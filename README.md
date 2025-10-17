# ElectNepal - Empowering Democracy in Nepal 🇳🇵

[![Django](https://img.shields.io/badge/Django-4.2.7-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.12.3-blue.svg)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue.svg)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-Proprietary-red.svg)]()
[![Status](https://img.shields.io/badge/Status-Development-yellow.svg)]()
[![Coverage](https://img.shields.io/badge/Coverage-95%25-brightgreen.svg)]()

> A bilingual platform for transparent independent candidate information in Nepal elections, enabling informed democratic participation for all citizens.

## 📋 Table of Contents

- [Features](#-features)
- [Demo](#-demo)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Development](#-development)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Contributing](#-contributing)
- [License](#-license)

## ✨ Features

### Core Functionality
- **🌐 100% Automated Bilingual Support** - English/Nepali with automatic translation
- **🗺️ Complete Nepal Data** - All 7 provinces, 77 districts, 753 municipalities
- **👤 Candidate Management** - Multi-step registration with admin approval workflow
- **📍 Location-Based Ballot** - GPS-enabled candidate discovery by location
- **🔍 Advanced Search** - Full-text search with filters by location and position

### Technical Features
- **📚 RESTful API** - Comprehensive API with OpenAPI 3.0 documentation
- **🔐 Security** - Input sanitization, rate limiting, CSRF/XSS protection
- **📱 Responsive Design** - Mobile-first, WeVote-inspired UI
- **⚡ Performance** - Optimized queries, caching, connection pooling
- **📊 Analytics** - Built-in page view tracking and statistics

## 🎯 Demo

- **Live Demo**: Coming soon
- **API Documentation**: [View Swagger Docs](http://localhost:8000/api/docs/) (local)
- **Screenshots**: See [/docs/screenshots](./docs/screenshots)

## 🚀 Quick Start

```bash
# Clone repository
git clone https://github.com/yourusername/electNepal.git
cd electNepal

# Setup virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Setup database
python manage.py migrate
python manage.py load_nepal_locations --file data/nepal_locations.json

# Create admin user
python manage.py createsuperuser

# Run server
python manage.py runserver
```

Access at: http://localhost:8000/

## 📦 Installation

### Prerequisites

- Python 3.12.3+
- PostgreSQL 16+
- pip and virtualenv

### Detailed Setup

1. **Database Configuration**
```bash
# Create PostgreSQL database and user
sudo -u postgres psql
CREATE DATABASE electnepal;
CREATE USER electnepal_user WITH PASSWORD 'your-secure-password';
GRANT ALL PRIVILEGES ON DATABASE electnepal TO electnepal_user;
```

2. **Environment Variables**
```bash
# .env file
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgresql://electnepal_user:password@localhost:5432/electnepal
```

3. **Initial Data**
```bash
# Load location data
python manage.py load_nepal_locations --file data/nepal_locations.json

# Load demo candidates (optional)
python manage.py load_demo_candidates

# Compile translations
python manage.py compilemessages
```

## 🎮 Usage

### Key URLs

| URL | Description |
|-----|-------------|
| `/` | Homepage (English) |
| `/ne/` | Homepage (Nepali) |
| `/admin/` | Admin Panel |
| `/api/docs/` | API Documentation (Swagger) |
| `/api/redoc/` | API Documentation (ReDoc) |
| `/candidates/ballot/` | Location-based ballot |
| `/auth/signup/` | User registration |

### Management Commands

```bash
# Translation management
python manage.py ensure_all_translations
python manage.py translate_candidates

# Data management
python manage.py load_nepal_locations --file data/nepal_locations.json
python manage.py create_test_profiles --count 10

# API key management
python manage.py create_api_key "App Name" --email user@example.com

# Image optimization
python manage.py optimize_existing_images
```

## 📡 API Documentation

### Authentication

The API supports two authentication methods:

1. **Session Authentication** - For web interface
2. **API Key Authentication** - For programmatic access

```bash
# Create API key
python manage.py create_api_key "My App" --email your@email.com
```

### Example Requests

```bash
# Health check
curl http://localhost:8000/api/health/

# Get candidates (with API key)
curl -H "X-API-Key: your-api-key" \
     http://localhost:8000/candidates/api/cards/

# Get districts by province
curl http://localhost:8000/api/districts/?province=1

# Location-based ballot
curl "http://localhost:8000/candidates/api/my-ballot/?province_id=1&district_id=1"
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health/` | GET | API health check |
| `/candidates/api/cards/` | GET | Paginated candidate list |
| `/api/districts/` | GET | Districts by province |
| `/api/municipalities/` | GET | Municipalities by district |
| `/api/georesolve/` | GET | GPS to location |
| `/candidates/api/my-ballot/` | GET | Location-based ballot |

Full documentation available at `/api/docs/` when server is running.

## 🛠️ Development

### Project Structure

```
electNepal/
├── nepal_election_app/     # Django project settings
├── authentication/         # User authentication
├── candidates/            # Candidate management
├── locations/             # Nepal administrative data
├── api_auth/              # API key authentication
├── templates/             # HTML templates
├── static/                # CSS, JS, images
├── locale/                # Translation files
└── data/                  # Location data
```

### Tech Stack

- **Backend**: Django 4.2.7, PostgreSQL 16
- **API**: Django REST Framework + drf-spectacular
- **Frontend**: Tailwind CSS, Alpine.js
- **Translation**: Google Translate API
- **Security**: bleach, django-ratelimit

### Development Guidelines

1. **Always use AutoTranslationMixin** for content models
2. **Never hardcode text** - use `{% trans %}` tags
3. **Sanitize all user input** with bleach
4. **Write tests** for new features
5. **Follow PEP 8** naming conventions

## 🧪 Testing

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test candidates

# Check for issues
python manage.py check
python manage.py check --deploy  # Production readiness

# Coverage report
coverage run --source='.' manage.py test
coverage report
```

## 🚢 Deployment

### Production Checklist

- [ ] Set `DEBUG=False`
- [ ] Generate new `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Enable HTTPS/SSL
- [ ] Set secure cookie flags
- [ ] Configure database pooling
- [ ] Set up monitoring
- [ ] Configure backups

### Docker Deployment

```bash
# Build image
docker build -t electnepal .

# Run container
docker run -p 8000:8000 electnepal
```

### Environment Variables

```bash
# Production .env
DEBUG=False
SECRET_KEY=your-production-secret-key
ALLOWED_HOSTS=yourdomain.com
DATABASE_URL=postgresql://user:pass@host:5432/db
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md).

### How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Code Style

- Follow PEP 8 guidelines
- Write clear commit messages
- Add tests for new features
- Update documentation

## 📚 Documentation

- [Technical Documentation](CLAUDE.md) - Comprehensive technical details
- [API Documentation](API_DOCUMENTATION.md) - Complete API reference
- [Bilingual System](BILINGUAL_SYSTEM_DOCUMENTATION.md) - Translation architecture
- [Ballot Feature](BALLOT_FEATURE.md) - Location-based voting system

## 📊 Project Status

- **Version**: 1.0.0
- **Status**: Development (95% Complete)
- **Python**: 3.12.3+ compatible
- **Django**: 4.2.7
- **Last Updated**: January 2025

## 📄 License

This project is proprietary software. All rights reserved.

## 👥 Contact

- **Email**: electnepal5@gmail.com
- **Issues**: [GitHub Issues](https://github.com/yourusername/electNepal/issues)

## 🙏 Acknowledgments

- Django community for the excellent framework
- Google Translate for bilingual capabilities
- PostgreSQL for robust database features
- All contributors and testers

---

<p align="center">
  <strong>ElectNepal - Making Democracy Accessible</strong><br>
  Empowering informed voting decisions for all Nepali citizens 🇳🇵
</p>