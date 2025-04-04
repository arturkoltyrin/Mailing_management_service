from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import HttpResponseForbidden
from django.core.mail import send_mail
from datetime import datetime
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import DetailView, ListView, TemplateView, View
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from mailing.forms import MessageForm, RecipientForm, MailingForm
from mailing.models import Mailing, MailingAttempt, Message, Recipient
from mailing.services import get_index_page_cache_data


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = "mailing/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context.update(get_index_page_cache_data(user))
        return context


class RecipientListView(LoginRequiredMixin, ListView):
    model = Recipient

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="Менеджер").exists():
            return Recipient.objects.all()
        return Recipient.objects.filter(owner=user.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        is_manager = self.request.user.groups.filter(name="Менеджер").exists()
        context["is_manager"] = is_manager
        return context


class RecipientCreateView(LoginRequiredMixin, CreateView):
    model = Recipient
    form_class = RecipientForm
    success_url = reverse_lazy("mailing:recipient_list")

    def form_valid(self, form):
        recipient = form.save()
        user = self.request.user
        recipient.owner = user
        recipient.save()
        return super().form_valid(form)


class RecipientUpdateView(LoginRequiredMixin, UpdateView):
    model = Recipient
    form_class = RecipientForm
    success_url = reverse_lazy("mailing:recipient_list")

    def dispatch(self, request, *args, **kwargs):
        obj = super().get_object()
        if obj.owner == self.request.user:
            return super().dispatch(request, *args, **kwargs)
        return HttpResponseForbidden("Вы не можете изменять получателя рассылки.")


class RecipientDeleteView(LoginRequiredMixin, DeleteView):
    model = Recipient
    success_url = reverse_lazy("mailing:recipient_list")

    def dispatch(self, request, *args, **kwargs):
        obj = super().get_object()
        if obj.owner == self.request.user:
            return super().dispatch(request, *args, **kwargs)
        return HttpResponseForbidden("Вы не можете просматривать или удалять получателя рассылки.")


class MessageListView(LoginRequiredMixin, ListView):
    model = Message

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="Менеджер").exists():
            return Message.objects.all()
        return Message.objects.filter(owner=user.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        is_manager = self.request.user.groups.filter(name="Менеджер").exists()
        context["is_manager"] = is_manager
        return context


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    success_url = reverse_lazy("mailing:message_list")

    def form_valid(self, form):
        message = form.save()
        user = self.request.user
        message.owner = user
        message.save()
        return super().form_valid(form)


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    model = Message
    form_class = MessageForm
    success_url = reverse_lazy("mailing:message_list")

    def dispatch(self, request, *args, **kwargs):
        obj = super().get_object()
        if obj.owner == self.request.user:
            return super().dispatch(request, *args, **kwargs)
        return HttpResponseForbidden("Вы не можете просматривать или изменять это сообщение.")


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    model = Message
    success_url = reverse_lazy("mailing:message_list")

    def dispatch(self, request, *args, **kwargs):
        obj = super().get_object()
        if obj.owner == self.request.user:
            return super().dispatch(request, *args, **kwargs)
        return HttpResponseForbidden("Вы не можете просматривать или удалять это сообщение.")


class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="Менеджер").exists():
            return Mailing.objects.prefetch_related("recipients")
        return Mailing.objects.filter(owner=user.id).prefetch_related("recipients")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        is_manager = self.request.user.groups.filter(name="Менеджер").exists()
        context["is_manager"] = is_manager
        return context


class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    success_url = reverse_lazy("mailing:mailing_list")

    def form_valid(self, form):
        mailing = form.save()
        user = self.request.user
        mailing.owner = user
        mailing.save()
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class MailingUpdateView(LoginRequiredMixin, UpdateView):
    model = Mailing
    success_url = reverse_lazy("mailing:mailing_list")
    fields = '__all__'

    def dispatch(self, request, *args, **kwargs):
        obj = super().get_object()
        if obj.owner == self.request.user:
            return super().dispatch(request, *args, **kwargs)
        return HttpResponseForbidden("Вы не можете просматривать или изменять эту рассылку.")


class MailingDeleteView(LoginRequiredMixin, DeleteView):
    model = Mailing
    success_url = reverse_lazy("mailing:mailing_list")

    def dispatch(self, request, *args, **kwargs):
        obj = super().get_object()
        if obj.owner == self.request.user:
            return super().dispatch(request, *args, **kwargs)
        return HttpResponseForbidden("Вы не можете просматривать или удалять эту рассылку.")


class MailingDetailView(LoginRequiredMixin, DetailView):
    model = Mailing

    def get_queryset(self):
        queryset = Mailing.objects.prefetch_related("recipients")
        return queryset

    def dispatch(self, request, *args, **kwargs):
        obj = super().get_object()
        if obj.owner == self.request.user:
            return super().dispatch(request, *args, **kwargs)
        return HttpResponseForbidden("Вы не можете просматривать эту рассылку.")

    def post(self, request, *args, **kwargs):

        self.object = self.get_object()
        subject = self.object.message
        message = self.object.message.message
        # self.object.status = "running"
        # self.object.save()
        from_email = "drovosekov1910@mail.ru"
        recipient_list = [recipient.email for recipient in self.object.recipients.all()]

        for recipient in recipient_list:
            try:
                send_mail(subject, message, from_email, [recipient])
                response = f"{recipient}: Успешно отправлено"
                MailingAttempt.objects.create(attempted_at=timezone.now(), status="success",
                                              mail_server_response=response,
                                              mailing=self.object)
            except Exception as e:
                response = f"{recipient}: Ошибка: {e}"
                MailingAttempt.objects.create(attempted_at=datetime.now(), status="failure",
                                              mail_server_response=response,
                                              mailing=self.object)
        return redirect("mailing:mailing_list")


class MailingAttemptListView(LoginRequiredMixin, ListView):
    model = MailingAttempt

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="Менеджер").exists():
            return MailingAttempt.objects.all()
        return MailingAttempt.objects.filter(mailing__owner=user.id)


class MailingStopView(LoginRequiredMixin, View):
    def post(self, request, pk):
        mailing = get_object_or_404(Mailing, pk=pk)
        user = request.user
        is_manager = user.groups.filter(name="Менеджер").exists()
        if is_manager or user == mailing.owner:
            mailing.status = "completed"
            mailing.save()

            return redirect("mailing:mailing_list")
        return HttpResponseForbidden("У вас нет прав для отключения рассылки")