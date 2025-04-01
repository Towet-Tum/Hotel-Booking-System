from rest_framework import serializers
from .models import Payment
from booking_service.models import Booking
from booking_service.serializers import BookingSerializer
from users.models import CustomUser

class PaymentSerializer(serializers.ModelSerializer):
    booking = BookingSerializer()
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    
    class Meta:
        model = Payment
        fields = '__all__'
     

        