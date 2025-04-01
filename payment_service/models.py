# payment/models.py
from django.db import models
from booking_service.models import Booking
from django.contrib.auth.models import User
from booking_service.models import Booking



class Payment(models.Model):
    id = models.AutoField(primary_key=True)  # Default primary key
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100, unique=True)
    token = models.CharField(max_length=255)
    payer_id = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Payment for {self.payment_id} with amount {self.amount}"

