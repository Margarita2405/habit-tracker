from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from habits.models import Habit
from habits.permissions import IsOwnerOrReadOnlyIfPublic
from habits.serializers import HabitSerializer


class HabitViewSet(viewsets.ModelViewSet):
    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnlyIfPublic]

    def get_queryset(self):
        """Фильтруем выборку: обычные действия возвращают только личные привычки текущего пользователя."""
        if self.action == "public_list":
            return Habit.objects.filter(is_public=True)
        return Habit.objects.filter(creator=self.request.user)

    def perform_create(self, serializer):
        """Автоматически назначаем создателем текущего авторизованного пользователя"""
        serializer.save(creator=self.request.user)

    @action(detail=False, methods=["get"], url_path="public")
    def public_list(self, request):
        """Эндпоинт для просмотра списка ВСЕХ публичных привычек. Доступен по URL: /api/habits/public/"""
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
