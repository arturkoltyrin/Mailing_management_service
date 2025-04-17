from django.db import models
from users.models import User


class ReceiveMail(models.Model):
    """Модель «Получатель рассылки»:"""

    mail = models.EmailField(unique=True)
    fio = models.CharField(max_length=255, verbose_name="ФИО", blank=True, null=True)
    comment = models.TextField(verbose_name="Комментарии", null=True, blank=True)

    owner = models.ForeignKey(
        User,
        verbose_name="Получатель",
        help_text="укажите получателя рассылки",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    def __str__(self):
        return f"{self.fio} {self.mail} "

    class Meta:
        verbose_name = "получатель"
        verbose_name_plural = "получатели"
        ordering = ["fio"]
        permissions = [
            ("can_blocking_client", "Может блокировать получателя"),
        ]


class Message(models.Model):
    """Модель «Сообщение»:"""

    subject = models.CharField(max_length=255, verbose_name="Тема письма")
    content = models.TextField(verbose_name="Содержимое письма")
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Владелец")

    def __str__(self):
        return self.content

    class Meta:
        verbose_name = "письмо"
        verbose_name_plural = "письма"
        ordering = ["subject"]
        permissions = [
            ('can_blocking_sms', 'Может блокировать сообщение'),
        ]


class Mailing(models.Model):
    """Модель «Рассылка»:"""

    CREATED = "Создано"
    LAUNCHED = "Запущено"
    FINISHED = "Завершена"

    STATUS_CHOICES = [
        (CREATED, "Создано"),
        (LAUNCHED, "Запущено"),
        (FINISHED, "Завершена"),
    ]

    first_sending = models.DateTimeField(verbose_name="Дата первой отправки", null=True, blank=True)
    end_sending = models.DateTimeField(verbose_name="Дата окончания отправки", null=True, blank=True)

    status = models.CharField(max_length=11, choices=STATUS_CHOICES, default=CREATED, verbose_name="Статус рассылки")
    is_active = models.BooleanField(default=True, verbose_name="активна", null=True, blank=True)
    message = models.ForeignKey(Message, on_delete=models.CASCADE, verbose_name="Сообщение", related_name="mailings",
                                null=True, blank=True)
    client = models.ManyToManyField(ReceiveMail, verbose_name="Клиент", )
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, editable=False, null=True, blank=True,
                              verbose_name="Владелец")

    def __str__(self):
        return f"{self.id}"

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"
        ordering = ["first_sending"]
        permissions = [
            ("set_is_active", "set is active"),
        ]


class AttemptMailing(models.Model):
    """Модель «Попытка рассылки»"""

    date_attempt = models.DateTimeField(verbose_name="Дата и время попытки")
    status = models.CharField(max_length=115, verbose_name="Статус попытки")
    response = models.TextField(verbose_name="Комментарии", null=True, blank=True)
    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE, verbose_name="Рассылка", related_name="mailing")
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Владелец")

    def __str__(self):
        return f'{self.date_attempt} "{self.status}" '

    class Meta:
        verbose_name = "попытка"
        verbose_name_plural = "попытки"
        ordering = ["date_attempt", "status"]