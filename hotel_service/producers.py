import json
import logging
from confluent_kafka import Producer
from django.conf import settings

logger = logging.getLogger(__name__)

# Kafka Producer Configuration
producer_config = {
    'bootstrap.servers': 'localhost:9092',
    'client.id': 'hotel-management-system'
}
producer = Producer(producer_config)

def delivery_report(err, msg):
    """Callback for Kafka delivery reports."""
    if err is not None:
        logger.error("Message delivery failed: %s", err)
    else:
        logger.info("Message delivered to %s [%s] at offset %s",
                    msg.topic(), msg.partition(), msg.offset())

def produce_event(topic, key, value):
    """
    Produce a Kafka event.
    
    :param topic: Kafka topic name.
    :param key: Key for the Kafka message.
    :param value: Value for the Kafka message (dictionary).
    """
    try:
        message = json.dumps(value)
        producer.produce(
            topic=topic,
            key=key,
            value=message,
            callback=delivery_report
        )
        # Poll for events; this will trigger delivery report callbacks.
        producer.poll(0)
    except Exception as e:
        logger.exception("Failed to produce message: %s", e)

def flush_producer():
    """
    Flush the Kafka producer.
    This should be called periodically or at the end of a batch/request.
    """
    producer.flush()

def produce_hotel_event(event_type, hotel_instance):
    """
    Produce an event for Hotel model CRUD operations.
    
    :param event_type: Type of event (created, updated, deleted).
    :param hotel_instance: Hotel model instance.
    """
    event = {
        'event_type': event_type,
        'model': 'Hotel',
        'data': {
            'id': hotel_instance.hotel_id,
            'name': hotel_instance.name,
            'address': hotel_instance.address,
            'city': hotel_instance.city,
            'state': hotel_instance.state,
            'country': hotel_instance.country,
            'zip_code': hotel_instance.zip_code,
            # Use getattr in case field name differs (e.g., phone vs phone_number)
            'phone_number': getattr(hotel_instance, 'phone_number', None),
            'email': hotel_instance.email,
            'created_at': hotel_instance.created_at.isoformat(),
            'updated_at': hotel_instance.updated_at.isoformat(),
        }
    }
    produce_event('hotel_events', str(hotel_instance.hotel_id), event)
    

def produce_room_event(event_type, room_instance):
    """
    Produce an event for Room model CRUD operations.
    
    :param event_type: Type of event (created, updated, deleted).
    :param room_instance: Room model instance.
    """
    event = {
        'event_type': event_type,
        'model': 'Room',
        'data': {
            'id': room_instance.room_id,
            'hotel_id': room_instance.hotel.hotel_id,
            'room_type_id': room_instance.room_type.room_type_id,
            'room_number': room_instance.room_number,
            'capacity': room_instance.capacity,
            'base_price': str(room_instance.base_price),
            'created_at': room_instance.created_at.isoformat(),
            'updated_at': room_instance.updated_at.isoformat(),
        }
    }
    produce_event('room_events', str(room_instance.room_id), event)


def produce_room_type_event(event_type, room_type_instance):
    """
    Produce an event for RoomType model CRUD operations.
    
    :param event_type: Type of event (created, updated, deleted).
    :param room_type_instance: RoomType model instance.
    """
    event = {
        'event_type': event_type,
        'model': 'RoomType',
        'data': {
            'id': room_type_instance.room_type_id,
            'name': room_type_instance.name,
            'description': room_type_instance.description,
            'created_at': room_type_instance.created_at.isoformat(),
            'updated_at': room_type_instance.updated_at.isoformat(),
        }
    }
    produce_event('room_type_events', str(room_type_instance.room_type_id), event)

def produce_room_rate_event(event_type, room_rate_instance):
    """
    Produce an event for RoomRate model CRUD operations.
    
    :param event_type: Type of event (created, updated, deleted).
    :param room_rate_instance: RoomRate model instance.
    """
    event = {
        'event_type': event_type,
        'model': 'RoomRate',
        'data': {
            'id': room_rate_instance.rate_id,
            'room_type_id': room_rate_instance.room_type.id,
            'rate': str(room_rate_instance.rate),
            'start_date': room_rate_instance.start_date.isoformat(),
            'end_date': room_rate_instance.end_date.isoformat(),
            'created_at': room_rate_instance.created_at.isoformat(),
            'updated_at': room_rate_instance.updated_at.isoformat(),
        }
    }
    produce_event('room_rate_events', str(room_rate_instance.id), event)

def produce_amenity_event(event_type, amenity_instance):
    """
    Produce an event for Amenity model CRUD operations.
    
    :param event_type: Type of event (created, updated, deleted).
    :param amenity_instance: Amenity model instance.
    """
    event = {
        'event_type': event_type,
        'model': 'Amenity',
        'data': {
            'id': amenity_instance.amenity_id,
            'name': amenity_instance.name,
            'description': amenity_instance.description,
            'created_at': amenity_instance.created_at.isoformat(),
            'updated_at': amenity_instance.updated_at.isoformat(),
        }
    }
    produce_event('amenity_events', str(amenity_instance.amenity_id), event)

def produce_hotel_amenity_event(event_type, hotel_amenity_instance):
    """
    Produce an event for HotelAmenity model CRUD operations.
    
    :param event_type: Type of event (created, updated, deleted).
    :param hotel_amenity_instance: HotelAmenity model instance.
    """
    event = {
        'event_type': event_type,
        'model': 'HotelAmenity',
        'data': {
            'id': hotel_amenity_instance.hotel_amenity_id,
            'hotel_id': hotel_amenity_instance.hotel.hotel_id,
            'amenity_id': hotel_amenity_instance.amenity.amenity_id,
            'created_at': hotel_amenity_instance.created_at.isoformat(),
            'updated_at': hotel_amenity_instance.updated_at.isoformat(),
        }
    }
    produce_event('hotel_amenity_events', str(hotel_amenity_instance.hotel_amenity_id), event)

def produce_room_inventory_event(event_type, room_inventory_instance):
    """
    Produce an event for RoomInventory model CRUD operations.
    
    :param event_type: Type of event (created, updated, deleted).
    :param room_inventory_instance: RoomInventory model instance.
    """
    event = {
        'event_type': event_type,
        'model': 'RoomInventory',
        'data': {
            'id': room_inventory_instance.inventory_id,
            'hotel_id': room_inventory_instance.hotel.hotel_id,
            'room_id': room_inventory_instance.room.room_id,
            'inventory_date': room_inventory_instance.inventory_date.isoformat(),
            'total_count': room_inventory_instance.total_count,
            'booked_count': room_inventory_instance.booked_count,
            'available_count': room_inventory_instance.available_count,
            'last_updated': room_inventory_instance.last_updated.isoformat(),
        }
    }
    produce_event('room_inventory_events', str(room_inventory_instance.inventory_id), event)