from datetime import datetime, timedelta
from django.db import models
from users.models import CustomUser


class Recipient(models.Model):
    """Модель Получатель рассылки"""

    email = models.EmailField(unique=True, verbose_name='Почта', help_text='Адрес почты должен быть уникальным')
    full_name = models.CharField(max_length=200, verbose_name='ФИО')
    comment = models.TextField(null=True, blank=True, verbose_name='Комментарий')
    owner = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='recipients_owner',
                              verbose_name='Владелец')

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'Получатель рассылки'
        verbose_name_plural = 'Получатели рассылки'
        ordering = ['id']


class Message(models.Model):
    """Модель сообщений"""
    title = models.CharField(max_length=200, verbose_name='Тема письма')
    message = models.TextField(verbose_name='Тело письма')
    owner = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='message_owner',
                              verbose_name='Владелец')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        ordering = ['id']


class Mailing(models.Model):
    """Модель рассылок"""

    COMPLETED = 'completed'
    CREATED = 'created'
    RUNNING = 'running'

    STATUS_CHOICES = [
        (COMPLETED, 'Завершена'),
        (CREATED, 'Создана'),
        (RUNNING, 'Запущена'),
    ]

    first_send_at = models.DateTimeField(default=datetime.now(), verbose_name="Дата и время первой отправки")
    finish_send_at = models.DateTimeField(default=datetime.now() + timedelta(days=1),
                                          verbose_name="Дата и время окончания отправки",)
    status = models.CharField(max_length=9, choices=STATUS_CHOICES, verbose_name='Статус рассылки')
    owner = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='mailing_owner',
                              verbose_name='Владелец')
    message = models.ForeignKey(Message, on_delete=models.SET_NULL, null=True, blank=True, related_name='mailing',
                                verbose_name='Сообщение')
    recipients = models.ManyToManyField(Recipient, related_name="mailing", verbose_name="Получатели")

    def __str__(self):
        subject = self.message.title if self.message else 'Тема не указана'
        recipient_count = self.recipients.count()
        return (f'''Рассылка №{self.pk}.
                Тема письма: {subject}.
                Количество получателей: {recipient_count}.''')

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'
        ordering = ['id']
        permissions = [('can_cancel_mailing', 'Can cancel mailing')]


class MailingAttempt(models.Model):
    SUCCESS = 'success'
    FAILURE = 'failure'

    STATUS_CHOICES = [
        (SUCCESS, 'Успешно'),
        (FAILURE, 'Не успешно'),
    ]

    attempted_at = models.DateTimeField(verbose_name="Дата и время попытки отправки")
    status = models.CharField(max_length=7, choices=STATUS_CHOICES, verbose_name='Статус')
    mail_server_response = models.TextField(null=True, blank=True, verbose_name='Ответ сервера')
    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE, related_name='attempts', verbose_name='Рассылка')

    def __str__(self):
        return f'{self.pk} - {self.attempted_at}'

    class Meta:
        verbose_name = 'Попытка рассылки'
        verbose_name_plural = 'Попытки рассылки'
        ordering = ['id']