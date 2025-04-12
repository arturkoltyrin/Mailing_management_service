from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm, UserCreationForm
from django.forms import ModelForm
from django.urls import reverse_lazy
from django import forms
from mailing.forms import StyleFormMixin
from users.models import User


class UserRegisterForm(StyleFormMixin, UserCreationForm):
    class Meta:
        model = User
        fields = ("email", "password1", "password2")

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            self.fields["password1"].label = "Ваш пароль"
            self.fields["password2"].label = "Повторите пароль"

            self.fields["password1"].help_text = (
                "- Ваш пароль не должен быть слишком похож на другую личную информацию.<br>"
                "- Ваш пароль должен содержать как минимум 8 символов.<br>"
                "- Ваш пароль не должен быть распространённым.<br>"
                "- Ваш пароль не должен состоять только из цифр."
            )

            self.fields["password2"].help_text = "Введите тот же пароль для подтверждения."




class UserUpdateForm(StyleFormMixin, ModelForm):

    class Meta:
        model = User
        fields = "__all__"
        exclude = ("token",)

        success_url = reverse_lazy("users:users")


class UserForgotPasswordForm(PasswordResetForm):
    """Форма запроса на восстановление пароля"""

    def __init__(self, *args, **kwargs):
        """Обновление стилей формы"""
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({"class": "form-control", "autocomplete": "off"})


class UserSetNewPasswordForm(SetPasswordForm):
    """Форма изменения пароля пользователя после подтверждения"""

    def __init__(self, *args, **kwargs):
        """Обновление стилей формы"""
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({"class": "form-control", "autocomplete": "off"})


class PasswordRecoveryForm(StyleFormMixin, forms.Form):
    email = forms.EmailField(label="Укажите Email")

    def clean_email(self):
        """Проверка email на уникальность"""
        email = self.cleaned_data.get("email")
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("Такого email нет в системе")
        return email