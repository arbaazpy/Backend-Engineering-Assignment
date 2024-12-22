from django.apps import AppConfig


class CoreConfig(AppConfig):
    """
    Configuration class for the 'core' app.

    Ensures that signals are imported and ready when the app is loaded.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        """
        Import signal handlers when the app is ready.
        """
        import core.signals  # Import signals to activate them
