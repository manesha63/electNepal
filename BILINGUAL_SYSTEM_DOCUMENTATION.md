# ElectNepal Bilingual System Documentation

## Overview

ElectNepal implements a **100% automated bilingual system** (English/Nepali) using Django's i18n framework combined with Google Translate API for dynamic content. The system is designed to work seamlessly without manual translation effort.

## System Architecture

### Core Components

1. **AutoTranslationMixin** (`candidates/translation.py`)
   - Base class for models requiring automatic translation
   - Handles field detection and translation logic
   - Tracks machine-translated content with `is_mt_*` flags

2. **AsyncTranslator** (`candidates/async_translation.py`)
   - Manages background translation tasks
   - Uses threading for non-blocking translation
   - Handles database connections properly in threads

3. **Translation Service** (`candidates/translation.py`)
   - Google Translate API integration (googletrans 4.0.0rc1)
   - Political dictionary with 139+ specialized terms
   - Caching mechanism for performance

4. **UI Translation** (`locale/ne/LC_MESSAGES/`)
   - 264 translated UI strings
   - Compiled .mo files for runtime performance
   - Django's standard i18n framework

## Implementation Details

### 1. Model-Level Translation

```python
class AutoTranslationMixin:
    """
    Mixin that provides automatic translation for model fields.
    Fields ending with _en are automatically translated to _ne fields.
    """

    TRANSLATABLE_FIELDS = []  # Define in each model

    def autotranslate_missing(self):
        """Translates empty _ne fields from _en fields"""
        translator = TranslationService()

        for field_base in self.TRANSLATABLE_FIELDS:
            en_field = f"{field_base}_en"
            ne_field = f"{field_base}_ne"
            mt_flag = f"is_mt_{ne_field}"

            en_value = getattr(self, en_field, '')
            ne_value = getattr(self, ne_field, '')

            if en_value and not ne_value:
                # Translate only if English exists and Nepali is empty
                translated = translator.translate_to_nepali(en_value)
                setattr(self, ne_field, translated)
                setattr(self, mt_flag, True)  # Mark as machine translated
```

### 2. Asynchronous Translation

```python
class AsyncTranslator:
    """
    Handles translation in background threads to prevent blocking.
    Properly manages database connections in threads.
    """

    def translate_in_background(self, obj_class, obj_id):
        def _translate():
            # Close old database connection (required for threads)
            from django.db import connection
            connection.close()

            # Re-fetch object in thread context
            obj = obj_class.objects.get(pk=obj_id)
            obj.autotranslate_missing()
            obj.save(update_fields=[...])  # Save only translated fields

        thread = threading.Thread(target=_translate)
        thread.daemon = True
        thread.start()
```

### 3. URL-Based Language Detection

```python
# nepal_election_app/urls.py
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    path('api/', include('locations.urls')),
    path('candidates/', include('candidates.urls')),
]

urlpatterns += i18n_patterns(
    path('', views.HomeView.as_view(), name='home'),
    path('about/', views.AboutView.as_view(), name='about'),
    prefix_default_language=False  # No /en/ prefix for English
)
```

- English URLs: `/`, `/about/`, `/candidates/`
- Nepali URLs: `/ne/`, `/ne/about/`, `/ne/candidates/`

### 4. Template Translation

```django
{% load i18n %}

<!-- Automatic translation based on active language -->
<h1>{% trans "Welcome to ElectNepal" %}</h1>

<!-- Force specific language -->
{% get_current_language as LANGUAGE_CODE %}
{% if LANGUAGE_CODE == 'ne' %}
    {{ candidate.bio_ne|default:candidate.bio_en }}
{% else %}
    {{ candidate.bio_en }}
{% endif %}
```

### 5. API Language Support

```python
def get_candidate_data(self, candidate):
    """Returns data in the correct language based on request"""
    from django.utils.translation import get_language

    lang = get_language()
    if lang == 'ne':
        return {
            'name': candidate.full_name,  # Names don't translate
            'bio': candidate.bio_ne or candidate.bio_en,  # Fallback
            'education': candidate.education_ne or candidate.education_en,
        }
    return {
        'name': candidate.full_name,
        'bio': candidate.bio_en,
        'education': candidate.education_en,
    }
```

## Political Dictionary

The system includes a specialized dictionary for political and administrative terms:

```python
POLITICAL_DICTIONARY = {
    # Administrative Terms
    'province': 'प्रदेश',
    'district': 'जिल्ला',
    'municipality': 'नगरपालिका',
    'rural municipality': 'गाउँपालिका',
    'ward': 'वडा',

    # Political Positions
    'mayor': 'मेयर',
    'deputy mayor': 'उप-मेयर',
    'chairperson': 'अध्यक्ष',
    'vice chairperson': 'उपाध्यक्ष',
    'ward chairperson': 'वडा अध्यक्ष',

    # Election Terms
    'candidate': 'उम्मेदवार',
    'independent': 'स्वतन्त्र',
    'election': 'निर्वाचन',
    'vote': 'मत',
    'ballot': 'मतपत्र',

    # Total: 139+ terms
}
```

## Language Switching

### Frontend JavaScript

```javascript
function setLanguage(lang) {
    let currentPath = window.location.pathname;

    // Remove existing language prefix
    currentPath = currentPath.replace(/^\/ne\//, '/');

    // Add new language prefix for Nepali
    if (lang === 'ne') {
        window.location.href = '/ne' + currentPath;
    } else {
        window.location.href = currentPath;
    }
}
```

### Django Middleware

