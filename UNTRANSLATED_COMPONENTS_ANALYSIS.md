# Untranslated Components - Complete Analysis

**Date**: October 15, 2025
**Issue**: Multiple components showing English text on Nepali pages
**Root Cause**: NOT using bilingual infrastructure - hardcoding values instead

---

## Critical Finding

The user is **100% CORRECT** - many components are NOT being translated by the bilingual system. They are hardcoded in Python/JavaScript which bypasses Django's translation framework.

---

## Category 1: Python Messages (HARDCODED - WRONG)

**Location**: `authentication/views.py`, `candidates/views.py`, `candidates/admin.py`
**Count**: 24 instances
**Problem**: Using raw English strings in `messages.success/error/warning/info()`
**Why Wrong**: Bypasses Django translation system

### Examples Found
```python
# WRONG - Hardcoded English
messages.success(self.request, f'Welcome back, {self.request.user.username}!')
messages.error(request, 'Your profile must be approved before you can edit it.')
messages.info(request, 'You already have a candidate profile.')
```

### Correct Approach (Using Bilingual System)
```python
# CORRECT - Uses translation system
from django.utils.translation import gettext as _

messages.success(self.request, _('Welcome back, %(username)s!') % {'username': self.request.user.username})
messages.error(request, _('Your profile must be approved before you can edit it.'))
messages.info(request, _('You already have a candidate profile.'))
```

### All 24 Instances

**authentication/views.py**:
1. Line 162: `f'Welcome back, {username}!'` ✅ FIXED
2. Line 176: `'You have been logged out successfully.'` ✅ FIXED
3. Line 190: `'Your email has already been verified. You can log in.'`
4. Line 209: `'Verification failed. Please try again or contact support.'`
5. Line 213: `'Invalid verification link.'`
6. Line 230: `'Your email is already verified. You can log in.'`
7. Line 382: `'This password reset link has expired.'`
8. Line 390: `'Passwords do not match.'`
9. Line 401: `'Your password has been reset successfully! You can now log in.'`
10. Line 405: `'Invalid password reset link.'`

**candidates/views.py**:
11. Line 608: `'You already have a candidate profile.'`
12. Line 644: `'Your candidate profile has been submitted for review! You will be notified once approved.'`
13. Line 648: `f'Registration failed: {str(e)}. Please try again.'`
14. Line 669: `'You need to create a candidate profile first.'`
15. Line 707: `'Your profile must be approved before you can edit it.'`
16. Line 728: `'Your profile has been updated successfully!'`
17. Line 731: `f'Profile update failed: {str(e)}. Please try again.'`
18. Line 777: `'Your profile must be approved before you can add events.'`
19. Line 788: `'Event created successfully!'`
20. Line 791: `f'Event creation failed: {str(e)}. Please try again.'`

**candidates/admin.py**:
21-24. Lines 138-156: Admin email notification messages

---

## Category 2: Template Step Labels (HARDCODED - WRONG)

**Location**: `candidates/templates/candidates/register.html` lines 22-35
**Problem**: Progress indicator labels hardcoded in English
**Why Wrong**: Not using `{% trans %}` tags

### Examples Found
```html
<!-- WRONG - Hardcoded English -->
<span class="font-semibold text-blue-600 text-base">Step 1 of 5: Basic Info</span>
<span class="font-semibold text-blue-600 whitespace-nowrap">1. Basic Info</span>
<span class="text-gray-600 whitespace-nowrap">2. Location</span>
<span class="text-gray-600 whitespace-nowrap">3. Content</span>
<span class="text-gray-600 whitespace-nowrap">4. Documents</span>
<span class="text-gray-600 whitespace-nowrap">5. Review</span>
```

### Correct Approach
```html
<!-- CORRECT - Uses translation tags -->
<span class="font-semibold text-blue-600 text-base">{% trans "Step" %} 1 {% trans "of" %} 5: {% trans "Basic Info" %}</span>
<span class="font-semibold text-blue-600 whitespace-nowrap">1. {% trans "Basic Info" %}</span>
<span class="text-gray-600 whitespace-nowrap">2. {% trans "Location" %}</span>
<span class="text-gray-600 whitespace-nowrap">3. {% trans "Content" %}</span>
<span class="text-gray-600 whitespace-nowrap">4. {% trans "Documents" %}</span>
<span class="text-gray-600 whitespace-nowrap">5. {% trans "Review" %}</span>
```

