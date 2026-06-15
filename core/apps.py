from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = 'core'

    def ready(self):
        from . import signals  # noqa: F401  (registers post_save receivers)
