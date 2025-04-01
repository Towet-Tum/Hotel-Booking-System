from django.apps import AppConfig


class HotelServiceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'hotel_service'
    
    def ready(self):
        import hotel_service.signals

