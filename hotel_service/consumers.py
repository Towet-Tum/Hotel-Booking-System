import json
import logging
from confluent_kafka import Consumer, KafkaError
from datetime import date
from django.db import transaction
from .models import RoomInventory

logger = logging.getLogger(__name__)



def update_inventory_from_event(event, inventory_date=None):
    """
    Update the inventory count based on a Kafka event for room creation or deletion.

    Parameters:
        event (dict): Kafka event containing the event_type and data.
            Expected data keys include:
              - 'room_type_id': The ID of the room type.
              - 'hotel_id': The ID of the hotel.
        inventory_date (date, optional): The date for which to update inventory. Defaults to today.

    This function updates the RoomInventory record (tracked by hotel and room type)
    by either incrementing or decrementing the counts based on the event_type.
    """
    if inventory_date is None:
        inventory_date = date.today()

    event_type = event.get('event_type')
    data = event.get('data', {})
    
    # Extract necessary fields from the event data.
    room_type_id = data.get('room_type_id')
    hotel_id = data.get('hotel_id')

    # Ensure we have the required data.
    if not room_type_id or not hotel_id:
        # Log error or return if necessary data is missing.
        return

    # Determine the operation type based on event_type.
    operation = None
    if event_type == 'created':
        operation = 'increment'
    elif event_type == 'deleted':
        operation = 'decrement'
    else:
        # Optionally, handle update or other event types.
        return

    with transaction.atomic():
        inventory, created = RoomInventory.objects.get_or_create(
            hotel_id=hotel_id,
            room_type_id=room_type_id,
            inventory_date=inventory_date,
            defaults={
                'total_count': 1 if operation == 'increment' else 0,
                'booked_count': 0,
                'available_count': 1 if operation == 'increment' else 0,
            }
        )
        
        # If the record already exists, update the counts.
        if not created:
            if operation == 'increment':
                inventory.total_count += 1
                inventory.available_count += 1
            elif operation == 'decrement':
                inventory.total_count = max(inventory.total_count - 1, 0)
                inventory.available_count = max(inventory.available_count - 1, 0)
            inventory.save()
            
            
# Kafka Consumer Configuration
consumer_config = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'room-inventory-group',
    'auto.offset.reset': 'earliest',
}
consumer = Consumer(consumer_config)
consumer.subscribe(['room_events'])

def consume_room_events():
    """
    Continuously listen for room events and process them.
    """
    try:
        while True:
            msg = consumer.poll(1.0)  # Adjust the timeout as needed
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    logger.error(msg.error())
                    break

            event = json.loads(msg.value().decode('utf-8'))
            update_inventory_from_event(event)

    except Exception as e:
        logger.exception(f"Error consuming room events: {e}")
    finally:
        consumer.close()
