"""
Breadcrumb navigation template tags
Provides easy way to add breadcrumb navigation to any page
"""

from django import template
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

register = template.Library()


@register.inclusion_tag('core/breadcrumbs.html', takes_context=True)
def breadcrumbs(context, *items):
    """
    Render breadcrumb navigation

    Usage:
        {% load breadcrumbs %}
        {% breadcrumbs %}  # Auto-detect from URL
        {% breadcrumbs "About" %}  # Home > About
        {% breadcrumbs "Candidates" "/candidates/" "John Doe" %}  # Home > Candidates > John Doe
    """
    request = context.get('request')
    breadcrumb_items = []

    # Always start with Home
    breadcrumb_items.append({
        'title': _('Home'),
        'url': reverse('home'),
        'active': False
    })

    # Process custom items
    i = 0
    while i < len(items):
        title = items[i]

        # Check if next item is a URL
        url = None
        if i + 1 < len(items) and isinstance(items[i + 1], str) and items[i + 1].startswith('/'):
            url = items[i + 1]
            i += 2
        else:
            i += 1

        # Last item is always active (current page)
        is_last = (i >= len(items))

        breadcrumb_items.append({
            'title': title,
            'url': url,
            'active': is_last
        })

    # If no custom items, try to auto-detect from URL
    if len(items) == 0 and request:
        path = request.path

        # Map common paths to breadcrumbs
        if path.startswith('/candidates/ballot'):
            breadcrumb_items.append({
                'title': _('My Ballot'),
                'url': None,
                'active': True
            })
        elif path.startswith('/candidates/dashboard'):
            breadcrumb_items.append({
                'title': _('Dashboard'),
                'url': None,
                'active': True
            })
        elif path.startswith('/candidates/register'):
            breadcrumb_items.append({
                'title': _('Register as Candidate'),
                'url': None,
                'active': True
            })
        elif '/candidates/' in path and path.count('/') > 2:
            # Individual candidate page
            breadcrumb_items.append({
                'title': _('Candidates'),
                'url': reverse('candidates:list'),
                'active': False
            })
            # The candidate name will be added by the template
        elif path.startswith('/candidates/'):
            breadcrumb_items.append({
                'title': _('Candidates'),
                'url': None,
                'active': True
            })
        elif path.startswith('/about'):
            breadcrumb_items.append({
                'title': _('About'),
                'url': None,
                'active': True
            })
        elif path.startswith('/how-to-vote'):
            breadcrumb_items.append({
                'title': _('How to Vote'),
                'url': None,
                'active': True
            })
        elif path.startswith('/auth/login'):
            breadcrumb_items.append({
                'title': _('Login'),
                'url': None,
                'active': True
            })
        elif path.startswith('/auth/signup'):
            breadcrumb_items.append({
                'title': _('Sign Up'),
                'url': None,
                'active': True
            })

    return {
        'breadcrumb_items': breadcrumb_items,
        'request': request
    }


@register.simple_tag
def breadcrumb_schema(items):
    """
    Generate structured data for breadcrumbs (SEO)
    """
    schema = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": []
    }

    for i, item in enumerate(items):
        schema['itemListElement'].append({
            "@type": "ListItem",
            "position": i + 1,
            "name": str(item['title']),
            "item": item.get('url', '')
        })

    import json
    return mark_safe(f'<script type="application/ld+json">{json.dumps(schema)}</script>')