from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        """
        Load automatic translation signals when the app is ready
        """
        try:
            from . import auto_translate
        except ImportError:
            pass
