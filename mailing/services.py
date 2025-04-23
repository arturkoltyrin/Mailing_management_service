from django.utils import timezone
from django.core.cache import cache
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from config import settings
from config.settings import CACHE_ENABLED, EMAIL_HOST_USER
from mailing.models import AttemptMailing, Mailing
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse



def run_mail(request, pk):
    """Функция запуска рассылки по требованию"""
    mailing = get_object_or_404(Mailing, id=pk)
    try:
        # Код отправки рассылки
        for recipient in mailing.client.all():
            send_mail(
                subject=mailing.message.subject,
                message=mailing.message.content,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[recipient.mail],
                fail_silently=False,
            )
            # Запись истории отправки
            AttemptMailing.objects.create(
                date_attempt=timezone.now(),
                status=AttemptMailing.STATUS_OK,
                server_response="Email отправлен",
                mailing=mailing,
            )
    except Exception as e:
        # Запись ошибки
        AttemptMailing.objects.create(
            date_attempt=timezone.now(),
            status=AttemptMailing.STATUS_NOK,
            server_response=str(e),
            mailing=mailing,
        )
        return HttpResponse("Ошибка отправки рассылки.")
    return redirect("mailing:mailing_list")


def get_mailing_from_cache():
    """Получение данных по рассылкам из кэша, если кэш пуст берем из БД."""

    if not CACHE_ENABLED:
        return Mailing.objects.all()
    key = "mailing_list"
    cache_mail = cache.get(key)
    if cache_mail is not None:
        return cache_mail
    cache_mail = Mailing.objects.all()
    cache.set(cache_mail, key)
    return cache_mail


def get_attempt_from_cache():
    """Получение данных по попыткам  из кэша, если кэш пуст берем из БД."""

    if not CACHE_ENABLED:
        return AttemptMailing.objects.all()
    key = "attempt_list"
    cache_attempt = cache.get(key)
    if cache_attempt is not None:
        return cache_attempt
    cache_mail = Mailing.objects.all()
    cache.set(cache_attempt, key)
    return cache_attempt


@login_required
def block_mailing(request, pk):
    mailing = get_object_or_404(Mailing, pk=pk)
    # Проверить, имеет ли пользователь право блокировать рассылку
    if not request.user.is_superuser and not request.user.groups.filter(name="Модераторы").exists():
        raise PermissionDenied("Только модераторы и администраторы могут блокировать рассылки.")
    # Меняем статус активности рассылки
    mailing.is_active = not mailing.is_active
    mailing.save()
    return redirect(reverse("mailing:mailing_list"))