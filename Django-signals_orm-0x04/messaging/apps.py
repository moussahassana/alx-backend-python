from django.apps import AppConfig

class MessagingConfig(AppConfig):
    """
    Application configuration for the 'messaging' app.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'messaging'

    def ready(self):
        """
        This method is called when Django starts.
        It's the recommended place to import signals.
        """
        import messaging.signals