---

## Category 3: JavaScript Alert Messages (HARDCODED - WRONG)

**Location**: `candidates/templates/candidates/register.html` lines 343-423
**Count**: 15+ alert() calls
**Problem**: Validation messages hardcoded in JavaScript
**Why Wrong**: JavaScript can't access Django's `{% trans %}` tags

### Examples Found
```javascript
// WRONG - Hardcoded English
alert('Please enter your full name');
alert('Please enter a valid age (must be 18 or older)');
alert('Please upload your profile photo (required)');
alert('Please select a seat');
alert('Please select a province');
```

### Correct Approach (Django i18n for JavaScript)

**Option 1: Use Django's JavaScript catalog**
```html
<script src="{% url 'javascript-catalog' %}"></script>
<script>
// CORRECT - Uses gettext from Django
alert(gettext('Please enter your full name'));
alert(gettext('Please upload your profile photo (required)'));
</script>
```

**Option 2: Pass translated strings from server**
```html
<script>
const messages = {
    enterFullName: "{% trans 'Please enter your full name' %}",
    uploadPhoto: "{% trans 'Please upload your profile photo (required)' %}",
    // ... etc
};
alert(messages.enterFullName);
</script>
```

---

## Category 4: "Ward X" Labels (GENERATED IN JS - WRONG)

**Location**: `candidates/templates/candidates/register.html` line 508
**Problem**: Ward labels generated dynamically in JavaScript
**Why Wrong**: Hardcoded "Ward" text in English

### Example Found
```javascript
// WRONG - Hardcoded "Ward" text
option.textContent = `Ward ${i}`;
```

### Correct Approach
```javascript
// CORRECT - Use pre-translated template
const wardLabel = "{% trans 'Ward' %}";
option.textContent = `${wardLabel} ${i}`;
```

---

## Category 5: Location Names (WRONG FIELD - CRITICAL)

**Location**: ALL templates and APIs showing location data
**Problem**: Always showing `name_en` field instead of language-aware `name_ne`
**Why Wrong**: Not respecting user's language preference
**Impact**: HIGH - This is why Lumbini, Palpa, R ipdikot show in English on Nepali pages

### Examples Found

**In JavaScript** (register.html lines 449-451, 474-476):
```javascript
// WRONG - Always uses name_en
const option = new Option(district.name_en, district.id);
const option = new Option(municipality.name_en, municipality.id);
```

**In API Views** (`locations/views.py`, `locations/api_views.py`):
```python
# WRONG - Always returns name_en
{
    'id': district.id,
    'name_en': district.name_en,
    'name_ne': district.name_ne
}
```

**In Templates** (wherever location names displayed):
```django
{# WRONG - Hardcoded to English field #}
{{ candidate.province.name_en }}
{{ candidate.district.name_en }}
{{ candidate.municipality.name_en }}
```

### Correct Approach (Language-Aware Data)

**In Models** (Create a property):
```python
from django.utils.translation import get_language

class Province(models.Model):
    name_en = models.CharField(max_length=100)
    name_ne = models.CharField(max_length=100)

    @property
    def name(self):
        """Return name in current language"""
        lang = get_language()
        if lang == 'ne':
            return self.name_ne or self.name_en
        return self.name_en
```

**In Templates**:
```django
{# CORRECT - Uses language-aware property #}
{{ candidate.province.name }}
{{ candidate.district.name }}
{{ candidate.municipality.name }}
```

**In APIs**:
```python
from django.utils.translation import get_language

def get_districts(request):
    province_id = request.GET.get('province')
    districts = District.objects.filter(province_id=province_id)

    lang = get_language()
    name_field = 'name_ne' if lang == 'ne' else 'name_en'

    return JsonResponse([
        {
            'id': d.id,
            'name': getattr(d, name_field)  # Language-aware!
        }
        for d in districts
    ], safe=False)
```

