# booking/models.py
from django.db import models
from hotel_service.models import Hotel, RoomType, RoomRate
from decimal import Decimal
from django.conf import settings

class Booking(models.Model):
    booking_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='bookings')
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, related_name='bookings')
    total_rooms = models.PositiveIntegerField()
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    # Optionally record the rate used at booking time.
    rate = models.ForeignKey(RoomRate, on_delete=models.SET_NULL, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=50,
        choices=(
            ('pending', 'Pending'),
            ('confirmed', 'Confirmed'),
            ('cancelled', 'Cancelled'),
        ),
        default='pending',
        help_text="Booking status"
    )
    booking_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return (
            f"Booking ID: {self.booking_id}, User: {self.user.username}, "
            f"Hotel: {self.hotel.name}, Room Type: {self.room_type.name}, "
            f"Check-in: {self.check_in_date}, Check-out: {self.check_out_date}, "
            f"Status: {self.status}"
        )

    @property
    def computed_total_amount(self):
        """
        Calculate the total amount for the booking.
        
        The total is computed as:
            total_rooms * number_of_nights * room_rate
        
        Assumes that the RoomRate model has a 'price' field.
        If check_out_date is not after check_in_date, it defaults to 1 night.
        """
        if self.rate and self.check_in_date and self.check_out_date:
            nights = (self.check_out_date - self.check_in_date).days
            # Ensure at least one night is counted
            nights = nights if nights > 0 else 1
            return Decimal(self.total_rooms) * self.rate.price * Decimal(nights)
        return Decimal("0.00")

    def save(self, *args, **kwargs):
        """
        Override the save method to automatically update the total_amount 
        field with the computed total amount before saving.
        """
        self.total_amount = self.computed_total_amount
        super().save(*args, **kwargs)


