#!/usr/bin/env python
"""
Auto-translate django.po file using Google Translate API

This script automatically translates all English strings in the django.po file
to Nepali using Google Translate API, following the ElectNepal bilingual system
philosophy of automatic translation rather than manual hardcoding.

Usage:
    python auto_translate_po_file.py [--force] [--verify-only]

Options:
    --force: Retranslate even if translation exists (use with caution)
    --verify-only: Only show what would be translated without making changes
"""

import sys
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nepal_election_app.settings')
django.setup()

from googletrans import Translator
import polib
from pathlib import Path

# Known wrong translations that MUST be fixed
WRONG_TRANSLATIONS = {
    "Phone Number": "वडा नम्बर",  # Currently says "Ward Number" - WRONG
    "Enter your username": "वार्ड नम्बर प्रविष्ट गर्नुहोस्",  # Says "Enter ward number" - WRONG
    "Basic Information": "सम्पर्क जानकारी",  # Says "Contact Information" - WRONG
    "Ward Member": "वडा नम्बर",  # Says "Ward Number" - WRONG
    "Edit Profile": "प्रोफाइल हेर्नुहोस्",  # Says "View Profile" - WRONG
    "Age": "उमेर:",  # Has unnecessary colon - WRONG
    "बूढो हनु": "WRONG",  # Wrong auto-translation for "Age"
}

# Dictionary of accurate translations for common terms
# These override Google Translate when the API produces poor results
ACCURATE_TRANSLATIONS = {
    "Age": "उमेर",
    "Note": "नोट",
    "Time:": "समय:",
    "Switch language": "भाषा बदल्नुहोस्",
    "Toggle navigation menu": "नेभिगेसन मेनू टगल गर्नुहोस्",
    "Position": "पद",
    "Welcome back": "फेरि स्वागत छ",
    "Email": "इमेल",
    "Status": "स्थिति",
    "Description": "विवरण",
    "Register": "दर्ता गर्नुहोस्",
    "About": "बारेमा",
    "Minimum 8 characters": "न्यूनतम ८ वर्ण",
    "Dashboard": "ड्यासबोर्ड",
    "Pending Review": "समीक्षा बाँकी",
    "Phone Number": "फोन नम्बर",
    "Basic Information": "आधारभूत जानकारी",
    "Ward Member": "वार्ड सदस्य",
}

