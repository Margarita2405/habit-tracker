import datetime

from celery import shared_task

from habits.models import Habit
from notifications.services import send_telegram_message


@shared_task
def send_habit_reminders():
    """Ежеминутная задача Celery для проверки текущих привычек и отправки алертов."""
    now = datetime.datetime.now().time()
    current_hour_minute = now.replace(second=0, microsecond=0)
    print(f"Текущее время (без секунд): {current_hour_minute}")

    # Находим привычки, время которых совпадает по часам и минутам
    habits = Habit.objects.filter(time__hour=current_hour_minute.hour, time__minute=current_hour_minute.minute)
    print(f"Найдено привычек: {habits.count()}")

    for habit in habits:
        print(f"Обработка привычки: {habit.action}, telegram_id={habit.creator.telegram_id}")
        if habit.creator.telegram_id:
            message = f"Напоминание! Время выполнять привычку: '{habit.action}' в {habit.time.strftime('%H:%M')}."
            message += f"\nМесто: {habit.place}."

            if habit.bound_habit:
                message += f"\nЗатем вас ждет приятное: {habit.bound_habit.action}!"
            elif habit.reward:
                message += f"\nНаграда после выполнения: {habit.reward}!"

            send_telegram_message(habit.creator.telegram_id, message)
