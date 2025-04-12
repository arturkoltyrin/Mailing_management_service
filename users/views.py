import secrets

from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, PasswordResetConfirmView, PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.crypto import get_random_string
from django.views.generic import CreateView, DeleteView, DetailView, FormView, ListView, TemplateView, UpdateView

from config.settings import EMAIL_HOST_USER
from users.forms import UserForgotPasswordForm, UserRegisterForm, UserSetNewPasswordForm, UserUpdateForm, \
    PasswordRecoveryForm
from users.models import User

# Create your views here.

def user_logout(request):
    logout(request)
    return render(request, template_name='mailing/home.html')

class UserCreateView(CreateView):
    model = User
    form_class = UserRegisterForm
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        user = form.save()
        user.is_active = False
        token = secrets.token_hex(16)
        user.token = token
        user.save()
        host = self.request.get_host()
        url = f"http://{host}/users/email-confirm/{token}/"
        send_mail(
            subject="Потверждение почты",
            message=f"Рады вашей регистрации!Осталось потвердить почту!{url}",
            from_email=EMAIL_HOST_USER,
            recipient_list=[user.email],
        )

        return super().form_valid(form)


def email_verification(request, token):
    user = get_object_or_404(User, token=token)
    user.is_active = True
    user.save()
    return HttpResponse("подтвержден")


class UserListView(ListView):
    model = User
    template_name = "users/user_lists.html"
    context_object_name = "users_list"


class UserDetailView(DetailView):
    model = User
    form_class = UserUpdateForm


class UserUpdateView(UpdateView):
    model = User
    form_class = UserUpdateForm


class UserDeleteView(DeleteView):
    model = User
    form_class = UserUpdateForm


class UserPasswordResetConfirmView(SuccessMessageMixin, PasswordResetConfirmView):
    """Представление установки нового пароля"""

    form_class = UserSetNewPasswordForm
    template_name = "users/user_password_set_new.html"
    success_url = reverse_lazy("users:login")
    success_message = "Пароль успешно изменен. Можете авторизоваться на сайте."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Установить новый пароль"
        return context


class UserForgotPasswordView(SuccessMessageMixin, PasswordResetView):
    """Представление по сбросу пароля по почте"""

    form_class = UserForgotPasswordForm
    template_name = "users/password_reset.html"
    success_url = reverse_lazy("users:login")
    success_message = "Письмо с инструкцией по восстановлению пароля отправлено на ваш email"
    subject_template_name = "users/email/password_subject_reset_mail.txt"
    email_template_name = "users/email/password_reset_mail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Запрос на восстановление пароля"
        return context


class PasswordRecoveryView(FormView):
    template_name = "password_recovery.html"
    form_class = PasswordRecoveryForm
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        user = User.objects.get(email=email)
        length = 12
        alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        password = get_random_string(length, alphabet)
        user.set_password(password)
        user.save()
        send_mail(
            subject="Восстановление пароля",
            message=f"Ваш новый пароль: {password}",
            from_email=EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=False,
        )
        return super().form_valid(form)