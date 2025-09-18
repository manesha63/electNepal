# ElectNepal 🇳🇵

A Django-based web application for tracking and displaying independent candidates in Nepal elections with comprehensive bilingual support (English/Nepali).

## 🌟 Features

- **Bilingual Support**: Complete English/Nepali translation system with automatic content translation
- **WeVote-Inspired UI**: Professional grayscale design with light blue accents
- **Candidate Management**: Comprehensive profiles with standardized template format
- **Location-Based Ballot**: Geolocation-aware candidate discovery system
- **Responsive Design**: Mobile-friendly interface with Tailwind CSS
- **PostgreSQL Database**: Complete Nepal administrative data (7 provinces, 77 districts, 753 municipalities, 6,743 wards)
- **Admin Dashboard**: Enhanced Django admin for content management
- **Real-time Search**: Dynamic candidate filtering with pagination
- **Privacy-First**: No tracking, minimal cookies, secure data handling

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- PostgreSQL 16+
- Git

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/electNepal.git
cd electNepal
```

2. **Create virtual environment**
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

8. **Run development server**
```bash
python manage.py runserver
```

Visit http://127.0.0.1:8000 to see the application.

## 📁 Project Structure

```
electNepal/
├── nepal_election_app/     # Main Django project
│   ├── settings/          # Split settings (base, local, production)
│   └── urls.py           # URL configuration with i18n
├── candidates/           # Candidate management app
│   ├── models.py        # Bilingual candidate models
│   ├── views.py         # API and web views
│   ├── templates/       # Candidate templates
│   └── management/      # Custom commands
├── locations/           # Nepal administrative data
│   ├── models.py        # Province, District, Municipality
│   └── views.py         # Location API endpoints
├── core/                # Core functionality
│   └── templates/       # Home, About pages
├── static/              # Static assets
│   ├── css/            # Custom styles + colors.css
│   └── js/             # Alpine.js components
├── templates/           # Global templates
├── locale/              # Translation files
└── data/                # Location data JSONs
```

## 📊 Project Status

**Current Phase**: Development (85% Complete)
**Last Updated**: January 19, 2025

### ✅ Completed
- Core Django infrastructure with PostgreSQL
- Complete Nepal administrative data (7 provinces, 77 districts, 753 municipalities, 6,743 wards)
- Bilingual system with auto-translation
- Candidate management with standardized profiles
- Location-based ballot system with geolocation
- WeVote-inspired UI redesign
- API endpoints for filtering and search
- Responsive design with Tailwind CSS
- Verification system removal
- Professional grayscale color scheme

### 🔄 In Progress
- Candidate registration workflow
- Email notification system
- Search and filtering enhancements

### 📝 Planned
- Candidate dashboard
- Social media integration
- Campaign finance tracking
- Docker configuration
- Production deployment

## 🏗️ Tech Stack

- **Backend**: Django 4.2.7, Python 3.12
- **Database**: PostgreSQL 16
- **Frontend**: Tailwind CSS, Alpine.js
- **Translation**: Google Translate API, Django i18n
- **Deployment**: Gunicorn, Nginx (production ready)

## 🌐 Bilingual System

The application automatically translates all content between English and Nepali:

- 264+ UI strings translated
- Auto-translation for user-generated content
- Machine translation tracking
- Smart fallback system
- Never overwrites human translations

## 📁 Project Structure

```
electNepal/
├── candidates/          # Candidate management app
├── locations/          # Nepal administrative data
├── core/              # Core functionality
├── locale/            # Translation files
├── static/            # CSS, JavaScript
├── templates/         # HTML templates
├── nepal_election_app/ # Main Django project
└── data/             # Location data files
```

## 🔒 Security

- Environment variables for sensitive data
- CSRF protection enabled
- XSS protection configured
- Secure password hashing
- SQL injection prevention

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is currently private. License to be determined.

## 📧 Contact

For questions or support, contact: chandmanisha002@gmail.com

## 🙏 Acknowledgments

- Django community
- Nepal government for administrative data
- Contributors and testers

---

**Developed with ❤️ for democratic participation in Nepal**