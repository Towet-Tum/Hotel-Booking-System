
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/hotels/', include('hotel_service.urls')),
    path('api/bookings/', include('booking_service.urls')),
    path('api/payments/', include('payment_service.urls')),
    path('api/users/', include('users.urls')),
]
