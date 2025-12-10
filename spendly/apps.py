from django.apps import AppConfig


class SpendlyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'spendly'

    def ready(self):
        import spendly.signals
