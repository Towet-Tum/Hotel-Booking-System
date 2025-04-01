from django.test import TestCase

# Create your tests here.
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from users.models import Profile
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class UserRegisterationAPIViewTest(APITestCase):
    def test_user_registration(self):
        data = {
            "email": "testuser@example.com",
            "password": "testpassword123",
            "username": "Test",
            
        }
        response = self.client.post("/users/register/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("tokens", response.data)

class UserLoginAPIViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@example.com", password="testpassword123"
        )

    def test_user_login(self):
        data = {"email": "testuser@example.com", "password": "testpassword123"}
        response = self.client.post("/users/login/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("tokens", response.data)

class UserLogoutAPIViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@example.com", password="testpassword123"
        )
        self.token = RefreshToken.for_user(self.user)

    def test_user_logout(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token.access_token}")
        data = {"refresh": str(self.token)}
        response = self.client.post("/users/logout/", data)
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)

class UserAPIViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@example.com", password="testpassword123"
        )
        self.client.force_authenticate(user=self.user)

    def test_get_user(self):
        response = self.client.get("/users/me/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class UserProfileAPIViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@example.com", password="testpassword123"
        )
        self.client.force_authenticate(user=self.user)

    def test_get_user_profile(self):
        response = self.client.get("/users/profile/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

