import logging
import json
from confluent_kafka import Producer
from django.conf import settings

logger = logging.getLogger(__name__)

# Kafka producer configuration. It's a good idea to configure these values in your settings.
KAFKA_PRODUCER_CONFIG = {
    'bootstrap.servers': 'localhost:9092',
    'client.id': 'inventory-producer',
    # add any other producer settings you need
}

# Create a global Kafka Producer instance.  
producer = Producer(KAFKA_PRODUCER_CONFIG)

def delivery_report(err, msg):
    """
    Callback for Kafka message delivery.
    """
    if err is not None:
        logger.error(f"Message delivery failed: {err}")
    else:
        logger.info(f"Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")

def produce_event(topic: str, key: str, event: dict):
    """
    Generic function to produce an event to a given Kafka topic.
    
    :param topic: The Kafka topic where the event will be published.
    :param key: The message key (as a string) used for partitioning.
    :param event: A dictionary containing the event data.
    """
    try:
        # Convert the event to a JSON string.
        event_data = json.dumps(event)
        producer.produce(topic=topic, key=key, value=event_data, callback=delivery_report)
        # Trigger delivery callbacks by polling.
        producer.poll(0)
    except Exception as e:
        logger.exception(f"Error producing event: {e}")

def flush_producer():
    """
    Flush all outstanding messages.
    """
    producer.flush()
    
def produce_booking_event(booking):
    """
    Produce an event for a new booking.
    
    :param booking: The booking model instance.
    """
    event = {
        'event_type': 'created',
        'booking_id': booking.booking_id,
        'user_id': booking.user_id,
        'hotel_id': booking.hotel_id,
        'room_type_id': booking.room_type_id,
        'total_rooms': booking.total_rooms,
        'check_in_date': booking.check_in_date.isoformat(),
        'check_out_date': booking.check_out_date.isoformat(),
        'total_amount': str(booking.total_amount),
        'status': booking.status,
        'booking_date': booking.booking_date.isoformat(),
    }
    produce_event('booking_events', str(booking.booking_id), event)
    flush_producer()