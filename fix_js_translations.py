#!/usr/bin/env python
"""
Script to identify and document JavaScript strings that need translation.
These strings should be passed from Django templates or use a JavaScript i18n library.
"""

import re
import json

# List of JavaScript strings that need translation
JS_STRINGS_TO_TRANSLATE = [
    {
        "file": "static/js/main.js",
        "line": 25,
        "string": "Cookie settings feature coming soon! For now, all cookies are essential for the app to function properly.",
        "context": "Cookie settings alert",
        "solution": "Pass from Django template as data attribute"
    },
    {
        "file": "static/js/main.js",
        "line": 327,
        "string": "Showing candidates in:",
        "context": "Location status display",
        "solution": "Pass from Django template or use data-i18n attributes"
    },
    {
        "file": "static/js/main.js",
        "line": 352,
        "string": "No candidates found in your area yet.",
        "context": "Empty state message",
        "solution": "Pass from Django template"
    },
    {
        "file": "static/js/main.js",
        "line": 353,
        "string": "Try adjusting your filters or search in a different location.",
        "context": "Empty state help text",
        "solution": "Pass from Django template"
    },
    {
        "file": "static/js/main.js",
        "line": 338,
        "string": "Error loading candidates. Please try again.",
        "context": "Error message",
        "solution": "Pass from Django template"
    }
]

def main():
    print("JavaScript Translation Issues Report")
    print("=" * 60)
    print("\nThe following JavaScript strings are hardcoded and need translation:")
    print("-" * 60)

    for item in JS_STRINGS_TO_TRANSLATE:
        print(f"\nFile: {item['file']}")
        print(f"Line: {item['line']}")
        print(f"String: \"{item['string']}\"")
        print(f"Context: {item['context']}")
        print(f"Suggested Fix: {item['solution']}")

    print("\n" + "=" * 60)
    print("\nRecommended Solutions:")
    print("-" * 60)
    print("""
1. Pass translations from Django templates as data attributes:
   <div id="translations"
        data-cookie-settings="{% trans 'Cookie settings feature coming soon!' %}"
        data-no-candidates="{% trans 'No candidates found in your area yet.' %}"
        data-error-loading="{% trans 'Error loading candidates. Please try again.' %}">
   </div>

2. Access in JavaScript:
   const translations = document.getElementById('translations').dataset;
   alert(translations.cookieSettings);

3. Or use Django's JavaScript catalog:
   Add to urls.py:
   from django.views.i18n import JavaScriptCatalog
   path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),

   Then in template:
   <script src="{% url 'javascript-catalog' %}"></script>
   <script>
     console.log(gettext('String to translate'));
   </script>
""")

if __name__ == "__main__":
    main()