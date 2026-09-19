import requests
from django.conf import settings


def send_telegram_message(telegram_id: str, text: str) -> bool:
    """Отправляет текстовое сообщение пользователю в Telegram.
    В режиме тестирования или при отсутствии токена симулирует отправку в
    консоль. Возвращает True в случае успеха, False при ошибке."""
    token = getattr(settings, "TELEGRAM_BOT_TOKEN", None)

    # Если токена нет или мы в режиме тестов, используем безопасную заглушку
    if not token or token == "mock_token" or not telegram_id:
        payload = {"chat_id": telegram_id, "text": text}
        print(f"[Telegram] (симуляция) Отправлено сообщение: {payload}")
        return True

    # Реальная отправка через Telegram Bot API
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": telegram_id, "text": text}

    try:
        response = requests.post(url, json=payload, timeout=5)
        print(f"Telegram ответ: {response.status_code} - {response.text}")
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"Исключение при отправке в Telegram: {e}")
        return False

