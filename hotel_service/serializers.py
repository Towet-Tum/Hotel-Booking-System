from rest_framework import serializers
from .models import Hotel, RoomType, Room, Amenity, HotelAmenity, RoomRate

class HotelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hotel
        fields = '__all__'

    def validate_zip_code(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Zip code must contain only digits.")
        return value

    def validate_phone(self, value):
        if value and not value.isdigit():
            raise serializers.ValidationError("Phone number must contain only digits.")
        return value


class RoomTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomType
        fields = '__all__'

    def validate_name(self, value):
        if value not in dict(RoomType.ROOM_TYPE_CHOICES).keys():
            raise serializers.ValidationError("Invalid room type.")
        return value


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'

    def validate_capacity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Capacity must be greater than zero.")
        return value

    def validate_base_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Base price must be greater than zero.")
        return value


class AmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenity
        fields = '__all__'


class HotelAmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = HotelAmenity
        fields = '__all__'


class RoomRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomRate
        fields = '__all__'

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero.")
        return value


