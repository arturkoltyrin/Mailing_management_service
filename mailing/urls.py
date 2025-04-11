from django.urls import path, include
from . import views
from django.views.decorators.cache import cache_page
from django.contrib.auth import views as auth_views
from users.views import RegisterView

app_name = "mailing"

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("recipient_list", cache_page(5*60)(views.RecipientListView.as_view()), name="recipient_list",),
    path("recipient/create", views.RecipientCreateView.as_view(), name="recipient_create"),
    path("recipient/<int:pk>/update", views.RecipientUpdateView.as_view(), name="recipient_update"),
    path("recipient/<int:pk>/delete", views.RecipientDeleteView.as_view(), name="recipient_delete"),
    path("message_list", cache_page(5*60)(views.MessageListView.as_view()), name="message_list"),
    path("message/create", views.MessageCreateView.as_view(), name="message_create"),
    path("message/<int:pk>/update", views.MessageUpdateView.as_view(), name="message_update"),
    path("message/<int:pk>/delete", views.MessageDeleteView.as_view(), name="message_delete"),
    path("mailing_list", cache_page(5*60)(views.MailingListView.as_view()), name="mailing_list"),
    path("mailing/create", views.MailingCreateView.as_view(), name="mailing_create"),
    path("mailing/<int:pk>/update", views.MailingUpdateView.as_view(), name="mailing_update"),
    path("mailing/<int:pk>/delete", views.MailingDeleteView.as_view(), name="mailing_delete"),
    path("mailing/<int:pk>", views.MailingDetailView.as_view(), name="mailing_detail"),
    path("mailing/<int:pk>/stop", views.MailingStopView.as_view(), name="mailing_stop"),
    path("mailingattempt_list", cache_page(5*60)(views.MailingAttemptListView.as_view()), name="mailingattempt_list"),
    path('register/', RegisterView.as_view(), name='register'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('clients/', include('clients.urls', namespace='clients')),
]