from django.urls import path

from .apps import UsersConfig
from .views import RegisterView

app_name = UsersConfig.name

urlpatterns = [
    path("", RegisterView.as_view(), name="auth_register"),
]
