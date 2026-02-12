from django.apps import AppConfig


class EventManagerConfig(AppConfig):
        default_auto_field = 'django.db.models.BigAutoField'
        name = 'event_manager'

        def ready(self):
                import event_manager.signals
