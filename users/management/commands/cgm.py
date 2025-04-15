from django.core.management.base import BaseCommand
from users.models import User

class Command(BaseCommand):
    help = 'Создаёт пользователя с правами модератора'

    def handle(self, *args, **kwargs):
        user = User.objects.create_user(
            email='moderator@example.com',
            password='securepassword123',
            is_staff=True  # делаем модератором
        )
        user.save()
        self.stdout.write(self.style.SUCCESS(f'Пользователь {user.email} создан с правами модератора'))