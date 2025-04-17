from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, request
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from mailing.models import AttemptMailing, Mailing, Message, ReceiveMail
from .forms import MailingForm, MailingModeratorForm, MessageForm, ReceiveMailForm, ReceiveMailModeratorForm
from .services import get_attempt_from_cache, get_mailing_from_cache


def base(request):
    return render(request, "base.html")


# Главная страница
class homeView(TemplateView):
    template_name = "mailing/home.html"

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["title"] = "Главная"
        context_data["count_mailing"] = len(Mailing.objects.all())
        active_mailings_count = Mailing.objects.filter(status="Создано").count()
        context_data["active_mailings_count"] = active_mailings_count
        unique_clients_count = ReceiveMail.objects.distinct().count()
        context_data["unique_clients_count"] = unique_clients_count
        return context_data


# Шаблон контакты
class Contacts(TemplateView):

    template_name = "mailing/contacts.html"

    def contacts(request):
        if request.method == "POST":
            name = request.POST.get("name")  # получаем имя
            message = request.POST.get("message")  # получаем сообщение
            return HttpResponse(f"Спасибо, {name}! {message} Сообщение получено.")
        return render(request, "mailing/contacts.html")


# Страница ответа на отправленное сообщение
class Messages(ListView):

    template_name = "mailing/message_list.html"


# CRUD для рассылок
class MailingListView(ListView):
    model = Mailing
    template_name = "mailing/mailing_list.html"

    def get_queryset(self):
        return get_mailing_from_cache()


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailing/message_form.html'
    success_url = reverse_lazy("mailing:message_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user  # устанавливаем владельца
        return super().form_valid(form)




class MailingDetailView(LoginRequiredMixin, DetailView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailing/receivemail_list.html"

    def get_queryset(self):
        return get_mailing_from_cache()


class MailingUpdateView(LoginRequiredMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    success_url = reverse_lazy("mailing:mailing_list")

    def get_form_class(self):
        user = self.request.user
        if user.has_perm("mailing.set_is_active"):
            return MailingModeratorForm
        return MailingForm

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['client'].queryset = ReceiveMail.objects.filter(owner=self.request.user)
        form.fields['message'].queryset = Message.objects.filter(owner=self.request.user)
        return form


class MailingDeleteView(LoginRequiredMixin, DeleteView):
    model = Mailing
    template_name = "mailing/mailing_delete.html"
    success_url = reverse_lazy("mailing:mailing_list")


# CRUD для получателей


class ReceiveMailListView(LoginRequiredMixin, ListView):
    model = ReceiveMail
    template_name = 'mailing/receivemail_list.html'
    context_object_name = 'Получатель'

    def get_queryset(self):
        return ReceiveMail.objects.filter(owner=self.request.user)


class ReceiveMailDetailView(LoginRequiredMixin, DetailView):
    model = ReceiveMail
    form_class = ReceiveMailModeratorForm

    def get_object(self, queryset=None):
        self.object = super().get_object(queryset)
        if self.request.user.is_superuser:
            return self.object
        if self.object.owner != self.request.user and not self.request.user.is_superuser:
            raise PermissionDenied
        return self.object


class ReceiveMailCreateView(LoginRequiredMixin, CreateView):
    model = ReceiveMail
    form_class = ReceiveMailForm
    template_name = "mailing/receivemail_form.html"
    success_url = reverse_lazy("mailing:receivemail_list")

    def form_valid(self, form):
        client = form.save()
        user = self.request.user
        client.owner = user
        client.save()

        return super().form_valid(form)


class ReceiveMailUpdateView(LoginRequiredMixin, UpdateView):
    model = ReceiveMail
    form_class = ReceiveMailForm

    success_url = reverse_lazy("mailing:receivemail_list")

    def get_form_class(self):
        user = self.request.user
        if user.has_perm("mailing.can_blocking_client"):
            return ReceiveMailModeratorForm
        return ReceiveMailForm


class ReceiveMailingDeleteView(LoginRequiredMixin, DeleteView):
    model = ReceiveMail
    template_name = "mailing/receivemail_delete.html"
    success_url = reverse_lazy("mailing:receivemail_list")


# CRUD для сообщений
class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = 'mailing/message_list.html'
    context_object_name = 'письмо'

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)


class MessageDetailView(LoginRequiredMixin, DetailView):
    model = Message
    form_class = MessageForm
    template_name = 'mailing/message_detail.html'

    def get_object(self, queryset=None):
        self.object = super().get_object(queryset)
        if not self.request.user.is_superuser:
            raise PermissionDenied
        return self.object


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailing/message_form.html'
    success_url = reverse_lazy("mailing:message_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user  # автоматически устанавливаем владельца
        return super().form_valid(form)

    def form_valid(self, form):
        recipient = form.save()
        recipient.owner = self.request.user
        recipient.save()
        return super().form_valid(form)


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailing/message_form.html'
    success_url = reverse_lazy("mailing:message_list")

    def get_object(self, queryset=None):
        self.object = super().get_object(queryset)
        if not self.request.user.is_superuser:
            raise PermissionDenied
        return self.object


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    model = Message
    template_name = 'mailing/message_delete.html'
    success_url = reverse_lazy("mailing:message_list")

    def get_object(self, queryset=None):
        self.object = super().get_object(queryset)
        if not self.request.user.is_superuser:
            raise PermissionDenied
        return self.object


class MailingAttemptCreateView(LoginRequiredMixin, CreateView):
    model = AttemptMailing

    def form_valid(self, form):
        recipient = form.save()
        recipient.owner = self.request.user
        recipient.save()
        return super().form_valid(form)


class MailingAttemptListView(LoginRequiredMixin, ListView):
    model = AttemptMailing
    template_name = "mailing/attemptmailing_list.html"

    def get_queryset(self, *args, **kwargs):
        if self.request.user:
            return super().get_queryset()
        elif self.request.user.groups.filter(name="Пользователи").exists():
            return super().get_queryset().filter(owner=self.request.user)
        raise PermissionDenied

class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/mailing_form.html'
    success_url = reverse_lazy("mailing:mailing_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['client'].queryset = ReceiveMail.objects.filter(owner=self.request.user)
        form.fields['message'].queryset = Message.objects.filter(owner=self.request.user)
        return form

