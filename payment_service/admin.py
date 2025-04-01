from django.contrib import admin
from .models import Payment

# Register your models here.
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'booking', 'amount', 'status', 'created_at')
    list_display_links = ('id', 'booking')
    list_editable = ('amount', 'status')
    list_per_page = 20
    list_select_related = ('booking',)
    list_approximate = ('booking',)
    search_fields = ('amount',)
    list_filter = ('created_at',)
    ordering = ('-created_at',)