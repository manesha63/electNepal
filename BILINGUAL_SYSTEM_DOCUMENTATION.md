# 🌐 ElectNepal Bilingual System Documentation

## Executive Summary

ElectNepal implements a **100% automated bilingual system** (English/Nepali) where developers only work with English content, and the system automatically handles all Nepali translations. This document outlines the complete implementation, protocols, and guidelines.

**STATUS: ✅ FULLY OPERATIONAL** (Last verified: January 20, 2025)

---

## 🎯 Core Principle

> **"Write Once in English, Display Everywhere in Both Languages"**

Developers NEVER manually translate content. The system automatically:
- Translates all content from English to Nepali
- Caches translations for performance
- Displays correct language based on user preference
- Falls back gracefully if translation fails

---

## 📁 System Architecture

### 1. Base Classes (`core/models_base.py`)

#### `BilingualModel`
Base class for all content models with automatic translation:

```python
from core.models_base import BilingualModel

class YourModel(BilingualModel):
    BILINGUAL_FIELDS = ['title', 'description']

    # Fields are automatically created as:
    # title_en, title_ne, is_mt_title_ne
    # description_en, description_ne, is_mt_description_ne
```

#### `BilingualCharField` & `BilingualTextField`
Custom field types that automatically create bilingual versions:

```python
from core.models_base import BilingualCharField, BilingualTextField

class Article(BilingualModel):
    title = BilingualCharField(max_length=200)  # Creates title_en, title_ne
    content = BilingualTextField()  # Creates content_en, content_ne
```

### 2. Automatic Translation System

#### Primary Translation Method (`candidates/models.py`)
- **Direct Google Translate Integration**: Models use `googletrans` library directly
- **Method**: `_fill_missing_pair()` in Candidate model
- **Configuration**: `MT_ENGINE=google` in `.env` file
- **Status**: ✅ WORKING - Verified with live tests

#### Supplementary System (`core/auto_translate.py`)
- **SmartTranslator**: Handles translation with 30-day caching
- **Pre-save Signals**: Auto-translate before saving to database
- **Bulk Translation**: Management command for existing data
- **Status**: ✅ WORKING - All components operational

#### How It Works:
1. Model save triggered → `autotranslate_missing()` method called
2. System checks for empty Nepali fields
3. Translates from English using Google Translate API directly
4. Caches translation for 30 days (via SmartTranslator)
5. Sets machine translation flag (is_mt_field_ne = True)

### 3. Template Tags (`core/templatetags/bilingual.py`)

#### Available Tags:

```django
{% load bilingual %}

<!-- Get field in current language -->
{{ candidate|bilingual:'bio' }}

<!-- Display location name -->
{{ province|location_name }}

<!-- Choose text based on language -->
{% trans_choice "English" "नेपाली" %}

<!-- Display position -->
{% position_display candidate.position_level %}

<!-- Render complete bilingual field -->
{% render_bilingual_field candidate 'manifesto' 'Political Manifesto' %}
```

---

## 🛠️ Development Protocol

### ✅ ALWAYS DO:

#### 1. **For New Models**
```python
# CORRECT - Inherit from BilingualModel
from core.models_base import BilingualModel, BilingualCharField

class NewFeature(BilingualModel):
    BILINGUAL_FIELDS = ['name', 'description']

    name = BilingualCharField(max_length=100)
    description = BilingualTextField()
```

#### 2. **For Forms**
```python
# Only include English fields in forms
class NewFeatureForm(forms.ModelForm):
    class Meta:
        model = NewFeature
        fields = ['name_en', 'description_en']  # Only English
        labels = {
            'name_en': 'Name',
            'description_en': 'Description'
        }
```

#### 3. **In Templates**
```django
{% load bilingual %}

<!-- CORRECT - Use bilingual tags -->
<h1>{{ feature|bilingual:'name' }}</h1>
<p>{{ feature|bilingual:'description' }}</p>

<!-- For UI labels -->
<label>{% trans "Name:" %}</label>
```

#### 4. **In Views**
```python
# Create with English only
feature = NewFeature.objects.create(
    name_en="My Feature",  # Only provide English
    description_en="Description here"
    # name_ne and description_ne are auto-filled
)

# The system automatically handles translation
```

### ❌ NEVER DO:

#### 1. **Don't Create Standalone Text Fields**
```python
# WRONG - Single language field
class BadModel(models.Model):
    title = models.CharField(max_length=200)  # ❌ Not bilingual

# WRONG - Manual bilingual fields
class BadModel(models.Model):
    title_en = models.CharField(max_length=200)
    title_ne = models.CharField(max_length=200)  # ❌ No auto-translation
```

