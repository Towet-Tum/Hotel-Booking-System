from django.urls import path
from .views import BookingListCreate, BookingRetrieveUpdateDestroy, BookingCancel, BookingPaymentConfirm

urlpatterns = [
    path('bookings/', BookingListCreate.as_view(), name='booking-list-create'),
    path('bookings/<int:pk>/', BookingRetrieveUpdateDestroy.as_view(), name='booking-detail'),
    path('booking/cancel/<int:pk>/', BookingCancel.as_view(), name='booking-cancel'),
    path('booking/payment-confirm/', BookingPaymentConfirm.as_view(), name='booking-payment-confirm'),

    
]
