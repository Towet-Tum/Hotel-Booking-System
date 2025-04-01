from django.contrib import admin
from .models import Hotel, RoomType, Room, Amenity, HotelAmenity, RoomRate, Inventory

@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'state', 'country', 'created_at', 'updated_at')
    search_fields = ('name', 'city', 'state', 'country')
    list_filter = ('state', 'country')
    ordering = ('-created_at',)

@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at', 'updated_at')
    search_fields = ('name',)
    ordering = ('-created_at',)

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('room_type', 'capacity', 'base_price', 'created_at', 'updated_at')
    search_fields = ('room_number',)
    list_filter = ('room_type',)
    ordering = ('-created_at',)

@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at', 'updated_at')
    search_fields = ('name',)
    ordering = ('-created_at',)

@admin.register(HotelAmenity)
class HotelAmenityAdmin(admin.ModelAdmin):
    list_display = ('hotel', 'amenity', 'created_at', 'updated_at')
    search_fields = ('hotel__name', 'amenity__name')
    ordering = ('-created_at',)

@admin.register(RoomRate)
class RoomRateAdmin(admin.ModelAdmin):
    list_display = ('room_type', 'rate_date', 'price', 'currency', 'created_at', 'updated_at')
    search_fields = ('room_type__name',)
    list_filter = ('rate_date', 'room_type')
    ordering = ('-created_at',)

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('hotel_id', 'room_type_id', 'date', 'total_count', 'booked_count', 'available_count')
    search_fields = ('hotel_id', 'room_type_id')
    list_filter = ('date',)
    ordering = ('-date',)
    list_per_page = 20
