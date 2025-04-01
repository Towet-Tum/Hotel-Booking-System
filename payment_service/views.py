# payment_service/views.py
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.exceptions import ValidationError
from .models import Payment
from .serializers import PaymentSerializer
import paypalrestsdk
from dotenv import load_dotenv
import os
load_dotenv()
# Configure PayPal SDK
paypalrestsdk.configure({
    "mode": os.getenv('MODE'),  # "sandbox" or "live"
    "client_id": os.getenv('CLIENT_ID'),
    "client_secret": os.getenv('CLIENT_SECRET'),
      
})

def create_paypal_payment(amount, currency="USD", description="Payment for booking"):
    """
    Create a PayPal payment and return a tuple (payment, approval_url).
    Raises a ValidationError if the payment creation fails or the approval URL cannot be found.
    """
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {"payment_method": "paypal"},
        "transactions": [{
            "amount": {"total": f"{amount:.2f}", "currency": currency},
            "description": description
        }],
        "redirect_urls": {
            
             "return_url": "https://5ace-41-90-70-18.ngrok-free.app/payments/payment/success/",
            "cancel_url": "https://5ace-41-90-70-18.ngrok-free.app/payments/payment/cancel/"



        }
    })

    if payment.create():
        approval_url = next(
            (link.href for link in payment.links if link.rel == "approval_url"),
            None
        )
        if approval_url is None:
            raise ValidationError("Could not retrieve approval URL from PayPal.")
        return payment, approval_url
    else:
        raise ValidationError(f"PayPal payment creation failed: {payment.error}")

class PaymentListCreate(generics.ListCreateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer 
    #permission_classes = [IsAuthenticated]  # Adjust as needed
    #authentication_classes = []  # Adjust as needed
       
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        booking = serializer.validated_data.get('booking')
        # Save Payment record using the booking's total_amount.
        payment_instance = serializer.save(user=request.user, amount=booking.total_amount)
        
        # Initiate the PayPal payment and retrieve the approval URL.
        _, approval_url = create_paypal_payment(amount=booking.total_amount)
        
        response_data = serializer.data
        response_data['approval_url'] = approval_url
        return Response(response_data, status=status.HTTP_201_CREATED)
