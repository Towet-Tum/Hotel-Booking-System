from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from .serializers import BookingSerializer
from .models import Booking
from hotel_service.models import Inventory
from payment_service.models import Payment
from payment_service.views import create_paypal_payment  # Returns approval_url with payment
from django.db import transaction
from django.db.models import F
from datetime import timedelta
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser

def reserve_rooms(hotel_id, room_type_id, start_date, end_date, rooms_requested):
    """
    Reserve rooms by increasing booked_count on each day between start_date and end_date.
    Returns a list of dates (as strings) for which rooms were reserved.
    """
    reserved_dates = []
    current_date = start_date
    while current_date < end_date:
        with transaction.atomic():
            try:
                inventory = Inventory.objects.select_for_update().get(
                    hotel_id=hotel_id,
                    room_type_id=room_type_id,
                    date=current_date
                )
            except Inventory.DoesNotExist:
                raise ValidationError(f"No inventory record found for {current_date}.")
            
            if inventory.available_count < rooms_requested:
                raise ValidationError(f"Not enough rooms available for {current_date}.")
            
            inventory.booked_count = F('booked_count') + rooms_requested
            inventory.available_count = F('available_count') - rooms_requested
            inventory.save()
            # Refresh to get updated values
            inventory.refresh_from_db()
            reserved_dates.append(current_date.isoformat())
        current_date += timedelta(days=1)
    return reserved_dates

def release_rooms(hotel_id, room_type_id, start_date, end_date, rooms_requested):
    """
    Release reserved rooms by decrementing booked_count for each day in the range.
    """
    current_date = start_date
    while current_date < end_date:
        with transaction.atomic():
            try:
                inventory = Inventory.objects.select_for_update().get(
                    hotel_id=hotel_id,
                    room_type_id=room_type_id,
                    date=current_date
                )
            except Inventory.DoesNotExist:
                # If there's no record, skip this day.
                current_date += timedelta(days=1)
                continue
            inventory.booked_count = F('booked_count') - rooms_requested
            inventory.available_count = F('available_count') + rooms_requested
            if inventory.booked_count < 0:
                raise ValidationError(f"Booked count cannot be negative for {current_date}.")
            if inventory.available_count < 0:
                raise ValidationError(f"Available count cannot be negative for {current_date}.")
            # Save the inventory record
            inventory.save()
            inventory.refresh_from_db()
        current_date += timedelta(days=1)

class BookingValidationMixin:
    """
    Mixin to validate booking dates.
    """
    def validate_booking_dates(self, checkin, checkout):
        if checkin is None or checkout is None:
            raise ValidationError("Both check-in and check-out dates must be provided.")
        today = timezone.now().date()
        if checkin >= checkout:
            raise ValidationError("Check-in date must be before the check-out date.")
        if checkin < today:
            raise ValidationError("Check-in date must be in the future.")
    
    def can_modify_booking(self, booking):
        """
        Check if the booking can be modified or canceled.
        """
        today = timezone.now().date()
        if (booking.check_in_date - today).days < 3:
            raise ValidationError("Bookings can only be modified or canceled at least 3 days before the check-in date.")

