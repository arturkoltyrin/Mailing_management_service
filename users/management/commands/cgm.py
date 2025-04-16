from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from users.models import User
from mailing.models import Message, ReceiveMail, Mailing  # адаптируй под свои модели

class Command(BaseCommand):
    help = "Создаёт модератора и группу с нужными правами"

    def handle(self, *args, **kwargs):
        # Создание группы
        group_name = 'moderator_mailing'
        moder_group, created = Group.objects.get_or_create(name=group_name)

        # Установка прав доступа
        models_with_permissions = [Message, ReceiveMail, Mailing]
        for model in models_with_permissions:
            content_type = ContentType.objects.get_for_model(model)
            permissions = Permission.objects.filter(content_type=content_type)
            for perm in permissions:
                moder_group.permissions.add(perm)

        # Создание пользователя
        user, created = User.objects.get_or_create(email='moderator@example.com')
        if created:
            user.set_password('q1w2e3R$')
            user.is_active = True
            user.is_staff = True  # можно включить интерфейс админки
            user.save()
            self.stdout.write(self.style.SUCCESS("Модератор создан."))

        user.groups.add(moder_group)
        self.stdout.write(self.style.SUCCESS(f"Модератор добавлен в группу {group_name}"))