```python
MIDDLEWARE = [
    'django.middleware.locale.LocaleMiddleware',  # Detects language
    # ... other middleware
]

# Settings
LANGUAGE_CODE = 'en'
LANGUAGES = [
    ('en', 'English'),
    ('ne', 'नेपाली'),
]
USE_I18N = True
LOCALE_PATHS = [BASE_DIR / 'locale']
```

## Translation Workflow

### 1. When Content is Created/Updated

```
User submits English content
    ↓
Model save() method called
    ↓
AutoTranslationMixin.autotranslate_missing() runs
    ↓
Empty _ne fields detected
    ↓
TranslationService translates via Google API
    ↓
Nepali content saved with is_mt_* = True
    ↓
transaction.on_commit() triggers async translation (if needed)
```

### 2. When User Switches Language

```
User clicks language button
    ↓
JavaScript changes URL (adds/removes /ne/)
    ↓
Page reloads with new URL
    ↓
LocaleMiddleware detects language from URL
    ↓
Sets request.LANGUAGE_CODE
    ↓
Templates use correct language
    ↓
API returns correct language fields
```

## Current Status

### ✅ Working Components
- **UI Translation**: 264 strings fully translated
- **Model Translation**: Auto-translation on save
- **Language Switching**: URL-based detection
- **API Support**: Language-aware responses
- **Political Dictionary**: 139+ specialized terms
- **Async Translation**: Background processing
- **Fallback Logic**: Shows English if Nepali missing

### ⚠️ Known Issues

1. **Translation Performance**
   - Google Translate API calls take 2-5 seconds
   - Can timeout on long text (>5000 characters)
   - Solution: Async translation implemented

2. **Email Templates Not Translated**
   - 6 email templates referenced but not created
   - No Nepali versions of emails
   - Solution: Create bilingual email templates

3. **Bare Fallback**
   - Currently copies English to Nepali if translation fails
   - Should leave empty for manual translation
   - Location: `translation.py:277-279`

## Management Commands

### Ensure All Translations

```bash
python manage.py ensure_all_translations
```
- Checks all translatable models
- Translates missing Nepali content
- Reports statistics

### Translate Specific Model

```bash
python manage.py translate_candidates
```
- Translates all Candidate objects
- Runs in batches to prevent timeout
- Shows progress bar

### Extract UI Strings

```bash
python manage.py makemessages -l ne
# Edit locale/ne/LC_MESSAGES/django.po
python manage.py compilemessages
```

## Testing Translation

### Unit Test

```python
def test_auto_translation(self):
    candidate = Candidate.objects.create(
        full_name="Test User",
        bio_en="I am a candidate",
        education_en="Bachelor's degree"
    )

    # Check translation happened
    self.assertIsNotNone(candidate.bio_ne)
    self.assertIsNotNone(candidate.education_ne)

    # Check flags set
    self.assertTrue(candidate.is_mt_bio_ne)
    self.assertTrue(candidate.is_mt_education_ne)
```

### Manual Testing

1. Create a candidate with English content
2. Check database for Nepali translations
3. Switch to `/ne/` URL and verify display
4. Check API response includes correct language

## Performance Metrics

- **Translation Speed**: 2-5 seconds per field
- **Cached Translations**: <1ms retrieval
- **UI String Loading**: ~10ms for 264 strings
- **Language Switch**: Page reload (~200-500ms)
- **API Language Detection**: <1ms overhead

## Best Practices

### DO ✅
- Always use `AutoTranslationMixin` for content models
- Use `{% trans %}` tags for all UI text
- Let system handle translation automatically
- Use async translation for large text
- Cache frequently used translations

### DON'T ❌
- Never hardcode Nepali text
- Don't translate names or proper nouns
- Don't override machine translations manually
- Don't call translation API in view rendering
- Don't translate in database queries

## Configuration

### Required Settings

```python
# settings/base.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',  # Required for i18n
    # ... other apps
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',  # Must be after SessionMiddleware
    'django.middleware.common.CommonMiddleware',
    # ... other middleware
]

# Language settings
LANGUAGE_CODE = 'en'
LANGUAGES = [
    ('en', 'English'),
    ('ne', 'नेपाली'),
]
USE_I18N = True
USE_L10N = True
LOCALE_PATHS = [BASE_DIR / 'locale']
```

### Environment Variables

```bash
# .env (optional - for custom translation service)
GOOGLE_TRANSLATE_API_KEY=your-api-key  # Not currently used
TRANSLATION_CACHE_TIMEOUT=3600  # Cache for 1 hour
```

## Troubleshooting

### Translation Not Working

1. Check `is_mt_*` flags in database
2. Verify Google Translate is accessible
3. Check for network/proxy issues
4. Look for errors in logs

### Wrong Language Displayed

1. Check URL for `/ne/` prefix
2. Clear browser cookies
3. Check `request.LANGUAGE_CODE` in view
4. Verify LocaleMiddleware is installed

### Slow Translation

1. Use async translation for large text
2. Implement caching for common phrases
3. Consider batch translation
4. Reduce text length

## Future Improvements

1. **Professional Translation API**
   - Replace Google Translate with Azure or AWS
   - Better handling of political terminology

2. **Translation Memory**
   - Store and reuse previous translations
   - Reduce API calls and costs

3. **Manual Override System**
   - Allow admins to correct translations
   - Lock manually edited translations

4. **Email Localization**
   - Create Nepali email templates
   - Language-aware email sending

---

**Last Updated**: January 2025
**Status**: 95% Complete (Email templates missing)
**Maintainer**: ElectNepal Development Team