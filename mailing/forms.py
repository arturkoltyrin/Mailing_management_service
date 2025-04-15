from django import forms
from django.forms import BooleanField, ModelForm
from .models import AttemptMailing, Mailing, Message, ReceiveMail


class StyleFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for fild_name, fild in self.fields.items():
            if isinstance(fild, BooleanField):
                fild.widget.attrs["class"] = "form-check-input"
            else:
                fild.widget.attrs["class"] = "form-control"


class EmailForm(forms.Form):
    subject = forms.CharField(max_length=255, label="Тема письма")
    message = forms.CharField(widget=forms.Textarea, label="Сообщение")
    recipients = forms.CharField(widget=forms.Textarea, label="Получатели")


class MailingForm(StyleFormMixin, ModelForm):
    class Meta:
        model = Mailing
        fields = ['message', 'client']


class MessageForm(StyleFormMixin, ModelForm):

    class Meta:
        model = Message
        fields = "__all__"


class ReceiveMailForm(StyleFormMixin, ModelForm):

    class Meta:
        model = ReceiveMail
        fields = ['mail', 'fio', 'comment']



class ReceiveMailModeratorForm(StyleFormMixin, ModelForm):
    class Meta:
        model = ReceiveMail
        fields = "__all__"


class MailingModeratorForm(StyleFormMixin, ModelForm):
    class Meta:
        model = Mailing
        fields = "__all__"