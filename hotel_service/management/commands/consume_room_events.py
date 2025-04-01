from django.core.management.base import BaseCommand
from hotel_service.consumers import consume_room_events




class Command(BaseCommand):
    help = "Consumes room events from Kafka and updates room inventory accordingly."

    def handle(self, *args, **options):
        self.stdout.write("Starting Kafka consumer for room events...")
        consume_room_events()