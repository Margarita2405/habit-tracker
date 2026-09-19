from rest_framework import serializers

from habits.models import Habit


class HabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = "__all__"
        read_only_fields = ("creator",)

    def validate(self, data):
        """Комплексная валидация привычки по правилам бизнес-логики."""
        # Извлекаем данные с учетом частичного обновления (PATCH)
        # Если поле не передано в запросе, берем его текущее значение из инстанса
        is_pleasant = data.get("is_pleasant", getattr(self.instance, "is_pleasant", False))
        reward = data.get("reward", getattr(self.instance, "reward", None))
        bound_habit = data.get("bound_habit", getattr(self.instance, "bound_habit", None))
        duration = data.get("duration", getattr(self.instance, "duration", 2))
        periodicity = data.get("periodicity", getattr(self.instance, "periodicity", 1))

        # Ограничение на одновременный выбор связанной привычки и вознаграждения
        if reward and bound_habit:
            raise serializers.ValidationError(
                {
                    "non_field_errors": "Нельзя одновременно заполнять поле вознаграждения и связанной привычки."
                    "Выберите что-то одно."
                }
            )

        # Ограничение на время выполнения (не больше 120 секунд / 2 минут)
        if duration > 2:
            raise serializers.ValidationError(
                {"duration": "Время на выполнение привычки должно быть не больше 2 минут)."}
            )

        # В связанные привычки могут попадать только привычки с признаком приятной привычки
        if bound_habit and not bound_habit.is_pleasant:
            raise serializers.ValidationError(
                {
                    "bound_habit": "В связанные привычки можно добавлять только те привычки, у которых установлен"
                    "признак приятной привычки."
                }
            )

        # У приятной привычки не может быть вознаграждения или связанной привычки
        if is_pleasant:
            if reward or bound_habit:
                raise serializers.ValidationError(
                    {"is_pleasant": "У приятной привычки не может быть вознаграждения или связанной привычки."}
                )

        # Ограничение на периодичность выполнения (не реже чем 1 раз в 7 дней)
        if periodicity > 7:
            raise serializers.ValidationError(
                {
                    "periodicity": "Периодичность выполнения привычки не может быть реже, чем 1 раз в 7 дней"
                    "(нельзя не выполнять привычку более 7 дней)."
                }
            )

        return data