**In JavaScript**:
```javascript
// CORRECT - Uses language-aware 'name' field from API
const option = new Option(district.name, district.id);
const option = new Option(municipality.name, municipality.id);
```

---

## Category 6: "No file chosen" (BROWSER DEFAULT - CAN'T FIX)

**Location**: File input buttons
**Problem**: Shows "No file chosen" in English
**Why Wrong**: This is browser default text, not from our code
**Solution**: Can't fix - this is built into the browser. We can hide it with CSS and show custom text instead.

**Workaround**:
```html
<input type="file" id="photo" style="display:none">
<button onclick="document.getElementById('photo').click()">
    {% trans "Choose File" %}
</button>
<span id="filename">{% trans "No file selected" %}</span>
```

---

## Summary of Issues

| Category | Count | Status | Priority |
|----------|-------|--------|----------|
| Python Messages | 24 | 2/24 fixed | HIGH |
| Template Step Labels | 6 | Not started | HIGH |
| JavaScript Alerts | 15+ | Not started | HIGH |
| Ward Labels in JS | 1 | Not started | MEDIUM |
| Location Names (Fields) | ALL | Not started | **CRITICAL** |
| Browser Defaults | N/A | Can't fix | LOW |

---

## Bilingual System Philosophy Violations

### What's Wrong
1. ❌ **Hardcoding English text** in Python code (`messages.success()`)
2. ❌ **Hardcoding English text** in HTML templates (step labels)
3. ❌ **Hardcoding English text** in JavaScript (alert messages)
4. ❌ **Always using `name_en` field** instead of language-aware selection
5. ❌ **Not respecting `get_language()`** in data fetching

### What's Required (Bilingual System)
1. ✅ ALL Python strings must use `gettext()` or `_()`
2. ✅ ALL template strings must use `{% trans %}` tags
3. ✅ ALL JavaScript must use Django's JavaScript catalog or translated variables
4. ✅ ALL data fetching must be language-aware (check `get_language()`)
5. ✅ ALL location names must use `.name` property that returns correct language

---

## Fix Priority Order

### Phase 1: Critical Fixes (Location Names)
1. Add `.name` property to Province, District, Municipality models
2. Update ALL API views to return language-aware data
3. Update JavaScript to use `name` instead of `name_en`
4. Update ALL templates to use `.name` property
5. **Impact**: Lumbini → लुम्बिनी, Palpa → पाल्पा on Nepali pages

### Phase 2: High Priority (UI Messages)
1. Fix all 24 Python message strings to use `_()`
2. Fix template step labels to use `{% trans %}`
3. Fix JavaScript alerts to use Django i18n catalog
4. Extract all new strings with `makemessages`
5. Auto-translate with `auto_translate_po_file.py`
6. Compile with `compilemessages`
7. **Impact**: "Welcome back, maya!" → "फेरि स्वागत छ, maya!"

### Phase 3: Medium Priority (Generated Labels)
1. Fix "Ward X" labels in JavaScript
2. **Impact**: "Ward 4" → "वडा ४"

---

## Verification Checklist

After fixes, verify:
- [ ] NO hardcoded English in Python files
- [ ] NO hardcoded English in templates
- [ ] NO hardcoded English in JavaScript
- [ ] Location names show in Nepali on `/ne/` pages
- [ ] All messages show in Nepali on `/ne/` pages
- [ ] Step labels show in Nepali
- [ ] Alert messages show in Nepali
- [ ] Ward labels show in Nepali
- [ ] Run `makemessages`, verify all strings extracted
- [ ] Run `auto_translate_po_file.py`, verify translations
- [ ] Run `compilemessages`, verify no errors
- [ ] Test complete registration flow in Nepali
- [ ] Test ALL pages in Nepali - should be 100% Nepali (except "ElectNepal" brand)

---

**Philosophy**: "Everything is translated by bilingual infrastructure, not hardcoded"
**Status**: ❌ VIOLATED in 5 major categories
**Action Required**: Systematic fixes following bilingual system protocols

