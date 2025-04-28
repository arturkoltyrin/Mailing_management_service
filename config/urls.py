from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from config import settings
from mailing import views
from mailing.views import homeView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", homeView.as_view(), name="home"),
    path("", include("mailing.urls", namespace="mailing")),
    path("users/", include("users.urls", namespace="users")),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)