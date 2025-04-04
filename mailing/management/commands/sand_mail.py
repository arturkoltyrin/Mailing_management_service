from mailing.models import Mailing, MailingAttempt
from config.settings import DEFAULT_FROM_EMAIL
from django.utils.timezone import now
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.core.mail import send_mail
from datetime import timedelta


class Command(BaseCommand):
    """Функция для отправки рассылок."""
    def handle(self, *args, **kwargs):
        time_threshold_start = now() - timedelta(hours=20)
        time_threshold_end = now()

        mailings = Mailing.objects.filter(
            Q(status=Mailing.CREATED) | Q(status=Mailing.RUNNING),
            first_send_at__gte=time_threshold_start,
            first_send_at__lte=time_threshold_end)

        for mailing in mailings:
            recipients = mailing.recipients.all()
            for recipient in recipients:
                try:
                    send_mail(
                        subject=mailing.message,
                        message=mailing.message.message,
                        from_email=DEFAULT_FROM_EMAIL,
                        recipient_list=[recipient.email],
                    )
                    status = MailingAttempt.SUCCESS
                    response = f"{recipient.email}: Успешно отправлено"

                    MailingAttempt.objects.create(
                        attempted_at=now(),
                        status=status,
                        mail_server_response=response,
                        mailing=mailing)

                except Exception as e:
                    status = MailingAttempt.FAILURE
                    response = f"{recipient.email}: Ошибка: {str(e)}"

                MailingAttempt.objects.create(
                    attempted_at=now(),
                    status=status,
                    mail_server_response=response,
                    mailing=mailing,
                )

            mailing.status = Mailing.RUNNING
            mailing.save()