def auto_translate_po_file(force=False, verify_only=False, translate_fuzzy=False):
    """
    Auto-translate django.po file using Google Translate API

    Args:
        force: If True, retranslate even if translation exists
        verify_only: If True, only show what would be translated
    """
    po_file_path = Path(__file__).parent / 'locale/ne/LC_MESSAGES/django.po'

    if not po_file_path.exists():
        print(f"❌ ERROR: {po_file_path} not found!")
        return False

    print(f"📖 Reading translation file: {po_file_path}")
    po = polib.pofile(str(po_file_path))

    translator = Translator()

    translated_count = 0
    fixed_count = 0
    skipped_count = 0
    error_count = 0

    total_entries = len([e for e in po if e.msgid and not e.obsolete])

    print(f"\n🔍 Found {total_entries} translation entries")
    print(f"{'='*80}\n")

    for entry in po:
        # Skip empty entries and obsolete entries
        if not entry.msgid or entry.obsolete:
            continue

        # Determine if we need to translate this entry
        needs_translation = False
        is_wrong_translation = False

        # Check if it's a known wrong translation (by msgstr value)
        if entry.msgstr in WRONG_TRANSLATIONS.values():
            needs_translation = True
            is_wrong_translation = True
            print(f"🔴 WRONG TRANSLATION DETECTED:")
            print(f"   English: {entry.msgid}")
            print(f"   Current: {entry.msgstr}")
        # Check if it's a known wrong translation (by msgid)
        elif entry.msgid in WRONG_TRANSLATIONS:
            if entry.msgstr == WRONG_TRANSLATIONS[entry.msgid]:
                needs_translation = True
                is_wrong_translation = True
                print(f"🔴 WRONG TRANSLATION DETECTED:")
                print(f"   English: {entry.msgid}")
                print(f"   Current: {entry.msgstr}")

        # Check if translation is missing
        elif not entry.msgstr or entry.msgstr == "":
            needs_translation = True
            print(f"⚠️  MISSING TRANSLATION:")
            print(f"   English: {entry.msgid}")

        # Check if fuzzy (needs review)
        elif translate_fuzzy and 'fuzzy' in entry.flags:
            needs_translation = True
            print(f"🔍 FUZZY TRANSLATION (outdated):")
            print(f"   English: {entry.msgid}")
            print(f"   Current: {entry.msgstr}")

        # Force retranslation if requested
        elif force:
            needs_translation = True
            print(f"🔄 FORCE RETRANSLATE:")
            print(f"   English: {entry.msgid}")
            print(f"   Current: {entry.msgstr}")

        else:
            skipped_count += 1
            continue

        # If we only want to verify, skip actual translation
        if verify_only:
            print(f"   [VERIFY ONLY - Would translate]\n")
            continue

        # Perform translation
        try:
            # Check if we have an accurate translation in our dictionary
            if entry.msgid in ACCURATE_TRANSLATIONS:
                new_translation = ACCURATE_TRANSLATIONS[entry.msgid]
                print(f"   Using accurate translation from dictionary")
            else:
                result = translator.translate(entry.msgid, src='en', dest='ne')
                new_translation = result.text

                # Preserve Python format placeholders (%(variable)s, %s, %d, etc.)
                import re
                # Find all Python format placeholders in original
                placeholders = re.findall(r'%\([^)]+\)[sd]|%[sd]', entry.msgid)
                if placeholders:
                    # The translation might have broken the placeholders
                    # Try to restore them by replacing malformed versions
                    for placeholder in placeholders:
                        # Common broken patterns from Google Translate
                        broken_patterns = [
                            placeholder.replace('%(', '% ('),  # Spaces added
                            placeholder.replace(')s', ') s'),
                            placeholder.replace(')d', ') d'),
                            # URL encoded versions
                            placeholder.replace('(', '%28').replace(')', '%29'),
                        ]
                        for broken in broken_patterns:
                            if broken in new_translation:
                                new_translation = new_translation.replace(broken, placeholder)
                                print(f"   Fixed broken placeholder: {broken} → {placeholder}")

            # Update entry
            old_translation = entry.msgstr
            entry.msgstr = new_translation

            # Clear fuzzy flag if this was a fuzzy entry
            if 'fuzzy' in entry.flags:
                entry.flags.remove('fuzzy')

            # Add comment to track auto-translation
            if "Auto-translated" not in (entry.comment or ""):
                entry.comment = f"Auto-translated by auto_translate_po_file.py\n{entry.comment or ''}"

            print(f"   New: {new_translation}")

            if is_wrong_translation:
                print(f"   ✅ FIXED wrong translation")
                fixed_count += 1
            else:
                print(f"   ✅ TRANSLATED")
                translated_count += 1

            print()

        except Exception as e:
            print(f"   ❌ FAILED: {e}\n")
            error_count += 1

    # Save the file if not in verify mode
    if not verify_only:
        print(f"\n{'='*80}")
        print(f"💾 Saving translations to: {po_file_path}")
        po.save()
        print(f"✅ Saved successfully!")

    # Print summary
    print(f"\n{'='*80}")
    print(f"📊 SUMMARY:")
    print(f"{'='*80}")
    print(f"Total entries: {total_entries}")
    print(f"✅ Fixed wrong translations: {fixed_count}")
    print(f"✅ Added missing translations: {translated_count}")
    print(f"⏭️  Skipped (already translated): {skipped_count}")
    print(f"❌ Errors: {error_count}")

    if verify_only:
        print(f"\n⚠️  VERIFY MODE - No changes were made")
        print(f"Run without --verify-only to apply translations")
    else:
        print(f"\n🎯 Next step: Run 'python manage.py compilemessages' to compile translations")

    return True

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Auto-translate django.po file')
    parser.add_argument('--force', action='store_true',
                       help='Retranslate even if translation exists')
    parser.add_argument('--verify-only', action='store_true',
                       help='Only show what would be translated without making changes')
    parser.add_argument('--translate-fuzzy', action='store_true',
                       help='Retranslate fuzzy (outdated) entries')

    args = parser.parse_args()

    print("🌐 ElectNepal Auto-Translation Script")
    print("="*80)
    print("This script auto-translates django.po using Google Translate API")
    print("Following the bilingual system philosophy: automatic translation, not hardcoding")
    print("="*80 + "\n")

    success = auto_translate_po_file(force=args.force, verify_only=args.verify_only, translate_fuzzy=args.translate_fuzzy)

    if success:
        sys.exit(0)
    else:
        sys.exit(1)
