from datetime import date, timedelta
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from unittest.mock import patch

from booking_service.models import Booking
from payment_service.models import Payment
from hotel_service.models import Hotel, RoomType, RoomRate

User = get_user_model()

class BookingAPITest(APITestCase):
    def setUp(self):
        # Create and authenticate a test user.
        self.user = User.objects.create_user(
            username="testuser", password="testpass", email="testuser@gmail.com")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        # Create dummy objects required by the booking process.
        self.hotel = Hotel.objects.create(hotel_id=1, name="Test Hotel")
        self.room_type = RoomType.objects.create(room_type_id=1, name="Single")
        self.rate = RoomRate.objects.create(
            rate_id=1, room_type=self.room_type, price=100, rate_date=date.today())

        # Define valid booking data.
        # Use dates far enough in the future to pass the validation (at least 3 days ahead).
        self.valid_booking_data = {
            "user": self.user.id,
            "hotel": self.hotel.hotel_id,        # Use custom PK field.
            "room_type": self.room_type.room_type_id,
            "check_in_date": (date.today() + timedelta(days=5)).isoformat(),
            "check_out_date": (date.today() + timedelta(days=7)).isoformat(),
            "total_rooms": 1,
            "rate": self.rate.rate_id,
            # include any additional fields required by your BookingSerializer
        }

    @patch('booking_service.views.reserve_rooms', return_value=['2025-03-31', '2025-04-01'])
    @patch('booking_service.views.create_paypal_payment', return_value=(None, "http://paypal.com/approval"))
    def test_booking_creation_success(self, mock_create_paypal_payment, mock_reserve_rooms):
        url = reverse('booking-list-create')
        response = self.client.post(url, data=self.valid_booking_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("approval_url", response.data)
        session = self.client.session
        self.assertIn('pending_booking', session)
        mock_reserve_rooms.assert_called_once()
        mock_create_paypal_payment.assert_called_once()

    def test_booking_creation_missing_hotel_or_room_type(self):
        data = self.valid_booking_data.copy()
        data.pop('hotel')
        data.pop('room_type')
        url = reverse('booking-list-create')
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class BookingRetrieveUpdateDestroyTest(APITestCase):
    def setUp(self):
        # Create and authenticate a test user.
        self.user = User.objects.create_user(
            username="testuser2", password="testpass", email="testuser2@gmail.com")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        # Create dummy objects.
        self.hotel = Hotel.objects.create(hotel_id=2, name="Another Hotel")
        self.room_type = RoomType.objects.create(room_type_id=2, name="Double")
        self.rate = RoomRate.objects.create(
            rate_id=2, room_type=self.room_type, price=150, rate_date=date.today())

        # Set booking dates to be at least 3 days in the future.
        check_in = date.today() + timedelta(days=5)
        check_out = date.today() + timedelta(days=7)
        self.booking = Booking.objects.create(
            user=self.user,
            hotel=self.hotel,
            room_type=self.room_type,
            check_in_date=check_in,
            check_out_date=check_out,
            total_rooms=1,
            rate=self.rate,
            status="pending"
        )
        self.url = reverse('booking-detail', kwargs={'pk': self.booking.pk})

    def test_booking_update_success(self):
        new_checkin = (date.today() + timedelta(days=6)).isoformat()
        new_checkout = (date.today() + timedelta(days=8)).isoformat()
        data = {
            "check_in_date": new_checkin,
            "check_out_date": new_checkout
        }
        response = self.client.patch(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.check_in_date.isoformat(), new_checkin)
        self.assertEqual(self.booking.check_out_date.isoformat(), new_checkout)

    def test_booking_delete_success(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(Booking.DoesNotExist):
            Booking.objects.get(pk=self.booking.pk)


class BookingPaymentConfirmTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        # Set pending booking dates far enough in the future.
        pending_checkin = (date.today() + timedelta(days=5)).isoformat()
        pending_checkout = (date.today() + timedelta(days=7)).isoformat()
        self.pending_booking = {
            "user": 1,
            "hotel": 1,
            "room_type": 1,
            "check_in_date": pending_checkin,
            "check_out_date": pending_checkout,
            "total_rooms": 1,
            "rate": 1,
            "total_amount": "200.00",
            "reserved_dates": ['2025-03-31', '2025-04-01']
        }
        session = self.client.session
        session['pending_booking'] = self.pending_booking
        session.save()

    def test_payment_confirm_missing_parameters(self):
        url = reverse('booking-payment-confirm') + "?paymentId=abc&token=def"  # Missing PayerID.
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    @patch('booking_service.views.BookingSerializer.save')
    def test_payment_confirm_success(self, mock_save):
        # Create a dummy Booking instance without passing 'id' in the constructor.
        mock_booking = Booking(total_amount="200.00")
        mock_booking.pk = 10  # Manually set the primary key.
        mock_save.return_value = mock_booking

        url = reverse('booking-payment-confirm') + "?paymentId=abc&token=def&PayerID=ghi"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("message", response.data)
        self.assertIn("booking", response.data)
        session = self.client.session
        self.assertNotIn('pending_booking', session)
        payment_exists = Payment.objects.filter(booking=mock_booking, payment_id="abc").exists()
        self.assertTrue(payment_exists)


class BookingCancelTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser3", password="testpass", email="testuser3@gmail.com")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.hotel = Hotel.objects.create(hotel_id=3, name="Cancel Hotel")
        self.room_type = RoomType.objects.create(room_type_id=3, name="Suite")
        self.rate = RoomRate.objects.create(
            rate_id=3, room_type=self.room_type, price=250, rate_date=date.today())

        # Set booking dates to be at least 3 days in the future.
        check_in = date.today() + timedelta(days=5)
        check_out = date.today() + timedelta(days=7)
        self.booking = Booking.objects.create(
            user=self.user,
            hotel=self.hotel,
            room_type=self.room_type,
            check_in_date=check_in,
            check_out_date=check_out,
            total_rooms=1,
            rate=self.rate,
            status="pending"
        )
        self.url = reverse('booking-cancel', kwargs={'pk': self.booking.pk})
        # Patch can_modify_booking to bypass its restrictions if necessary.
        from booking_service.views import BookingCancel
        BookingCancel.can_modify_booking = lambda self, booking: None

    @patch('booking_service.views.release_rooms')
    def test_booking_cancel_success(self, mock_release_rooms):
        response = self.client.post(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, 'canceled')
        mock_release_rooms.assert_called_once_with(
            hotel_id=self.booking.hotel.hotel_id,
            room_type_id=self.booking.room_type.room_type_id,
            start_date=self.booking.check_in_date,
            end_date=self.booking.check_out_date,
            rooms_requested=self.booking.total_rooms
        )

    def test_booking_cancel_not_found(self):
        url = reverse('booking-cancel', kwargs={'pk': 9999})
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
