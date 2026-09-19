from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User


class UserAuthTests(APITestCase):
    def setUp(self):
        self.register_url = reverse("users:auth_register")
        self.token_url = reverse("token_obtain_pair")
        self.user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "StrongPassword123",
            "telegram_id": "123456789",
        }

    def test_registration(self):
        """Тест успешной регистрации пользователя"""
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().email, "test@example.com")

    def test_login_and_token_obtain(self):
        """Тест получения JWT-токена при авторизации"""
        User.objects.create_user(
            username=self.user_data["username"], email=self.user_data["email"], password=self.user_data["password"]
        )
        login_data = {"email": self.user_data["email"], "password": self.user_data["password"]}
        response = self.client.post(self.token_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
