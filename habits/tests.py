import datetime

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from habits.models import Habit
from users.models import User


class HabitAPITests(APITestCase):
    def setUp(self):
        # Создаем пользователей
        self.user1 = User.objects.create_user(username="user1", email="u1@test.com", password="password")
        self.user2 = User.objects.create_user(username="user2", email="u2@test.com", password="password")

        # Аутентифицируем первого пользователя по умолчанию
        self.client.force_authenticate(user=self.user1)

        self.list_create_url = reverse("habit-list")  # Эндпоинт /api/habits/
        self.public_list_url = reverse("habit-public-list")  # Эндпоинт /api/habits/public/

        # Создаем приятную привычку для тестов связанных связей
        self.pleasant_habit = Habit.objects.create(
            creator=self.user1,
            action="Съесть фрукт",
            time=datetime.time(12, 0),
            place="Кухня",
            is_pleasant=True,
            duration=1,
        )

    def test_create_habit_success(self):
        """Успешное создание полезной привычки с вознаграждением"""
        data = {
            "action": "Сделать зарядку",
            "time": "08:00:00",
            "place": "Спальня",
            "reward": "Выпить кофе",
            "duration": 2,
            "periodicity": 1,
        }
        response = self.client.post(self.list_create_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Habit.objects.filter(creator=self.user1).count(), 2)

    def test_validator_reward_and_bound_habit(self):
        """Ошибка: Нельзя одновременно указывать вознаграждение и связанную привычку"""
        data = {
            "action": "Почитать книгу",
            "time": "21:00:00",
            "place": "Зал",
            "reward": "Шоколадка",
            "bound_habit": self.pleasant_habit.id,
            "duration": 2,
        }
        response = self.client.post(self.list_create_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)

    def test_validator_duration_limit(self):
        """Ошибка: Время выполнения привычки не может превышать 120 секунд (2 минуты)"""
        data = {
            "action": "Бег на месте",
            "time": "07:00:00",
            "place": "Коридор",
            "reward": "Отдых",
            "duration": 5,  # Больше 2 минут
        }
        response = self.client.post(self.list_create_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("duration", response.data)

    def test_validator_periodicity_limit(self):
        """Ошибка: Периодичность не может быть реже 1 раза в 7 дней"""
        data = {
            "action": "Полить цветы",
            "time": "10:00:00",
            "place": "Окно",
            "reward": "Конфета",
            "periodicity": 10,  # Раз в 10 дней — запрещено
        }
        response = self.client.post(self.list_create_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("periodicity", response.data)

    def test_rights_and_public_visibility(self):
        """Тест прав доступа: пользователь не видит чужие приватные привычки, но видит публичные"""
        # Создаем публичную привычку от лица user2
        Habit.objects.create(
            creator=self.user2,
            action="Прогулка",
            time=datetime.time(18, 0),
            place="Парк",
            is_pleasant=True,
            is_public=True,
            duration=2,
        )
        # Создаем приватную привычку от лица user2
        Habit.objects.create(
            creator=self.user2,
            action="Секретное действие",
            time=datetime.time(23, 0),
            place="Дом",
            is_pleasant=True,
            is_public=False,
            duration=2,
        )

        # Запрос личного списка (user1 не должен видеть привычки user2)
        response = self.client.get(self.list_create_url)
        self.assertEqual(len(response.data["results"]), 1)  # Только его собственная pleasant_habit

        # Запрос публичного списка
        response = self.client.get(self.public_list_url)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["action"], "Прогулка")

    def test_owner_can_delete_own_habit(self):
        """Создатель может удалить свою привычку"""
        url = reverse("habit-detail", args=[self.pleasant_habit.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_cannot_delete_other_user_habit(self):
        """Пользователь не может удалить привычку другого пользователя"""
        # Привычка создана user2 (создана в setUp или сейчас)
        # Создаём привычку от user2 (ещё не создана)
        habit_user2 = Habit.objects.create(
            creator=self.user2,
            action="Чужая привычка",
            time=datetime.time(14, 0),
            place="Офис",
            is_pleasant=True,
            duration=1,
        )
        # Аутентифицируемся как user1
        self.client.force_authenticate(user=self.user1)
        url = reverse("habit-detail", args=[habit_user2.id])
        response = self.client.delete(url)
        # Ожидаем 403 (Forbidden) или 404 (Not Found)
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])
