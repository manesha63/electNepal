# ElectNepal Bilingual System Documentation

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Core Components](#core-components)
3. [Request-Response Flow](#request-response-flow)
4. [Code Implementation Details](#code-implementation-details)
5. [Automatic Translation System](#automatic-translation-system)
6. [Template System](#template-system)
7. [URL Routing](#url-routing)
8. [Frontend Language Switcher](#frontend-language-switcher)
9. [Missing Translation Handling](#missing-translation-handling)
10. [Database Schema](#database-schema)
11. [Configuration](#configuration)
12. [Usage Examples](#usage-examples)

## Architecture Overview

The ElectNepal bilingual system is a sophisticated multi-layered implementation that supports English and Nepali languages through several integrated components:

### High-Level Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Django i18n   │    │ Machine Trans.  │    │ Database Fields │
│   Framework     │    │    Service      │    │   (EN/NE)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Template System                              │
│   {% trans %} tags + Custom {% tdb %} + {% localized_field %}  │
└─────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│              Frontend Language Switcher                        │
│         JavaScript + URL Routing + Cookie Storage              │
└─────────────────────────────────────────────────────────────────┘
```

### Key Features
- **Dual Translation System**: Combines Django's i18n framework with automatic machine translation
- **Smart Fallback**: Never overwrites human translations with machine translations
- **Real-time Language Switching**: JavaScript-powered language switcher with URL manipulation
- **Transparent Translation Badges**: Visual indicators for machine-translated content
- **Cached Translation**: Performance-optimized with 30-day caching

## Core Components

### 1. Django i18n Framework
**Location**: `/home/manesha/electNepal/nepal_election_app/settings/base.py`

```python
# Core i18n Settings
LANGUAGE_CODE = 'en'
LANGUAGES = [
    ('en', 'English'),
    ('ne', 'नेपाली'),
]
USE_I18N = True
LOCALE_PATHS = [BASE_DIR / 'locale']

# Template Context Processor
'django.template.context_processors.i18n'

# Middleware for language detection
'django.middleware.locale.LocaleMiddleware'
```

### 2. Machine Translation Service
**Location**: `/home/manesha/electNepal/core/mt.py`

Multi-provider translation client supporting:
- **Google Cloud Translation API**
- **Azure Translator**
- **LibreTranslate** (self-hosted)
- **Dictionary fallback**

### 3. Custom Template Tags
**Location**: `/home/manesha/electNepal/core/templatetags/i18n_extras.py`

Three custom template tags for bilingual content:
- `{% tdb %}` - Template Database bilingual display
- `{% localized_field %}` - Dynamic field localization
- `{% mt_badge %}` - Machine translation indicator

## Request-Response Flow

### Complete Bilingual Request Flow

```
1. USER REQUEST
   │
   ▼
2. MIDDLEWARE PROCESSING
   ├─ LocaleMiddleware detects language from:
   │  ├─ URL prefix (/ne/ or /)
   │  ├─ Language cookie
   │  ├─ Accept-Language header
   │  └─ Default (English)
   │
   ▼
3. VIEW PROCESSING
   ├─ request.LANGUAGE_CODE set
   ├─ Django's translation activated
   ├─ Database queries execute
   │
   ▼
4. MODEL AUTO-TRANSLATION (if saving)
   ├─ Candidate.save() called
   ├─ autotranslate_missing() runs
   ├─ MTClient.translate() for empty NE fields
   ├─ is_mt_*_ne flags set to True
   │
   ▼
5. TEMPLATE RENDERING
   ├─ {% trans %} tags → Django i18n (.po files)
   ├─ {% tdb bio_en bio_ne %} → Custom bilingual display
   ├─ {% localized_field candidate "bio" %} → Auto field selection
   ├─ {% mt_badge candidate "bio" %} → Translation indicator
   │
   ▼
6. FRONTEND RENDERING
   ├─ Language switcher shows current language
   ├─ Content displays in appropriate language
   ├─ MT badges appear for machine translations
   │
   ▼
7. USER SEES BILINGUAL CONTENT
```

## Code Implementation Details

### Django Settings Configuration
**File**: `/home/manesha/electNepal/nepal_election_app/settings/base.py`

```python
# Machine Translation Configuration
MT_ENGINE = config('MT_ENGINE', default='libre')  # 'google', 'azure', 'libre', 'fallback'
LIBRE_MT_URL = config('LIBRE_MT_URL', default='http://localhost:5000/translate')
AZURE_MT_ENDPOINT = config('AZURE_MT_ENDPOINT', default='')
AZURE_MT_KEY = config('AZURE_MT_KEY', default='')
AZURE_MT_REGION = config('AZURE_MT_REGION', default='')

# Cache for translation results
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}
```

### URL Routing System
**File**: `/home/manesha/electNepal/nepal_election_app/urls.py`

```python
from django.conf.urls.i18n import i18n_patterns

# Non-internationalized URLs (APIs, admin)
urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    path('api/', include('locations.urls', namespace='locations_api')),
    path('set-language/', core_views.set_language, name='set_language'),
    path('api/nearby-candidates/', candidate_views.nearby_candidates_api),
    path('api/search-candidates/', candidate_views.search_candidates_api),
]

# Internationalized URLs with language prefix
urlpatterns += i18n_patterns(
    path('', candidate_views.CandidateListView.as_view(), name='home'),
    path('about/', core_views.HomeView.as_view(), name='about'),
    path('how-to-vote/', core_views.HowToVoteView.as_view(), name='how_to_vote'),
    path('candidates/', include('candidates.urls')),
    prefix_default_language=False  # No /en/ prefix for default language
)
```

### Machine Translation Client
**File**: `/home/manesha/electNepal/core/mt.py`

```python
class MTClient:
    def translate(self, text, src="en", tgt="ne"):
        # Cache key generation
        cache_key = f"mt:{self.engine}:{src}:{tgt}:{hashlib.md5(text.encode()).hexdigest()}"

        # Cache check
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            return cached_result

        # Provider-specific translation
        if self.engine == "google" and self.client:
            result = self.client.translate(text, source_language=src, target_language=tgt)
            translated = result.get("translatedText", text)
        elif self.engine == "libre" and self.requests:
            response = self.requests.post(url, data={"q": text, "source": src, "target": tgt})
            translated = response.json().get("translatedText", text)
        else:
            # Fallback to dictionary translation
            translated = self._dictionary_translate(text)

        # Cache for 30 days
        cache.set(cache_key, translated, 60 * 60 * 24 * 30)
        return translated
```

### Custom Template Tags
**File**: `/home/manesha/electNepal/core/templatetags/i18n_extras.py`

```python
@register.simple_tag(takes_context=True)
def tdb(context, en_text, ne_text):
    """Template tag for bilingual database content"""
    request = context.get('request')
    lang = getattr(request, 'LANGUAGE_CODE', get_language())

    if lang == 'ne':
        return ne_text if ne_text else en_text  # Prefer Nepali, fallback to English
    else:
        return en_text if en_text else ne_text  # Prefer English, fallback to Nepali

@register.simple_tag
def localized_field(obj, field_name):
    """Get localized field from an object"""
    lang = get_language()

    if lang == 'ne':
        ne_value = getattr(obj, f"{field_name}_ne", None)
        en_value = getattr(obj, f"{field_name}_en", None)
        return ne_value if ne_value else en_value
    else:
        en_value = getattr(obj, f"{field_name}_en", None)
        ne_value = getattr(obj, f"{field_name}_ne", None)
        return en_value if en_value else ne_value

@register.inclusion_tag('core/mt_badge.html')
def mt_badge(obj, field_name):
    """Display badge if content is machine translated"""
    lang = get_language()
    if lang == 'ne':
        is_machine_translated = getattr(obj, f"is_mt_{field_name}_ne", False)
        return {'is_mt': is_machine_translated, 'field_name': field_name}
    return {'is_mt': False}
```

## Automatic Translation System

### Model-Level Auto-Translation
**File**: `/home/manesha/electNepal/candidates/models.py`

The `Candidate` model implements automatic translation that:
1. **Never overwrites existing content**
2. **Only translates from English to Nepali**
3. **Marks machine translations with flags**
4. **Runs automatically on save**

```python
class Candidate(models.Model):
    # Bilingual fields with MT flags
    bio_en = models.TextField(help_text="Biography in English")
    bio_ne = models.TextField(blank=True, help_text="Biography in Nepali (optional)")
    is_mt_bio_ne = models.BooleanField(default=False, help_text="True if bio_ne is machine translated")

    def _fill_missing_pair(self, en_field, ne_field, mt_flag_field):
        """Auto-translate from English to Nepali if Nepali is empty"""
        en_value = getattr(self, en_field, "") or ""
        ne_value = getattr(self, ne_field, "") or ""

        # Only translate if English exists and Nepali is empty
        if en_value and not ne_value:
            from core.mt import mt
            translated = mt.translate(en_value, "en", "ne")
            setattr(self, ne_field, translated)
            setattr(self, mt_flag_field, True)

    def autotranslate_missing(self):
        """Auto-translate all empty Nepali fields from English"""
        self._fill_missing_pair("bio_en", "bio_ne", "is_mt_bio_ne")
        self._fill_missing_pair("education_en", "education_ne", "is_mt_education_ne")
        self._fill_missing_pair("experience_en", "experience_ne", "is_mt_experience_ne")
        self._fill_missing_pair("manifesto_en", "manifesto_ne", "is_mt_manifesto_ne")

    def save(self, *args, **kwargs):
        # Auto-translate missing Nepali fields (never overwrites existing)
        self.autotranslate_missing()
        super().save(*args, **kwargs)
```

### Translation Protection Logic

```python
# Safe Translation Algorithm
if english_content_exists AND nepali_content_is_empty:
    nepali_content = machine_translate(english_content)
    is_machine_translated_flag = True
else:
    # Do nothing - preserve existing human translations
    pass
```

## Template System

### Base Template Language Detection
**File**: `/home/manesha/electNepal/templates/base.html`

```html
{% load i18n static %}
<!doctype html>
<html lang="{{ request.LANGUAGE_CODE|default:'en' }}">
<head>
    <title>{% block title %}ElectNepal - {% trans "Independent Candidates Platform" %}{% endblock %}</title>
    <!-- Nepali font support -->
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Devanagari:wght@400;500;600;700&display=swap" rel="stylesheet">
</head>
<body class="{% if request.LANGUAGE_CODE == 'ne' %}ne{% endif %}">
    <!-- Language-specific CSS class applied to body -->

    <!-- Navigation with internationalized links -->
    <nav class="navbar">
        <a href="{% url 'home' %}">{% trans "Independent Candidates" %}</a>
        <a href="{% url 'how_to_vote' %}">{% trans "How to Vote" %}</a>
        <a href="{% url 'about' %}">{% trans "About Us" %}</a>
    </nav>

    <!-- Language Switcher -->
    <div class="language-switcher">
        <button onclick="toggleLanguage()">
            <i class="fas fa-globe"></i>
            <span id="currentLang">EN</span>
        </button>
        <div class="lang-dropdown" id="langDropdown">
            <a href="#" onclick="setLanguage('en')">🇬🇧 English</a>
            <a href="#" onclick="setLanguage('ne')">🇳🇵 नेपाली</a>
        </div>
    </div>
</body>
</html>
```

### Bilingual Content Display Patterns

```html
<!-- Method 1: Using custom {% tdb %} tag -->
{% load i18n_extras %}
<h2>{% tdb candidate.bio_en candidate.bio_ne %}</h2>
{% mt_badge candidate "bio" %}

<!-- Method 2: Using {% localized_field %} tag -->
<p>{% localized_field candidate "education" %}</p>
{% mt_badge candidate "education" %}

<!-- Method 3: Django's standard {% trans %} for static text -->
<button>{% trans "View Profile" %}</button>

<!-- Method 4: Manual language detection -->
{% if request.LANGUAGE_CODE == 'ne' %}
    {{ candidate.bio_ne|default:candidate.bio_en }}
{% else %}
    {{ candidate.bio_en|default:candidate.bio_ne }}
{% endif %}
```

### Machine Translation Badge
**File**: `/home/manesha/electNepal/core/templates/core/mt_badge.html`

```html
{% load i18n %}
{% if is_mt %}
<span class="mt-badge" title="{% trans 'This content was automatically translated. Please review for accuracy.' %}">
    <i class="fas fa-language"></i>
    <small>{% trans "Auto-translated" %}</small>
</span>
<style>
    .mt-badge {
        display: inline-block;
        background: #ffa500;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        margin-left: 8px;
        vertical-align: middle;
    }
</style>
{% endif %}
```

## URL Routing

### Language-Aware URL Structure

```
English (Default):
https://electnepal.com/                    → Home
https://electnepal.com/candidates/         → Candidate List
https://electnepal.com/candidates/123/     → Candidate Detail

Nepali:
https://electnepal.com/ne/                 → Home (Nepali)
https://electnepal.com/ne/candidates/      → Candidate List (Nepali)
https://electnepal.com/ne/candidates/123/  → Candidate Detail (Nepali)

APIs (No language prefix):
https://electnepal.com/api/districts/      → Always English
https://electnepal.com/admin/              → Always English
```

### Language Detection Priority

1. **URL prefix** (`/ne/` vs `/` or `/en/`)
2. **Language cookie** (`django_language`)
3. **Accept-Language header**
4. **Default language** (English)

### Custom Language Switcher View
**File**: `/home/manesha/electNepal/core/views.py`

```python
def set_language(request):
    """Custom language switching with cookie persistence"""
    next_url = request.GET.get('next', request.META.get('HTTP_REFERER', '/'))
    language = request.GET.get('language', 'en')

    # Validate language
    if language not in [lang[0] for lang in settings.LANGUAGES]:
        language = settings.LANGUAGE_CODE

    # Activate language
    translation.activate(language)

    # Create response with cookie
    response = HttpResponseRedirect(next_url)
    response.set_cookie(
        settings.LANGUAGE_COOKIE_NAME,
        language,
        max_age=365 * 24 * 60 * 60,  # 1 year
        path='/',
        httponly=True,
        samesite='Lax'
    )

    return response
```

## Frontend Language Switcher

### JavaScript Implementation
**File**: `/home/manesha/electNepal/static/js/main.js`

```javascript
// Language Switcher Functions
function toggleLanguage() {
    const dropdown = document.getElementById('langDropdown');
    dropdown.classList.toggle('active');
}

function setLanguage(lang) {
    const currentLang = document.getElementById('currentLang');
    const dropdown = document.getElementById('langDropdown');

    // Update display
    if (lang === 'en') {
        currentLang.textContent = 'EN';
        document.body.classList.remove('ne');
    } else if (lang === 'ne') {
        currentLang.textContent = 'NE';
        document.body.classList.add('ne');
    }

    // Close dropdown
    dropdown.classList.remove('active');

    // Save preference
    localStorage.setItem('electnepal_language', lang);

    // Handle URL manipulation
    let currentPath = window.location.pathname;

    // Remove existing language prefix
    currentPath = currentPath.replace(/^\/ne\//, '/').replace(/^\/en\//, '/');

    // Add new language prefix for Nepali
    if (lang === 'ne') {
        window.location.href = '/ne' + currentPath;
    } else {
        window.location.href = currentPath;
    }
}

// Initialize language from URL on page load
document.addEventListener('DOMContentLoaded', function() {
    const currentPath = window.location.pathname;
    const isNepali = currentPath.startsWith('/ne/');
    const currentLang = document.getElementById('currentLang');

    if (currentLang) {
        if (isNepali) {
            currentLang.textContent = 'NE';
            document.body.classList.add('ne');
            localStorage.setItem('electnepal_language', 'ne');
        } else {
            currentLang.textContent = 'EN';
            document.body.classList.remove('ne');
            localStorage.setItem('electnepal_language', 'en');
        }
    }
});
```

### CSS Language-Specific Styling

```css
/* Default (English) styles */
body {
    font-family: 'Inter', sans-serif;
}

/* Nepali-specific styles */
body.ne {
    font-family: 'Noto Sans Devanagari', 'Inter', sans-serif;
    direction: ltr; /* Nepali uses LTR, not RTL */
}

/* Language switcher styles */
.language-switcher {
    position: relative;
    display: inline-block;
}

.lang-dropdown {
    display: none;
    position: absolute;
    background: white;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    border-radius: 4px;
    min-width: 120px;
    z-index: 1000;
}

.lang-dropdown.active {
    display: block;
}
```

## Missing Translation Handling

### Graceful Fallback Strategy

The system implements a comprehensive fallback strategy:

```python
# Template Tag Fallback Logic
def tdb(context, en_text, ne_text):
    lang = get_language()

    if lang == 'ne':
        # For Nepali: prefer Nepali, fallback to English
        return ne_text if ne_text else en_text
    else:
        # For English: prefer English, fallback to Nepali
        return en_text if en_text else ne_text
```

### Translation File Fallbacks
**File**: `/home/manesha/electNepal/locale/ne/LC_MESSAGES/django.po`

```po
# Translated strings
msgid "Independent Candidates"
msgstr "स्वतन्त्र उम्मेदवारहरू"

msgid "View Profile"
msgstr "प्रोफाइल हेर्नुहोस्"

# Untranslated strings (fallback to English)
msgid "Enable Location Services"
msgstr ""  # Empty - will show English
```

### Database Content Fallbacks

```python
# Model field fallback in templates
{% tdb candidate.bio_en candidate.bio_ne %}

# If user selects Nepali but bio_ne is empty:
# → Shows bio_en (English content)
# → No broken display

# If user selects English but bio_en is empty:
# → Shows bio_ne (Nepali content)
# → Maintains content availability
```

## Database Schema

### Bilingual Field Pattern

Every text field that requires translation follows this pattern:

```python
class Candidate(models.Model):
    # English field (required)
    bio_en = models.TextField(help_text="Biography in English")

    # Nepali field (optional)
    bio_ne = models.TextField(blank=True, help_text="Biography in Nepali (optional)")

    # Machine translation flag
    is_mt_bio_ne = models.BooleanField(default=False, help_text="True if bio_ne is machine translated")
```

### Complete Bilingual Fields in Candidate Model

```sql
-- Core candidate information
full_name VARCHAR(200) NOT NULL,

-- Bilingual content fields
bio_en TEXT NOT NULL,
bio_ne TEXT,
is_mt_bio_ne BOOLEAN DEFAULT FALSE,

education_en TEXT,
education_ne TEXT,
is_mt_education_ne BOOLEAN DEFAULT FALSE,

experience_en TEXT,
experience_ne TEXT,
is_mt_experience_ne BOOLEAN DEFAULT FALSE,

manifesto_en TEXT,
manifesto_ne TEXT,
is_mt_manifesto_ne BOOLEAN DEFAULT FALSE,

-- Location fields (use models with bilingual names)
province_id INTEGER REFERENCES locations_province(id),
district_id INTEGER REFERENCES locations_district(id),
municipality_id INTEGER REFERENCES locations_municipality(id),
```

### Location Models Schema

```python
class Province(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name_en = models.CharField(max_length=100)  # "Province 1"
    name_ne = models.CharField(max_length=100)  # "प्रदेश १"

class District(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name_en = models.CharField(max_length=100)  # "Kathmandu"
    name_ne = models.CharField(max_length=100)  # "काठमाडौं"
    province = models.ForeignKey(Province)

class Municipality(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name_en = models.CharField(max_length=100)  # "Kathmandu Metropolitan City"
    name_ne = models.CharField(max_length=100)  # "काठमाडौं महानगरपालिका"
    district = models.ForeignKey(District)
    municipality_type = models.CharField(max_length=50)
    total_wards = models.IntegerField(default=1)
```

## Configuration

### Environment Variables

```bash
# .env file
# Machine Translation Service Configuration
MT_ENGINE=libre                                    # 'google', 'azure', 'libre', 'fallback'
LIBRE_MT_URL=http://localhost:5000/translate      # LibreTranslate URL
AZURE_MT_ENDPOINT=                                # Azure Translator endpoint
AZURE_MT_KEY=                                     # Azure API key
AZURE_MT_REGION=                                  # Azure region

# Django i18n Configuration
LANGUAGE_CODE=en
USE_I18N=True
```

### Django Settings Integration

```python
# settings/base.py
import os
from decouple import config

# Core i18n settings
LANGUAGE_CODE = 'en'
LANGUAGES = [
    ('en', 'English'),
    ('ne', 'नेपाली'),
]
TIME_ZONE = 'Asia/Kathmandu'
USE_I18N = True
USE_TZ = True
LOCALE_PATHS = [BASE_DIR / 'locale']

# Machine Translation Settings
MT_ENGINE = config('MT_ENGINE', default='libre')
LIBRE_MT_URL = config('LIBRE_MT_URL', default='http://localhost:5000/translate')
AZURE_MT_ENDPOINT = config('AZURE_MT_ENDPOINT', default='')
AZURE_MT_KEY = config('AZURE_MT_KEY', default='')
AZURE_MT_REGION = config('AZURE_MT_REGION', default='')

# Template context processors
TEMPLATES = [{
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.i18n',  # Required for i18n
            # ... other processors
        ],
    },
}]

# Middleware order (important!)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',      # Language detection
    'django.middleware.common.CommonMiddleware',
    # ... other middleware
]
```

## Usage Examples

### Creating Bilingual Content

```python
# Creating a candidate with bilingual content
candidate = Candidate.objects.create(
    user=user,
    full_name="John Doe",
    bio_en="I am an independent candidate committed to transparency and development.",
    # bio_ne will be auto-translated on save
    education_en="Master's in Public Administration",
    position_level='ward',
    province=province,
    district=district,
    municipality=municipality,
    ward_number=5
)

# After save:
# candidate.bio_ne = "म पारदर्शिता र विकासमा प्रतिबद्ध स्वतन्त्र उम्मेदवार हुँ।"
# candidate.is_mt_bio_ne = True
```

### Template Usage Examples

```html
<!-- Load custom template tags -->
{% load i18n i18n_extras %}

<!-- Static text translation -->
<h1>{% trans "Independent Candidates" %}</h1>

<!-- Database content with fallback -->
<h2>{% tdb candidate.bio_en candidate.bio_ne %}</h2>
{% mt_badge candidate "bio" %}

<!-- Dynamic field selection -->
<p>Education: {% localized_field candidate "education" %}</p>
{% mt_badge candidate "education" %}

<!-- Location display -->
<p>Location: {% tdb candidate.municipality.name_en candidate.municipality.name_ne %}</p>

<!-- Conditional display -->
{% if request.LANGUAGE_CODE == 'ne' %}
    <p class="nepali-notice">यो जानकारी नेपालीमा उपलब्ध छ।</p>
{% endif %}
```

### API Integration

```python
# API endpoint returning bilingual data
class CandidateAPIView(APIView):
    def get(self, request, pk):
        candidate = get_object_or_404(Candidate, pk=pk)
        lang = request.LANGUAGE_CODE

        # Return appropriate language content
        if lang == 'ne':
            bio = candidate.bio_ne or candidate.bio_en
            education = candidate.education_ne or candidate.education_en
        else:
            bio = candidate.bio_en or candidate.bio_ne
            education = candidate.education_en or candidate.education_ne

        return Response({
            'id': candidate.id,
            'name': candidate.full_name,
            'bio': bio,
            'education': education,
            'is_mt_bio': candidate.is_mt_bio_ne if lang == 'ne' else False,
            'is_mt_education': candidate.is_mt_education_ne if lang == 'ne' else False,
        })
```

### Management Commands

```bash
# Generate translation files
python manage.py makemessages -l ne

# Compile translations
python manage.py compilemessages

# Bulk translate existing candidates
python manage.py shell
>>> from candidates.models import Candidate
>>> candidates = Candidate.objects.filter(bio_ne='')
>>> for candidate in candidates:
...     candidate.autotranslate_missing()
...     candidate.save()
```

### Testing Bilingual Features

```python
from django.test import TestCase
from django.utils import translation
from candidates.models import Candidate

class BilingualTestCase(TestCase):
    def test_auto_translation(self):
        candidate = Candidate(bio_en="Hello world")
        candidate.autotranslate_missing()

        # Check that Nepali was generated
        self.assertIsNotNone(candidate.bio_ne)
        self.assertTrue(candidate.is_mt_bio_ne)

    def test_template_tag(self):
        with translation.override('ne'):
            # Test Nepali language selection
            pass

        with translation.override('en'):
            # Test English language selection
            pass
```

---

## Summary

The ElectNepal bilingual system is a comprehensive implementation that seamlessly integrates:

1. **Django's i18n framework** for static text translation
2. **Custom bilingual database fields** with automatic translation
3. **Smart template tags** for dynamic content display
4. **Machine translation service** with multiple provider support
5. **Frontend language switcher** with URL manipulation
6. **Caching system** for performance optimization
7. **Graceful fallback handling** for missing translations

The system ensures that users can browse the platform in their preferred language while maintaining data integrity and providing visual indicators for machine-translated content. The architecture is extensible and can easily accommodate additional languages or translation providers in the future.