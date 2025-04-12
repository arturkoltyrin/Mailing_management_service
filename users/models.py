from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):

    username = None
    email = models.EmailField(unique=True, verbose_name="Email")
    phone = models.CharField(
        max_length=35, verbose_name="телофон", blank=True, null=True, help_text="введи номер телефона"
    )
    first_name = models.CharField(max_length=50, verbose_name="Имя")
    last_name = models.CharField(max_length=50, verbose_name="Фамилия")
    middle_name = models.CharField(max_length=50, verbose_name="Отчество", blank=True, null=True)
    avatar = models.ImageField(upload_to="photo/avatars/", blank=True, null=True, verbose_name="Аватар")
    country = models.CharField(max_length=50, blank=True, null=True, verbose_name="Страна", help_text="Укажите страну")
    token = models.CharField(max_length=100, verbose_name="Token", blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        permissions = [
            ("can_block_user", "Блокировка пользователя"),
        ]

    def __str__(self):
        return self.email