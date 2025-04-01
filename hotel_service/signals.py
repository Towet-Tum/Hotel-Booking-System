"""from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from datetime import date, timedelta
from hotel_service.models import Inventory, Room  # Adjust the import paths as needed

@receiver(post_save, sender=Room)
def update_inventory_on_room_create(sender, instance, created, **kwargs):
    if created:
        hotel_id = instance.hotel.hotel_id
        room_type_id = instance.room_type.room_type_id
        
        # Calculate the current total number of rooms for this hotel and room type.
        total_rooms = Room.objects.filter(hotel=instance.hotel, room_type=instance.room_type).count()
        
        # Update Inventory for the next 30 days.
        start_date = date.today()
        end_date = start_date + timedelta(days=30)
        for n in range((end_date - start_date).days):
            current_date = start_date + timedelta(days=n)
            inventory, inv_created = Inventory.objects.get_or_create(
                hotel_id=hotel_id,
                room_type_id=room_type_id,
                date=current_date,
                defaults={'total_count': total_rooms, 'booked_count': 0}
            )
            if not inv_created:
                # Update the total_count to reflect the new total.
                inventory.total_count = total_rooms
                inventory.save()

@receiver(post_delete, sender=Room)
def update_inventory_on_room_delete(sender, instance, **kwargs):
    hotel_id = instance.hotel.hotel_id
    room_type_id = instance.room_type.room_type_id
    
    # Recalculate the total number of rooms after deletion.
    total_rooms = Room.objects.filter(hotel=instance.hotel, room_type=instance.room_type).count()
    
    # Update Inventory for the next 30 days.
    start_date = date.today()
    end_date = start_date + timedelta(days=30)
    for n in range((end_date - start_date).days):
        current_date = start_date + timedelta(days=n)
        try:
            inventory = Inventory.objects.get(
                hotel_id=hotel_id,
                room_type_id=room_type_id,
                date=current_date
            )
            inventory.total_count = total_rooms
            inventory.save()
        except Inventory.DoesNotExist:
            # Optionally, create a new inventory record if needed.
            pass

    """