from django.apps import AppConfig
from django.utils.module_loading import autodiscover_modules

class HellowordConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "helloword"

    def ready(self):
        autodiscover_modules('preload.py')

