
from django.utils import timezone
from django.core.cache import cache
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from config.settings import CACHE_ENABLED, EMAIL_HOST_USER
from mailing.models import AttemptMailing, Mailing
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse


@login_required
def run_mail(request, pk):
    mailing = get_object_or_404(Mailing, id=pk)
    # Проверяем, что пользователь — владелец или суперюзер
    if mailing.owner != request.user and not request.user.is_superuser:
        raise PermissionDenied("Нет доступа к отправке этой рассылки.")
    try:
        recipients = (mailing.client.filter(owner=request.user)
                      if not request.user.is_superuser else
                      mailing.client.all())
        for recipient in recipients:
            send_mail(
                subject=mailing.message.subject,
                message=mailing.message.content,
                from_email=EMAIL_HOST_USER,
                recipient_list=[recipient.mail],
                fail_silently=False,
            )
            AttemptMailing.objects.create(
                date_attempt=timezone.now(),
                status=AttemptMailing.STATUS_OK,
                response="Email отправлен",
                mailing=mailing,
            )
    except Exception as e:
        AttemptMailing.objects.create(
            date_attempt=timezone.now(),
            status=AttemptMailing.STATUS_NOK,
            response=str(e),
            mailing=mailing,
        )
        return HttpResponse("Ошибка отправки рассылки.")
    return redirect(reverse("mailing:mailing_list"))


def get_mailing_from_cache():
    if not CACHE_ENABLED:
        return Mailing.objects.all()
    key = "mailing_list"
    data = cache.get(key)
    if data is None:
        data = Mailing.objects.all()
        cache.set(key, data)
    return data


def get_attempt_from_cache():
    if not CACHE_ENABLED:
        return AttemptMailing.objects.all()
    key = "attempt_list"
    data = cache.get(key)
    if data is None:
        data = AttemptMailing.objects.all()
        cache.set(key, data)
    return data


@login_required
def block_mailing(request, pk):
    mailing = get_object_or_404(Mailing, pk=pk)
    # Блокировать может только суперюзер
    if not request.user.is_superuser:
        raise PermissionDenied("Только администратор может блокировать рассылки.")
    mailing.is_active = not mailing.is_active
    mailing.save()
    return redirect(reverse("mailing:mailing_list"))
