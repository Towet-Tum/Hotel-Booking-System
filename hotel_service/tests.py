from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.core.cache import cache
from datetime import date
from .models import Hotel, RoomType, Inventory
from django.contrib.auth import get_user_model

User = get_user_model()

class HotelListCreateAPIViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="testpassword", email="testuser@gmail.com")
        self.client.force_authenticate(user=self.user)  # Authenticate the client
        self.hotel_data = {
            "name": "Test Hotel",
            "address": "123 Test Street",
            "city": "Test City",
            "state": "Test State",
            "zip_code": "12345",
            "country": "Test Country",
            "description": "A test hotel",
            "phone": "1234567890",
            "email": "testhotel@example.com",
        }
        self.hotel = Hotel.objects.create(**self.hotel_data)
        self.url = reverse("hotel-list-create")

    def test_get_hotel_list(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), Hotel.objects.count())

    def test_create_hotel(self):
        response = self.client.post(self.url, self.hotel_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Hotel.objects.count(), 2)


class HotelRetrieveUpdateDestroyAPIViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="testpassword", email="testuser@gmail.com")
        self.client.force_authenticate(user=self.user)  # Authenticate the client
        self.hotel = Hotel.objects.create(
            name="Test Hotel",
            address="123 Test Street",
            city="Test City",
            state="Test State",
            zip_code="12345",
            country="Test Country",
            description="A test hotel",
            phone="1234567890",
            email="testhotel@example.com",
        )
        self.url = reverse("hotel-detail", kwargs={"pk": self.hotel.hotel_id})

    def test_get_hotel(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.hotel.name)

    def test_update_hotel(self):
        updated_data = {
            "name": "Updated Hotel",
            "address": "456 Updated Street",
            "city": "Updated City",
            "state": "Updated State",
            "zip_code": "67890",
            "country": "Updated Country",
            "description": "An updated test hotel",
            "phone": "0987654321",
            "email": "updatedhotel@example.com",
        }
        response = self.client.put(self.url, updated_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.hotel.refresh_from_db()
        self.assertEqual(self.hotel.name, updated_data["name"])

    def test_delete_hotel(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Hotel.objects.count(), 0)

    def test_cache_behavior(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        cached_data = cache.get(f"hotel_{self.hotel.hotel_id}")
        self.assertIsNotNone(cached_data)

        updated_data = {
            "name": "Updated Hotel",
            "address": "456 Updated Street",
            "city": "Updated City",
            "state": "Updated State",
            "zip_code": "67890",
            "country": "Updated Country",
            "description": "An updated test hotel",
            "phone": "0987654321",
            "email": "updatedhotel@example.com",
        }
        self.client.put(self.url, updated_data)
        self.assertIsNone(cache.get(f"hotel_{self.hotel.hotel_id}"))

        self.client.delete(self.url)
        self.assertIsNone(cache.get(f"hotel_{self.hotel.hotel_id}"))


class InventorySummaryViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="testpassword", email="testuser@gmail.com")
        self.client.force_authenticate(user=self.user)  # Authenticate the client

        # Create a Hotel instance
        self.hotel = Hotel.objects.create(
            name="Test Hotel",
            address="123 Test Street",
            city="Test City",
            state="Test State",
            zip_code="12345",
            country="Test Country",
            description="A test hotel",
            phone="1234567890",
            email="testhotel@example.com",
        )

        # Create a RoomType instance
        self.room_type = RoomType.objects.create(name="Deluxe")

        # Create an Inventory instance
        self.inventory = Inventory.objects.create(
            hotel_id=self.hotel.hotel_id,
            room_type_id=self.room_type.room_type_id,
            date=date.today(),
            total_count=10,
            booked_count=2,
            available_count=8,
        )

        # Define the URL for the InventorySummaryView
        self.url = reverse("inventory-summary")

    def test_get_inventory_summary(self):
        response = self.client.get(self.url, {"date": date.today().isoformat()})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.room_type.name, response.data)
        self.assertEqual(response.data[self.room_type.name]["total"], 10)
        self.assertEqual(response.data[self.room_type.name]["booked"], 2)
        self.assertEqual(response.data[self.room_type.name]["available"], 8)

    def test_invalid_date_format(self):
        response = self.client.get(self.url, {"date": "invalid-date"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)