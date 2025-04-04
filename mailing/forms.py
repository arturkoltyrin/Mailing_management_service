from django import forms
from .models import Message, Recipient, Mailing


class MailingForm(forms.ModelForm):
    class Meta:
        model = Mailing
        fields = "__all__"
        exclude = ["owner"]
        widgets = {"recipients": forms.CheckboxSelectMultiple()}

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user:
            self.fields["recipients"].queryset = Recipient.objects.filter(owner=user)
            self.fields["message"].queryset = Message.objects.filter(owner=user)


class RecipientForm(forms.ModelForm):
    class Meta:
        model = Recipient
        fields = "__all__"
        exclude = ["owner"]


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = "__all__"
        exclude = ["owner"]