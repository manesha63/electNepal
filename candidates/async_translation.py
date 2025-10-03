"""
Async translation module to handle translations in the background
without blocking the main request-response cycle
"""

import threading
import logging
from googletrans import Translator
from django.db import connection

logger = logging.getLogger(__name__)


def translate_candidate_async(candidate_id, fields_to_translate):
    """
    Translate candidate fields asynchronously in a background thread

    Args:
        candidate_id: ID of the Candidate to translate
        fields_to_translate: List of tuples (en_field, ne_field, mt_flag_field)
    """
    def _do_translation():
        # Close the old database connection to prevent issues with threading
        connection.close()

        try:
            # Import here to avoid circular imports
            from candidates.models import Candidate

            # Fetch the candidate instance
            candidate = Candidate.objects.get(pk=candidate_id)
            translator = Translator()

            # Track if any translations were made
            translations_made = False

            for en_field, ne_field, mt_flag_field in fields_to_translate:
                en_value = getattr(candidate, en_field, "") or ""
                ne_value = getattr(candidate, ne_field, "") or ""

                # Only translate if English exists and Nepali is empty
                if en_value and not ne_value:
                    try:
                        # Translate to Nepali
                        result = translator.translate(en_value, src='en', dest='ne')
                        translated = result.text

                        # Update the candidate fields
                        setattr(candidate, ne_field, translated)
                        setattr(candidate, mt_flag_field, True)
                        translations_made = True

                        logger.info(f"Successfully translated {en_field} to Nepali for Candidate {candidate_id}")

                    except Exception as e:
                        logger.error(f"Translation failed for {en_field} (Candidate {candidate_id}): {str(e)}")
                        # On failure, copy English text as fallback
                        setattr(candidate, ne_field, en_value)
                        setattr(candidate, mt_flag_field, False)
                        translations_made = True

            # Save the candidate with translated fields if any translations were made
            if translations_made:
                # Use update() to avoid triggering save() again and to be more efficient
                update_fields = []
                update_values = {}

                for _, ne_field, mt_flag_field in fields_to_translate:
                    update_fields.extend([ne_field, mt_flag_field])
                    update_values[ne_field] = getattr(candidate, ne_field)
                    update_values[mt_flag_field] = getattr(candidate, mt_flag_field)

                # Update only the translation fields
                Candidate.objects.filter(pk=candidate_id).update(**update_values)

                logger.info(f"Async translation completed for Candidate {candidate_id}")

        except Exception as e:
            logger.error(f"Error in async translation for Candidate {candidate_id}: {str(e)}")
        finally:
            # Ensure connection is closed
            connection.close()

    # Start the translation in a background thread
    thread = threading.Thread(target=_do_translation, daemon=True)
    thread.start()

    logger.info(f"Started async translation thread for Candidate {candidate_id}")



def translate_event_async(event_id, fields_to_translate):
    """
    Translate CandidateEvent fields asynchronously

    Args:
        event_id: ID of the CandidateEvent to translate
        fields_to_translate: List of tuples (en_field, ne_field, mt_flag_field)
    """
    def _do_translation():
        connection.close()

        try:
            from candidates.models import CandidateEvent

            event = CandidateEvent.objects.get(pk=event_id)
            translator = Translator()

            translations_made = False

            for en_field, ne_field, mt_flag_field in fields_to_translate:
                en_value = getattr(event, en_field, "") or ""
                ne_value = getattr(event, ne_field, "") or ""

                if en_value and not ne_value:
                    try:
                        result = translator.translate(en_value, src='en', dest='ne')
                        translated = result.text

                        setattr(event, ne_field, translated)
                        setattr(event, mt_flag_field, True)
                        translations_made = True

                        logger.info(f"Successfully translated {en_field} for CandidateEvent {event_id}")

                    except Exception as e:
                        logger.error(f"Translation failed for {en_field} (Event {event_id}): {str(e)}")
                        setattr(event, ne_field, en_value)
                        setattr(event, mt_flag_field, False)
                        translations_made = True

            if translations_made:
                update_values = {}
                for _, ne_field, mt_flag_field in fields_to_translate:
                    update_values[ne_field] = getattr(event, ne_field)
                    update_values[mt_flag_field] = getattr(event, mt_flag_field)

                CandidateEvent.objects.filter(pk=event_id).update(**update_values)
                logger.info(f"Async translation completed for CandidateEvent {event_id}")

        except Exception as e:
            logger.error(f"Error in async translation for CandidateEvent {event_id}: {str(e)}")
        finally:
            connection.close()

    thread = threading.Thread(target=_do_translation, daemon=True)
    thread.start()

    logger.info(f"Started async translation thread for CandidateEvent {event_id}")