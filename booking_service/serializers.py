from rest_framework import serializers
from .models import Booking
from hotel_service.models import Hotel, RoomType, RoomRate
from datetime import date

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ['total_amount', 'created_at', 'updated_at', 'status']
        extra_kwargs = {
            'user': {'write_only': True},
            'hotel': {'write_only': True},
            'room_type': {'write_only': True},
            'rate': {'write_only': True},
        }
        
    
