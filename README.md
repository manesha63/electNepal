# ElectNepal 🇳🇵

A Django-based web application for tracking and displaying independent candidates in Nepal elections with comprehensive bilingual support (English/Nepali).

## 🌟 Features

- **Bilingual Support**: Complete English/Nepali translation system
- **Auto-Translation**: Automatic content translation using machine learning
- **Candidate Management**: Comprehensive profiles with verification system
- **Location-Based Filtering**: Search by Province, District, Municipality, Ward
- **Responsive Design**: Mobile-friendly interface with Tailwind CSS
- **PostgreSQL Database**: Robust data management with 753 municipalities
- **Admin Dashboard**: Enhanced Django admin for content management

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

## 📊 Project Status

**Current Phase**: Development (75% Complete)

### ✅ Completed
- Core Django infrastructure
- PostgreSQL database migration
- Complete Nepal administrative data (7 provinces, 77 districts, 753 municipalities)
- Bilingual system implementation
- Candidate management system
- API endpoints for location filtering
- Responsive UI with Tailwind CSS

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