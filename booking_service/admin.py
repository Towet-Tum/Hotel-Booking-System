from django.contrib import admin
from .models import Booking
# Register your models here.
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_id', 'user', 'hotel', 'room_type', 'total_rooms', 'check_in_date', 'check_out_date', 'status', 'booking_date', 'total_amount')
    list_filter = ('status', 'booking_date')
    search_fields = ('user__username', 'hotel__name', 'room_type__name')
    date_hierarchy = 'booking_date'
    ordering = ('-booking_date',)