#### 2. **Don't Manually Translate**
```python
# WRONG - Manual translation
candidate.bio_ne = "मेरो जीवनी"  # ❌ Never manually set Nepali

# WRONG - Calling translator directly
from googletrans import Translator
translator = Translator()
text_ne = translator.translate(text_en)  # ❌ Don't do this
```

#### 3. **Don't Hardcode Text in Templates**
```django
<!-- WRONG - Hardcoded text -->
<h1>Welcome to ElectNepal</h1>  <!-- ❌ Not translatable -->

<!-- CORRECT -->
<h1>{% trans "Welcome to ElectNepal" %}</h1>  <!-- ✅ -->
```

---

## 📋 Implementation Checklist

### For New Features:

- [ ] Model inherits from `BilingualModel`
- [ ] Text fields use `BilingualCharField` or `BilingualTextField`
- [ ] Forms only include `_en` fields
- [ ] Templates use `{% load bilingual %}` tags
- [ ] UI text wrapped in `{% trans %}` tags
- [ ] Admin registers bilingual fields properly
- [ ] No manual Nepali content entry

### For Existing Features:

- [ ] Run migration to add bilingual fields
- [ ] Run `python manage.py ensure_all_translations`
- [ ] Update templates to use bilingual tags
- [ ] Test language switching works

---

## 🔧 Management Commands

### Translate All Content
```bash
python manage.py ensure_all_translations
```

### Validate Bilingual Compliance
```bash
python manage.py shell
from core.bilingual_validator import run_validation
run_validation()
```

---

## 🌍 Language Switching

### URL Structure:
- **English**: `/candidates/`, `/about/`
- **Nepali**: `/ne/candidates/`, `/ne/about/`

### How Users Switch:
1. Click language button in navigation
2. JavaScript updates URL prefix
3. Django serves content in selected language
4. Cookie saves preference

### Template Implementation:
```javascript
// In main.js
function switchLanguage() {
    let currentPath = window.location.pathname;
    const isNepali = currentPath.startsWith('/ne/');

    if (isNepali) {
        window.location.href = currentPath.replace('/ne/', '/');
    } else {
        window.location.href = '/ne' + currentPath;
    }
}
```

---

## 📊 Database Schema

### Bilingual Field Pattern:

For each content field, three database columns are created:

| Field Purpose | Column Name | Type | Description |
|--------------|-------------|------|-------------|
| English Content | `field_en` | Text/Char | Original English content |
| Nepali Content | `field_ne` | Text/Char | Auto-translated Nepali |
| Translation Flag | `is_mt_field_ne` | Boolean | True if machine translated |

### Example:
```sql
-- For a 'bio' field
bio_en          TEXT NOT NULL     -- English biography
bio_ne          TEXT              -- Nepali biography (auto-filled)
is_mt_bio_ne    BOOLEAN DEFAULT FALSE  -- Translation flag
```

---

## 🚀 Quick Start for New Developers

### 1. Create a New Bilingual Model:
```python
# models.py
from core.models_base import BilingualModel, BilingualCharField

class Event(BilingualModel):
    BILINGUAL_FIELDS = ['title', 'description']

    title = BilingualCharField(max_length=200)
    description = BilingualTextField()
```

### 2. Create Admin:
```python
# admin.py
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title_en', 'title_ne']
    fields = ['title_en', 'description_en']  # Only show English in admin
```

### 3. Create Template:
```django
<!-- event_detail.html -->
{% load bilingual %}

<h1>{{ event|bilingual:'title' }}</h1>
<p>{{ event|bilingual:'description' }}</p>
```

### 4. That's It!
The system handles everything else automatically.

---

## 🔍 Validation & Testing

### Run Validation:
```python
from core.bilingual_validator import BilingualValidator

validator = BilingualValidator()
validator.validate_all_models()
print(validator.generate_report())
```

### Test Translation:
```python
# Create test content
event = Event.objects.create(
    title_en="Test Event",
    description_en="This is a test"
)

# Check auto-translation
assert event.title_ne is not None
assert event.is_mt_title_ne == True
```

---

## 🐛 Troubleshooting

### Issue: Nepali fields are empty
**Solution**: Run `python manage.py ensure_all_translations`

### Issue: Translation not working
**Check**:
1. Internet connection (for Google Translate API)
2. Model inherits from `BilingualModel`
3. Fields listed in `BILINGUAL_FIELDS`

### Issue: Wrong language displayed
**Check**:
1. URL has correct prefix (`/ne/` for Nepali)
2. Template uses bilingual tags
3. Language cookie is set correctly

---

## 📈 Performance Optimization

### Caching Strategy:
- **Translation Cache**: 30 days per unique text
- **Database Queries**: Use `select_related()` for locations
- **Template Caching**: Cache rendered bilingual content

### Best Practices:
1. Translate during save, not on display
2. Cache all translations
3. Batch translate when possible
4. Use prefetch for related bilingual objects

---

## 🔐 Security Considerations

