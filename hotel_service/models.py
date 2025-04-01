# hotels/models.py
from django.db import models

class Hotel(models.Model):
    hotel_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['city']),
            models.Index(fields=['state']),
            models.Index(fields=['country']),
        ]
    def __str__(self):
        return self.name
class RoomType(models.Model):
    ROOM_TYPE_CHOICES = [
        ('standard', 'Standard'),
        ('suite', 'Suite'),
        ('deluxe', 'Deluxe'),
    ]
    room_type_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, choices=ROOM_TYPE_CHOICES, default='standard')
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['name']),
        ]
    def __str__(self):
        return self.name
    
    
    

class Room(models.Model):
    room_id = models.AutoField(primary_key=True)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='room_types')
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, related_name='rooms')
    room_number = models.IntegerField(default=0)
    description = models.TextField(blank=True, null=True)
    capacity = models.PositiveIntegerField()
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
   
    class Meta:
        indexes = [
            models.Index(fields=['capacity']),
            models.Index(fields=['room_type']),
        ]
    def __str__(self):
        return self.room_type.name


class Amenity(models.Model):
    amenity_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['name']),
        ]
    def __str__(self):
        return self.name

class HotelAmenity(models.Model):
    hotel_amenity_id = models.AutoField(primary_key=True)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='hotel_amenities')
    amenity = models.ForeignKey(Amenity, on_delete=models.CASCADE, related_name='amenity_hotels')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        indexes = [
            models.Index(fields=['hotel']),
            models.Index(fields=['amenity']),
        ]
    def __str__(self):
        return f'{self.hotel.name} - {self.amenity.name}'

class RoomRate(models.Model):
    rate_id = models.AutoField(primary_key=True)
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, related_name='rates')
    rate_date = models.DateField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='USD')
    promotion_code = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
   
    class Meta:
        indexes = [
            models.Index(fields=['rate_date']),
            models.Index(fields=['room_type']),
        ]
    def __str__(self):
        return f'{self.room_type} - {self.rate_date}'
    

class Inventory(models.Model):
    """
    Inventory model to track room availability by hotel and room type on a given date.
    """
    
    hotel_id = models.PositiveIntegerField(help_text="ID from the Hotel service")
    room_type_id = models.PositiveIntegerField(help_text="ID from the RoomType service")
    date = models.DateField()
    total_count = models.PositiveIntegerField()
    booked_count = models.PositiveIntegerField(default=0)
    available_count = models.PositiveIntegerField(editable=False)

    class Meta:
        unique_together = (('hotel_id', 'room_type_id', 'date'),)
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['hotel_id']),
            models.Index(fields=['room_type_id']),
        ]

    def __str__(self):
        return f"Hotel {self.hotel_id} - Room Type {self.room_type_id} on {self.date}"