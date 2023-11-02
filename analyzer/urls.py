from django.urls import path
from django.views.generic import TemplateView

from . import views

app_name = "analyzer"

urlpatterns = [
    path("", TemplateView.as_view(template_name="analyzer/index.html"),
         name="index"),
    path("webhook/", views.webhook, name="webhook"),
]
