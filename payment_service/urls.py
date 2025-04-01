from django.urls import path
from .views import PaymentListCreate
from booking_service.views import BookingPaymentConfirm, BookingCancel
urlpatterns = [
    path('payments/', PaymentListCreate.as_view(), name='payment-list-create'),
    path('payment/success/', BookingPaymentConfirm.as_view(), name='payment_success'),
    path('payment/cancel/', BookingCancel.as_view(), name='payment_cancel'),
    
]

