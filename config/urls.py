from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# Настройка Swagger / ReDoc документации
schema_view = get_schema_view(
    openapi.Info(
        title="Habit Tracker API",
        default_version="v1",
        description="Документация для курсовой работы по трекеру привычек",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("admin/", admin.site.urls),
    # Документация API
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    # Авторизация и регистрация
    path("api/users/register/", include("users.urls")),
    path("api/users/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/users/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # Бизнес-логика привычек
    path("api/", include("habits.urls")),
]