class BookingListCreate(BookingValidationMixin, generics.GenericAPIView):
    queryset = Booking.objects.all()  # required for GenericAPIView
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]  # Adjust as needed

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        checkin = serializer.validated_data.get('check_in_date')
        checkout = serializer.validated_data.get('check_out_date')
        self.validate_booking_dates(checkin, checkout)
        
        # Assume 'total_rooms' is provided in the booking data.
        total_rooms = serializer.validated_data.get('total_rooms', 1)
        
        # Get the hotel and room_type objects and convert them to IDs.
        hotel_obj = serializer.validated_data.get('hotel')
        room_type_obj = serializer.validated_data.get('room_type')
        if not hotel_obj or not room_type_obj:
            raise ValidationError("Hotel and RoomType must be provided.")
        hotel_id = hotel_obj.hotel_id
        room_type_id = room_type_obj.room_type_id

        # Reserve rooms for each day between check-in and check-out.
        reserved_dates = reserve_rooms(hotel_id, room_type_id, checkin, checkout, total_rooms)

        # Create a temporary Booking instance to compute the total amount.
        temp_booking = Booking(**serializer.validated_data)
        computed_total = temp_booking.computed_total_amount
        
        # Initiate the PayPal payment and retrieve the approval URL.
        _, approval_url = create_paypal_payment(amount=computed_total)
        
        # Store the validated booking data along with computed_total and reservation details in the session.
        pending_booking = serializer.validated_data.copy()
        pending_booking['user'] = pending_booking['user'].id
        pending_booking['hotel'] = hotel_id
        pending_booking['room_type'] = room_type_id
        pending_booking['rate'] = pending_booking['rate'].rate_id
        pending_booking['total_amount'] = str(computed_total)
        pending_booking['reserved_dates'] = reserved_dates
        
        request.session['pending_booking'] = pending_booking
            
        return Response({
            'approval_url': approval_url,
            'message': 'Please complete the payment to finalize your booking.'
        }, status=status.HTTP_201_CREATED)

class BookingRetrieveUpdateDestroy(BookingValidationMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]  # Adjust as needed

    def perform_update(self, serializer):
        booking = self.get_object()
        self.can_modify_booking(booking)
        checkin = serializer.validated_data.get('check_in_date', booking.check_in_date)
        checkout = serializer.validated_data.get('check_out_date', booking.check_out_date)
        self.validate_booking_dates(checkin, checkout)
        serializer.save()
        
    def perform_destroy(self, instance):
        self.can_modify_booking(instance)
        instance.delete()

class BookingPaymentConfirm(generics.GenericAPIView):
    """
    Finalizes the booking after payment is confirmed.
    This view should be set as the PayPal return URL.
    """
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]  # Adjust as needed
    authentication_classes = []  # Adjust as needed

    def get(self, request, *args, **kwargs):
        # Retrieve PayPal parameters from the request
        payment_id = request.GET.get('paymentId')
        token = request.GET.get('token')
        payer_id = request.GET.get('PayerID')

        if not all([payment_id, token, payer_id]):
            return Response({"error": "Missing PayPal payment details."}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve the pending booking from the session
        pending_booking = request.session.get('pending_booking')
        if not pending_booking:
            return Response({"error": "No pending booking found."}, status=status.HTTP_400_BAD_REQUEST)

        # Finalize booking by updating its status to 'confirmed'
        pending_booking['status'] = "confirmed"
        serializer = self.get_serializer(data=pending_booking)
        serializer.is_valid(raise_exception=True)
        booking = serializer.save()

        # Create a Payment record associated with the booking
        Payment.objects.create(
            booking=booking,
            payment_id=payment_id,
            token=token,
            payer_id=payer_id,
            amount=booking.total_amount,
            status='Completed'  # Adjust as needed
        )

        # Clear the pending booking from the session
        del request.session['pending_booking']

        return Response({
            "message": "Booking confirmed and payment recorded.",
            "booking": serializer.data
        }, status=status.HTTP_201_CREATED)
        

class BookingCancel(generics.GenericAPIView):
    """
    Cancels a booking and releases reserved rooms.
    """
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]  # Adjust as needed

    def post(self, request, *args, **kwargs):
        booking_id = kwargs.get('pk')
        try:
            booking = Booking.objects.get(pk=booking_id)
        except Booking.DoesNotExist:
            return Response({"error": "Booking not found."}, status=status.HTTP_404_NOT_FOUND)

        # Ensure the booking can be canceled
        self.can_modify_booking(booking)

        # Release the reserved rooms
        release_rooms(
            hotel_id=booking.hotel.hotel_id,
            room_type_id=booking.room_type.room_type_id,
            start_date=booking.check_in_date,
            end_date=booking.check_out_date,
            rooms_requested=booking.total_rooms
        )

        # Update the booking status to 'canceled'
        booking.status = 'canceled'
        booking.save()

        return Response({
            "message": "Booking has been canceled successfully.",
            "booking_id": booking_id
        }, status=status.HTTP_200_OK)