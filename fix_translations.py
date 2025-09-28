#!/usr/bin/env python
"""
Script to fix missing translations in the Nepali .po file
This script:
1. Removes fuzzy markers
2. Translates empty msgstr entries
3. Preserves existing translations
"""

import polib
from googletrans import Translator
import time
import re

def clean_and_translate_po():
    """Clean fuzzy translations and fill in missing ones."""

    # Load the .po file
    po_file_path = 'locale/ne/LC_MESSAGES/django.po'
    po = polib.pofile(po_file_path)

    translator = Translator()

    # Track statistics
    fuzzy_count = 0
    empty_count = 0
    translated_count = 0

    print(f"Processing {len(po)} entries...")

    for entry in po:
        # Skip the header entry
        if not entry.msgid:
            continue

        # Remove fuzzy flag if present
        if 'fuzzy' in entry.flags:
            entry.flags.remove('fuzzy')
            fuzzy_count += 1
            print(f"Removed fuzzy flag from: {entry.msgid[:50]}...")

        # Translate if msgstr is empty
        if not entry.msgstr or entry.msgstr.strip() == "":
            empty_count += 1

            try:
                # Small delay to avoid rate limiting
                time.sleep(0.1)

                # Translate the text
                result = translator.translate(entry.msgid, src='en', dest='ne')
                if result and result.text:
                    entry.msgstr = result.text
                    translated_count += 1
                    print(f"Translated: '{entry.msgid[:50]}...' -> '{entry.msgstr[:50]}...'")
                else:
                    print(f"Failed to translate: {entry.msgid[:50]}...")

            except Exception as e:
                print(f"Error translating '{entry.msgid[:50]}...': {str(e)}")
                # For common UI terms, use fallback translations
                fallback = get_fallback_translation(entry.msgid)
                if fallback:
                    entry.msgstr = fallback
                    translated_count += 1
                    print(f"Used fallback for: {entry.msgid[:50]}...")

    # Save the updated .po file
    po.save()
    print(f"\n✅ Translation fixes complete!")
    print(f"   - Fuzzy flags removed: {fuzzy_count}")
    print(f"   - Empty translations found: {empty_count}")
    print(f"   - Successfully translated: {translated_count}")
    print(f"\nSaved to: {po_file_path}")

    return True

def get_fallback_translation(text):
    """Provide fallback translations for common terms."""

    fallbacks = {
        "Page": "पृष्ठ",
        "of": "को",
        "Event Title (English)": "कार्यक्रम शीर्षक (अंग्रेजी)",
        "Event Description (English)": "कार्यक्रम विवरण (अंग्रेजी)",
        "Event Date & Time": "कार्यक्रम मिति र समय",
        "Must be a future date": "भविष्यको मिति हुनुपर्छ",
        "Location (English)": "स्थान (अंग्रेजी)",
        "Post Title (English)": "पोस्ट शीर्षक (अंग्रेजी)",
        "Post Content (English)": "पोस्ट सामग्री (अंग्रेजी)",
        "Current photo": "हालको तस्बिर",
        "Save Changes": "परिवर्तनहरू सुरक्षित गर्नुहोस्",
        "Online Presence": "अनलाइन उपस्थिति",
        "Announce your campaign events, rallies, and meetings to inform voters.": "मतदाताहरूलाई जानकारी दिन आफ्नो अभियान कार्यक्रम, र्यालीहरू र बैठकहरू घोषणा गर्नुहोस्।",
        "Describe the event, agenda, and what voters can expect": "कार्यक्रम, एजेन्डा र मतदाताहरूले के अपेक्षा गर्न सक्छन् वर्णन गर्नुहोस्",
        "Published events will be visible on your profile": "प्रकाशित कार्यक्रमहरू तपाईंको प्रोफाइलमा देखिनेछन्",
        "Share updates about your campaign with voters. Posts will be visible on your profile page.": "मतदाताहरूसँग आफ्नो अभियानको बारेमा अपडेटहरू साझा गर्नुहोस्। पोस्टहरू तपाईंको प्रोफाइल पृष्ठमा देखिनेछन्।",
        "Write your campaign update, announcement, or message to voters": "मतदाताहरूलाई आफ्नो अभियान अपडेट, घोषणा वा सन्देश लेख्नुहोस्",
        "Uncheck to save as draft": "मस्यौदाको रूपमा बचत गर्न अनचेक गर्नुहोस्"
    }

    return fallbacks.get(text, None)

if __name__ == "__main__":
    clean_and_translate_po()