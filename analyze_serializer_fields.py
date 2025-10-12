#!/usr/bin/env python
"""
Analyze which serializer fields are actually used in the frontend
"""

import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nepal_election_app.settings')
django.setup()

print("=" * 80)
print("SERIALIZER FIELD USAGE ANALYSIS")
print("=" * 80)

# Analyze CandidateCardSerializer
print("\n1. CandidateCardSerializer - Defined Fields:")
print("-" * 40)

from candidates.serializers import CandidateCardSerializer

defined_fields = CandidateCardSerializer.Meta.fields
print(f"Total fields defined: {len(defined_fields)}")
for field in defined_fields:
    print(f"  - {field}")

# Check JavaScript usage
print("\n2. Fields Used in Frontend JavaScript:")
print("-" * 40)

js_files = [
    'static/js/candidate-feed.js',
    'static/js/ballot.js',
]

js_used_fields = set()
for js_file in js_files:
    try:
        with open(js_file, 'r') as f:
            content = f.read()
            # Look for candidate.field_name patterns
            import re
            matches = re.findall(r'candidate\.(\w+)', content)
            js_used_fields.update(matches)
    except FileNotFoundError:
        print(f"  Warning: {js_file} not found")

print(f"Fields referenced in JavaScript: {len(js_used_fields)}")
for field in sorted(js_used_fields):
    print(f"  - {field}")

# Check template usage
print("\n3. Fields Used in Templates:")
print("-" * 40)

template_file = 'candidates/templates/candidates/feed_simple_grid.html'
template_used_fields = set()

try:
    with open(template_file, 'r') as f:
        content = f.read()
        import re
        # Look for candidate.field patterns in x-text, :src, etc.
        matches = re.findall(r'candidate\.(\w+)', content)
        template_used_fields.update(matches)
except FileNotFoundError:
    print(f"  Warning: {template_file} not found")

print(f"Fields referenced in templates: {len(template_used_fields)}")
for field in sorted(template_used_fields):
    print(f"  - {field}")

# Combine all used fields
all_used_fields = js_used_fields | template_used_fields

print("\n4. All Used Fields (Combined):")
print("-" * 40)
print(f"Total unique fields used: {len(all_used_fields)}")
for field in sorted(all_used_fields):
    print(f"  - {field}")

# Find unused fields
print("\n5. UNUSED FIELDS in CandidateCardSerializer:")
print("-" * 40)

unused_fields = set(defined_fields) - all_used_fields
print(f"Total unused fields: {len(unused_fields)}")
for field in sorted(unused_fields):
    print(f"  - {field}")

# Find definitely used fields (essential for frontend)
essential_fields = all_used_fields & set(defined_fields)
print("\n6. ESSENTIAL FIELDS (Used in Frontend):")
print("-" * 40)
print(f"Total essential fields: {len(essential_fields)}")
for field in sorted(essential_fields):
    print(f"  - {field}")

# Analyze CandidateBallotSerializer
print("\n" + "=" * 80)
print("CandidateBallotSerializer Analysis:")
print("=" * 80)

from candidates.serializers import CandidateBallotSerializer

ballot_defined_fields = CandidateBallotSerializer.Meta.fields
print(f"\nTotal fields defined: {len(ballot_defined_fields)}")
for field in ballot_defined_fields:
    print(f"  - {field}")

# Check ballot.js usage
ballot_used_fields = set()
try:
    with open('static/js/ballot.js', 'r') as f:
        content = f.read()
        import re
        matches = re.findall(r'candidate\.(\w+)', content)
        ballot_used_fields.update(matches)
except FileNotFoundError:
    pass

print(f"\nFields used in ballot.js: {len(ballot_used_fields)}")
for field in sorted(ballot_used_fields):
    print(f"  - {field}")

ballot_unused = set(ballot_defined_fields) - ballot_used_fields
print(f"\nUNUSED fields in CandidateBallotSerializer: {len(ballot_unused)}")
for field in sorted(ballot_unused):
    print(f"  - {field}")

print("\n" + "=" * 80)
print("RECOMMENDATIONS:")
print("=" * 80)

print("\n1. Remove these fields from CandidateCardSerializer:")
for field in sorted(unused_fields):
    print(f"   - {field}")

print("\n2. Remove these fields from CandidateBallotSerializer:")
for field in sorted(ballot_unused):
    print(f"   - {field}")

print("\n3. Keep these essential fields in CandidateCardSerializer:")
for field in sorted(essential_fields):
    print(f"   - {field}")

print("\n" + "=" * 80)