1. **Sanitize Input**: Always sanitize before translation
2. **Rate Limiting**: Implement for translation API
3. **Cache Security**: Don't cache sensitive data
4. **XSS Protection**: Escape translated content in templates

---

## 📝 Code Examples

### Complete Example - News Article:

```python
# models.py
from core.models_base import BilingualModel, BilingualCharField, BilingualTextField

class NewsArticle(BilingualModel):
    BILINGUAL_FIELDS = ['title', 'summary', 'content']

    title = BilingualCharField(max_length=200)
    summary = BilingualCharField(max_length=500)
    content = BilingualTextField()
    published_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-published_at']

# views.py
def create_article(request):
    article = NewsArticle.objects.create(
        title_en=request.POST['title'],
        summary_en=request.POST['summary'],
        content_en=request.POST['content']
        # Nepali versions auto-generated
    )
    return redirect('article_detail', pk=article.pk)

# template
{% load bilingual %}
<article>
    <h1>{{ article|bilingual:'title' }}</h1>
    <p class="summary">{{ article|bilingual:'summary' }}</p>
    <div class="content">
        {{ article|bilingual:'content'|linebreaksbr }}
    </div>
</article>
```

---

## 🎓 Training Checklist for Developers

Before coding, ensure you understand:

- [ ] How BilingualModel works
- [ ] When translation happens (on save)
- [ ] How to use bilingual template tags
- [ ] URL structure for languages
- [ ] How to test bilingual features
- [ ] Where translations are cached
- [ ] How to debug translation issues

---

## 📚 Additional Resources

- **Django i18n Documentation**: https://docs.djangoproject.com/en/4.2/topics/i18n/
- **Google Translate API**: https://pypi.org/project/googletrans/
- **Project Structure**: See CLAUDE.md for overall architecture

---

## ✅ System Verification Results (September 20, 2025)

### All Components Tested and Working:
1. **Google Translate API**: ✅ Direct integration via googletrans library
2. **Model Auto-Translation**: ✅ New candidates auto-translate on save
3. **Template Tags**: ✅ Language switching works correctly
4. **SmartTranslator Cache**: ✅ 30-day caching operational
5. **CandidatePost Model**: ✅ Auto-translation working
6. **CandidateEvent Model**: ✅ Auto-translation working
7. **Location Data**: ✅ All 837 locations bilingual
8. **API Language Awareness**: ✅ Returns correct language based on URL prefix
9. **UI Label Translation**: ✅ All interface text properly translated
10. **Dynamic Content**: ✅ JavaScript fetches language-aware API endpoints

### Recent Fixes (September 20, 2025):
- Fixed API URL detection in feed_simple_grid.html to use language prefix
- Added missing UI translations (Motivation, Political Manifesto, etc.)
- Fixed location names displaying in English on Nepali interface
- Made error messages translatable ("Location outside Nepal boundaries")

### Live Test Results:
- Created test candidate with English-only content
- All fields automatically translated to Nepali
- Nepali script (Devanagari) verified in all translations
- Machine translation flags properly set
- API returns English data for `/candidates/api/cards/`
- API returns Nepali data for `/ne/candidates/api/cards/`

## 🚨 CRITICAL REMINDERS

1. **NEVER** manually write Nepali content
2. **ALWAYS** inherit from BilingualModel for content models
3. **ALWAYS** use bilingual template tags
4. **NEVER** hardcode text in templates
5. **ALWAYS** test both languages before deploying

---

## 📊 Metrics & Monitoring

Track these metrics to ensure system health:

1. **Translation Success Rate**: Should be >95%
2. **Cache Hit Rate**: Should be >80%
3. **Average Translation Time**: Should be <500ms
4. **Missing Translations**: Should be 0

---

## Version History

- **v1.0** (2025-01-19): Initial bilingual system
- **v2.0** (2025-01-19): Added automatic translation
- **v3.0** (2025-01-20): Fixed translation issues, switched to Google Translate
- **v3.1** (2025-01-20): Complete automation with verification and testing
- **v3.2** (2025-09-20): Fixed API language detection and missing UI translations

## Technical Implementation Details

### Translation Method Used
```python
# In candidates/models.py
def _fill_missing_pair(self, en_field, ne_field, mt_flag_field):
    """Auto-translate from English to Nepali using Google Translate directly"""
    from googletrans import Translator
    translator = Translator()
    result = translator.translate(en_value, src='en', dest='ne')
    translated = result.text
    setattr(self, ne_field, translated)
    setattr(self, mt_flag_field, True)
```

### Environment Configuration
```bash
# .env file
MT_ENGINE=google  # Uses Google Translate API
```

---

**Last Updated**: September 20, 2025
**Maintained By**: ElectNepal Development Team
**Status**: ✅ Production Ready - All Systems Operational