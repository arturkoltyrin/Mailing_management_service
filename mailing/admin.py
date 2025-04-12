from django.contrib import admin
from mailing.models import Mailing, AttemptMailing, Message, ReceiveMail
from users.models import User


@admin.register(ReceiveMail)
class ReceiveMailAdmin(admin.ModelAdmin):
    list_display = ("id", "fio", "mail", "comment", "owner")
    list_filter = ("fio",)
    search_fields = (
        "fio",
        "mail",
    )


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "subject",
        "content",
        "owner",
    )
    search_fields = ("subject",)
    list_filter = ("subject",)


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ("id", "first_sending", "end_sending", "status", "message", "is_active", "owner")
    search_fields = ("status",)
    list_filter = ("status",)

@admin.register(AttemptMailing)
class MailingAttemptAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "owner",
        "response",
        "date_attempt",
        "status",
    )
    search_fields = ("owner",)
    list_filter = ("owner",)

