from rest_framework import permissions


class IsOwnerOrReadOnlyIfPublic(permissions.BasePermission):
    """Разрешает доступ к CRUD только создателю привычки.
    Публичные привычки разрешено только просматривать (SAFE_METHODS)."""

    def has_object_permission(self, request, view, obj):
        # Если привычка публичная и запрос безопасный (GET, HEAD, OPTIONS)
        if obj.is_public and request.method in permissions.SAFE_METHODS:
            return True
        # В остальных случаях доступ только владельцу
        return obj.creator == request.user
