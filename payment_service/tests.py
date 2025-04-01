# payment_service/tests.py
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch
from payment_service.models import Payment

User = get_user_model()

class DummyBooking:
    def __init__(self, total_amount):
        self.total_amount = total_amount

class PaymentListCreateTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpassword"
        )
        self.client.force_authenticate(user=self.user)
        self.url = reverse('payment-list-create')
        self.booking = DummyBooking(total_amount=100.00)

    @patch('payment_service.views.PaymentSerializer')
    def test_create_payment_success(self, mock_serializer_class):
        # Create a mock serializer instance.
        mock_serializer = mock_serializer_class.return_value
        mock_serializer.is_valid.return_value = True
        # Simulate that validated_data includes the real booking instance.
        mock_serializer.validated_data = {'booking': self.booking}
        # Create a dummy Payment instance without the 'user' field if not expected.
        dummy_payment = Payment(id=1, amount=self.booking.total_amount)
        dummy_payment.booking = self.booking
        mock_serializer.save.return_value = dummy_payment

        with patch('payment_service.views.create_paypal_payment') as mock_create_paypal_payment:
            dummy_approval_url = "https://dummy-approval.url/"
            mock_create_paypal_payment.return_value = (None, dummy_approval_url)

            response = self.client.post(self.url, data={"booking": self.booking.id}, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertIn('approval_url', response.data)
            self.assertEqual(response.data['approval_url'], dummy_approval_url)